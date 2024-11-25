"""
Database set up for connecting to the database with ssh keys, to the remote server. 
Refer to the config.py file, localted in the root of the project config.py
Along with proper .env file set up refer to the template_env file in the root of the project.
"""
from config import Base, engine, close_tunnel

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database Initilialize correctly.")

if __name__ == "__main__":
    init_db()
    close_tunnel()  # At the end of the code we close the SSH tunnel
