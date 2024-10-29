# database_setup.py
from config import Base, engine, close_tunnel

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
    close_tunnel()  # Make sure to close the tunnel after running the script
