import pymysql
import pyotp  # For 2FA generation
import qrcode  # For generating QR code
import os
import dotenv
from sshtunnel import SSHTunnelForwarder
from hashlib import sha256  # For password hashing

dotenv.load_dotenv()

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
MYSQL_PORT = 3309  # Local port for SSH tunnel

# Admin credentials from .env
ADMIN_NAME = os.getenv("ADMIN_NAME")
ADMIN_LAST_NAME = os.getenv("ADMIN_LAST_NAME")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PHONE = os.getenv("ADMIN_PHONE")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# SSH tunnel creation function
def create_ssh_tunnel():
    return SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_pkey=SSH_KEY_PATH,
        ssh_private_key_password=SSH_KEY_PASSPHRASE,
        remote_bind_address=('127.0.0.1', 3306),  # MySQL default port on remote server
        local_bind_address=('127.0.0.1', MYSQL_PORT)  # MySQL will be accessible via this local port
    )

# Function to hash the password using SHA-256
def hash_password(password):
    return sha256(password.encode('utf-8')).hexdigest()

# Function to generate the next company ID in the format "LR-001"
def generate_company_id(cursor):
    cursor.execute("SELECT COUNT(*) FROM workers;")
    result = cursor.fetchone()
    employee_number = result[0] + 1
    return f"LR-{employee_number:03d}"  # Format the ID as LR-001, LR-002, etc.

# Function to create admin user in MySQL with 2FA
def create_admin_user():
    tunnel = None
    try:
        # Start the SSH tunnel
        tunnel = create_ssh_tunnel()
        tunnel.start()

        # Connect to MySQL via the SSH tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Localhost due to SSH tunnel
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT  # The local bind port from the SSH tunnel
        )
        cursor = connection.cursor()

        # Generate 2FA secret for the admin
        admin_2fa_secret = pyotp.random_base32()
        print(f"Admin's 2FA Secret: {admin_2fa_secret}")

        # Generate a QR code for Google Authenticator
        otp_uri = pyotp.totp.TOTP(admin_2fa_secret).provisioning_uri(name=ADMIN_EMAIL, issuer_name="SecureLawFirm")
        qr = qrcode.make(otp_uri)
        qr.save("admin_2fa_qr.png")
        print("QR code generated and saved as 'admin_2fa_qr.png'.")

        # Generate the company ID in the format LR-XXX
        company_id = generate_company_id(cursor)

        # Hash the admin password
        admin_hashed_password = hash_password(ADMIN_PASSWORD)

        # Insert admin user into `workers` table
        query = """
        INSERT INTO workers (
            name, last_name, email, phone, role, company_id, hashed_password, 2fa_secret, 2fa_enabled
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (
            ADMIN_NAME, ADMIN_LAST_NAME, ADMIN_EMAIL, ADMIN_PHONE, 'admin', company_id, 
            admin_hashed_password, admin_2fa_secret, True
        ))
        connection.commit()

        print(f"Admin user created successfully with company ID: {company_id}.")
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
    
    finally:
        if tunnel:
            tunnel.stop()
        if connection:
            connection.close()

if __name__ == "__main__":
    create_admin_user()