import pymysql
import pymongo
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import os

load_dotenv()

# SSH Tunnel configuration
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT"))
SSH_USER = os.getenv("SSH_USER")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")
SSH_KEY_PASSPHRASE = os.getenv("SSH_KEY_PASSPHRASE")

# MySQL configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DB")
MYSQL_LOCAL_PORT = int(os.getenv("MYSQL_LOCAL_PORT"))  # Using local bind port 3309

# MongoDB configuration
MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
MONGO_LOCAL_PORT = int(os.getenv("MONGO_LOCAL_PORT"))  # Using local bind port 27020


def ssh_tunnel():
    """
    Create the SSH tunnels for MySQL and MongoDB, using the specified local ports to avoid conflicts.
    """
    return SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_pkey=SSH_KEY_PATH,  # Use the private key path
        remote_bind_addresses=[
            ('127.0.0.1', 3306),  # MySQL default port on server
            ('127.0.0.1', 27017)  # MongoDB default port on server
        ],
        local_bind_addresses=[
            ('127.0.0.1', 3309),  # MySQL local bind port
            ('127.0.0.1', 27020)  # MongoDB local bind port
        ],
        set_keepalive=10 # Optional: set keepalive if needed
    )


def mysql_connection(tunnel):
    """
    Establish connection to MySQL via SSH tunnel.
    """
    try:
        print("SSH tunnel for MySQL has started")
        connection = pymysql.connect(
            host='127.0.0.1',
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=3309  # Local port to avoid conflict
        )
        print("MySQL connection established")
        return connection
    except Exception as e:
        print(f"Failed to connect to MySQL: {e}")
        return None


def mongo_connection(tunnel):
    """
    Establish connection to MongoDB via SSH tunnel.
    """
    try:
        print("SSH tunnel for MongoDB has started")
        client = pymongo.MongoClient(
            host='127.0.0.1',
            port=27020  # Local port to avoid conflict
        )
        print("MongoDB connection established")
        return client
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None


if __name__ == "__main__":
    # Start the SSH tunnel
    tunnel = ssh_tunnel()
    tunnel.start()

    # Connect to MySQL
    mysql_conn = mysql_connection(tunnel)

    # Connect to MongoDB
    mongo_conn = mongo_connection(tunnel)

    # When done, stop the tunnel
    tunnel.stop()