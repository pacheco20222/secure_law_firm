import random
import pymysql
import pyotp
from hashlib import sha256
# Since we are using ssh tunnels we will bring the config files that handles function to create them
from config import mysql_connection, ssh_tunnel

# We will take a class approach to this

class worker_model:
    def __init__(self):
        """
        We will create the connection, tunnels from the config file, a secure ssh tunnel
        """
        self.tunnel = ssh_tunnel()
        self.tunnel.start()
        self.connection = mysql_connection()
        self.cursor = self.connection.cursor()
    
    def close(self):
        """
        This is just to ensure that once the tunnel and the connection is not needed we close it
        """
        self.connection.close()
        self.cursor.close()
        self.tunnel.stop()
    
    @staticmethod
    def hashed_password(password):
        """
        We use hash password for more security, better practices
        """
        return sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_company_id():
        """
        Function to randomly generate a employee ID
        """
        return f"LR-{random.randint(10000, 99999)}"
    
    @staticmethod
    def generate_2fa_secret():
        """Generate a random 2FA secret."""
        return pyotp.random_base32()
    
    def create_worker(self, data):
        """
        With the connection we established we query a new user when the admin requires it
        Since we are using dictionaries we will get the password with the key
        """
        try:
            hashed_password = self.hashed_password(data['password'])
            # Generate 2FA secret and company ID
            two_fa_secret = self.generate_2fa_secret()
            company_id = self.generate_company_id()
            
            # Insert the worker into the workers table
            insert_query = """
            INSERT INTO workers (name, second_name, last_name, second_last_name, email, role, company_id, hashed_password, 2fa_secret, 2fa_enabled)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            
            self.cursor.execute(insert_query, (
                data['name'], data['second_name'], data['last_name'], data['second_last_name'], 
                data['email'], data['role'], company_id, hashed_password, two_fa_secret, True
            ))
            self.connection.commit()
            return True
        except Exception as error:
            print(f"Error creating worker: {error}")
            return False
        finally:
            self.cursor.close()
            self.connection.close()
            self.tunnel.stop()