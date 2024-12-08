import sys
import os

# Calculate the path to the project root directory and add it to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from config import SessionLocal, close_tunnels
from models.worker_model import Worker
from services.auth_service import hash_password, generate_2fa_secret, generate_qr_code
from sqlalchemy.exc import IntegrityError


def create_user(name, second_name, last_name, second_last_name, email, phone, curp, role, password):
    session = SessionLocal()
    try:
        hashed_password = hash_password(password)
        two_fa_secret = generate_2fa_secret()

        new_user = Worker(
            name=name,
            second_name=second_name,
            last_name=last_name,
            second_last_name=second_last_name,
            email=email,
            phone=phone,
            curp=curp,
            role=role,
            company_id=f"LR-{session.query(Worker).count() + 1:03d}",
            hashed_password=hashed_password,
            two_fa_secret=two_fa_secret,
            two_fa_enabled=True
        )

        session.add(new_user)
        session.commit()

        # Generate QR code for 2FA
        qr_code_path = generate_qr_code(email, "SecureLawFirm", two_fa_secret)
        print(f"User created successfully! QR code saved at: {qr_code_path}")

    except IntegrityError:
        session.rollback()
        print("Error: Email or phone number already exists.")
    finally:
        session.close()
        close_tunnels()

# Usage example
if __name__ == "__main__":
    create_user(
        name="Jose", second_name="Ricardo", last_name="Pacheco", second_last_name="Chanico",
        email="jrp2022@gmail.com", phone="123456789", curp="pap243425", role="admin", password="securepassword"
    )
