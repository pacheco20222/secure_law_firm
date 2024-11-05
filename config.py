# config.py
import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sshtunnel import SSHTunnelForwarder, HandlerSSHTunnelForwarderError
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# SSH and MySQL Configuration
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT"))
SSH_USER = os.getenv("SSH_USER")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = 3306  # MySQL default port
LOCAL_PORT = 3310  # Changed local port to avoid conflicts

# MongoDB Configuration
MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
MONGO_LOCAL_PORT = int(os.getenv("MONGO_LOCAL_PORT", 27019))

# Initialize tunnels as global variables
mysql_tunnel = None
mongo_tunnel = None

# Start MySQL SSH tunnel with error handling
def start_mysql_tunnel(retries=3):
    global mysql_tunnel
    for attempt in range(retries):
        if mysql_tunnel is None or not mysql_tunnel.is_active:
            try:
                print(f"Attempting to start MySQL SSH tunnel on attempt {attempt + 1}...")
                mysql_tunnel = SSHTunnelForwarder(
                    (SSH_HOST, SSH_PORT),
                    ssh_username=SSH_USER,
                    ssh_pkey=SSH_KEY_PATH,
                    remote_bind_address=('127.0.0.1', MYSQL_PORT),
                    local_bind_address=('127.0.0.1', LOCAL_PORT),
                    set_keepalive=30
                )
                mysql_tunnel.start()
                print(f"MySQL SSH tunnel started successfully and is active: {mysql_tunnel.is_active}")
                break
            except HandlerSSHTunnelForwarderError as e:
                print(f"Failed to start MySQL SSH tunnel on attempt {attempt + 1}: {e}")
                time.sleep(2)
        else:
            print("MySQL SSH tunnel is already active.")
            break
    else:
        raise ConnectionError("Could not establish MySQL SSH tunnel after retries")

# Start MongoDB SSH tunnel with error handling
def start_mongo_tunnel(retries=3):
    global mongo_tunnel
    for attempt in range(retries):
        if mongo_tunnel is None or not mongo_tunnel.is_active:
            try:
                print(f"Attempting to start MongoDB SSH tunnel on attempt {attempt + 1}...")
                mongo_tunnel = SSHTunnelForwarder(
                    (SSH_HOST, SSH_PORT),
                    ssh_username=SSH_USER,
                    ssh_pkey=SSH_KEY_PATH,
                    remote_bind_address=(MONGO_HOST, 27017),  # Default MongoDB port on remote server
                    local_bind_address=('127.0.0.1', MONGO_LOCAL_PORT),
                    set_keepalive=30
                )
                mongo_tunnel.start()
                print(f"MongoDB SSH tunnel started successfully and is active: {mongo_tunnel.is_active}")
                break
            except HandlerSSHTunnelForwarderError as e:
                print(f"Failed to start MongoDB SSH tunnel on attempt {attempt + 1}: {e}")
                time.sleep(2)
        else:
            print("MongoDB SSH tunnel is already active.")
            break
    else:
        raise ConnectionError("Could not establish MongoDB SSH tunnel after retries")

# Initialize tunnels on module load
start_mysql_tunnel()
start_mongo_tunnel()

# SQLAlchemy setup with the MySQL SSH tunnel
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@127.0.0.1:{LOCAL_PORT}/{MYSQL_DB}"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB Client Setup
mongo_client = MongoClient(f"mongodb://127.0.0.1:{MONGO_LOCAL_PORT}")
mongo_db = mongo_client["legal_documents"]

# Cleanup function for when the app closes
def close_tunnels():
    global mysql_tunnel, mongo_tunnel
    if mysql_tunnel and mysql_tunnel.is_active:
        mysql_tunnel.stop()
        print("MySQL SSH tunnel closed.")
    if mongo_tunnel and mongo_tunnel.is_active:
        mongo_tunnel.stop()
        print("MongoDB SSH tunnel closed.")
