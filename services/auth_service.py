# services/auth_service.py

import pyotp
import qrcode
from hashlib import sha256
import os

# Function to hash passwords
def hash_password(password):
    return sha256(password.encode('utf-8')).hexdigest()

# Function to verify a password
def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# Function to generate 2FA secret
def generate_2fa_secret():
    return pyotp.random_base32()

# Function to generate QR code
def generate_qr_code(email, issuer_name, secret):
    otp_uri = pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)
    qr_code_dir = os.path.join("static", "qrcodes")
    os.makedirs(qr_code_dir, exist_ok=True)
    qr_code_path = os.path.join(qr_code_dir, f"{email}_2fa_qr.png")
    qrcode.make(otp_uri).save(qr_code_path)
    # Inside generate_qr_code function
    print(f"[QR Code Generation] 2FA secret used for QR code: {secret}")
    return qr_code_path

# Function to verify 2FA code with a time-based tolerance window
def verify_2fa_code(secret, code):
    totp = pyotp.TOTP(secret)
    is_valid = totp.verify(code, valid_window=1)  # Checks one code before and after current
    expected_code = totp.now()
    print(f"[2FA] Expected code: {expected_code}")  # Shows current valid code
    print(f"[2FA] Provided code: {code}")           # Shows user-provided code
    print(f"[2FA] Code match status with tolerance: {is_valid}")  # Shows result of verification
    return is_valid