# worker_model.py
import random
import pyotp
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from config import Base, SessionLocal
from services.auth_service import hash_password

class Worker(Base):
    __tablename__ = 'workers'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    second_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    second_last_name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(25), unique=True, nullable=False)
    curp = Column(String(20), unique=True, nullable=False)
    role = Column(String(50), nullable=False)
    company_id = Column(String(20), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    two_fa_secret = Column(String(100), nullable=True)
    two_fa_enabled = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    @staticmethod
    def generate_company_id(session):
        """
        Generate a unique employee ID in the format LR-XXX.
        """
        count = session.query(Worker).count() + 1
        return f"LR-{count:03d}"

    @staticmethod
    def generate_2fa_secret():
        """
        Generate a random 2FA secret.
        """
        return pyotp.random_base32()

    @classmethod
    def create_worker(cls, session: Session, data):
        """
        Create a new worker and save it to the database.
        """
        try:
            hashed_password = hash_password(data['password'])
            two_fa_secret = cls.generate_2fa_secret()
            company_id = cls.generate_company_id(session)

            # Create the worker instance
            new_worker = cls(
                name=data['name'],
                second_name=data.get('second_name'),
                last_name=data['last_name'],
                second_last_name=data.get('second_last_name'),
                email=data['email'],
                phone=data['phone'],
                role=data['role'],
                company_id=company_id,
                hashed_password=hashed_password,
                two_fa_secret=two_fa_secret,
                two_fa_enabled=True
            )

            # Add and commit the new worker to the session
            session.add(new_worker)
            session.commit()

            # Generate the QR code for 2FA
            qr_code_path = f"static/qrcodes/{data['email']}_2fa_qr.png"
            pyotp.TOTP(two_fa_secret).provisioning_uri(name=data['email'], issuer_name="SecureLawFirm")
            print(f"Worker created successfully with QR code saved at {qr_code_path}")
            return True

        except IntegrityError:
            session.rollback()
            print("Error: Email or phone number already exists.")
            return False
        except Exception as e:
            session.rollback()
            print(f"Error creating worker in the database: {e}")
            return False
