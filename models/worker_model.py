import random
import pyotp
from hashlib import sha256
from config import mysql_connection, ssh_tunnel  # Importing the functions from config for SSH and MySQL connection

class WorkerModel:
    def __init__(self):
        """
        Start an SSH tunnel and establish a MySQL connection.
        """
        self.tunnel = ssh_tunnel()  # Start the SSH tunnel
        self.tunnel.start()
        self.connection = mysql_connection(self.tunnel)  # Pass the tunnel to the MySQL connection
        self.cursor = self.connection.cursor()
    
    def close(self):
        """
        Ensure the tunnel and connection are closed when no longer needed.
        """
        self.cursor.close()
        self.connection.close()
        self.tunnel.stop()
    
    @staticmethod
    def hashed_password(password):
        """
        Hash the password using SHA-256.
        """
        return sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_company_id():
        """
        Generate a unique employee ID.
        """
        return f"LR-{random.randint(10000, 99999)}"
    
    @staticmethod
    def generate_2fa_secret():
        """
        Generate a random 2FA secret.
        """
        return pyotp.random_base32()
    
    def create_worker(self, data):
        """
        Insert a new worker into the database.
        """
        try:
            hashed_password = self.hashed_password(data['password'])
            two_fa_secret = self.generate_2fa_secret()
            company_id = self.generate_company_id()
            
            # SQL query to insert a new worker
            insert_query = """
            INSERT INTO workers (name, second_name, last_name, second_last_name, email, phone, role, company_id, hashed_password, 2fa_secret, 2fa_enabled)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            
            self.cursor.execute(insert_query, (
                data['name'], data.get('second_name'), data['last_name'], data.get('second_last_name'), 
                data['email'], data['phone'], data['role'], company_id, hashed_password, two_fa_secret, True
            ))
            self.connection.commit()
            print("Worker created successfully in the database")
            return True
        except Exception as error:
            print(f"Error creating worker in the database: {error}")
            return False
        finally:
            self.close()  # Ensure resources are closed
