# config.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sshtunnel import SSHTunnelForwarder

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
MYSQL_PORT = 3306  # Default MySQL port on the remote server
LOCAL_PORT = 3309  # Local port for accessing the MySQL DB through SSH

# SSH tunnel setup
tunnel = SSHTunnelForwarder(
    (SSH_HOST, SSH_PORT),
    ssh_username=SSH_USER,
    ssh_pkey=SSH_KEY_PATH,
    remote_bind_address=('127.0.0.1', MYSQL_PORT),
    local_bind_address=('127.0.0.1', LOCAL_PORT)
)

# Start the SSH tunnel
tunnel.start()

# SQLAlchemy setup with the SSH tunnel
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@127.0.0.1:{LOCAL_PORT}/{MYSQL_DB}"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Add a cleanup function for when the app closes
def close_tunnel():
    tunnel.stop()
    print("SSH tunnel closed.")
