import pymysql
import pymongo
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import os

# Load environment variables from .env
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
MYSQL_LOCAL_PORT = int(os.getenv("MYSQL_LOCAL_PORT"))  # Local bind port for MySQL

# MongoDB configuration
MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
MONGO_LOCAL_PORT = int(os.getenv("MONGO_LOCAL_PORT"))  # Local bind port for MongoDB


def ssh_tunnel():
    """
    Create the SSH tunnel for MySQL and MongoDB.
    """
    return SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_pkey=SSH_KEY_PATH,
        remote_bind_addresses=[
            ('127.0.0.1', 3306),  # MySQL default port on server
            ('127.0.0.1', 27017)  # MongoDB default port on server
        ],
        local_bind_addresses=[
            ('127.0.0.1', 3309),  # MySQL local bind port
            ('127.0.0.1', 27019)  # MongoDB local bind port
        ],
        set_keepalive=10
    )


def mysql_connection(tunnel):
    """
    Establish a connection to MySQL through the SSH tunnel.
    """
    try:
        print("Connecting to MySQL through SSH tunnel...")
        connection = pymysql.connect(
            host='127.0.0.1',
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=tunnel.local_bind_ports[0]  # Use the first port for MySQL
        )
        print("MySQL connection established")
        return connection
    except Exception as e:
        print(f"Failed to connect to MySQL: {e}")
        return None


def mongo_connection(tunnel):
    """
    Establish a connection to MongoDB through the SSH tunnel.
    """
    try:
        print("Connecting to MongoDB through SSH tunnel...")
        client = pymongo.MongoClient(
            host='127.0.0.1',
            port=tunnel.local_bind_ports[1]  # Use the second port for MongoDB
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

    # Test MySQL connection
    mysql_conn = mysql_connection(tunnel)
    if mysql_conn:
        mysql_conn.close()

    # Test MongoDB connection
    mongo_conn = mongo_connection(tunnel)
    if mongo_conn:
        mongo_conn.close()

    # Stop the SSH tunnel
    tunnel.stop()