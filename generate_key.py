import secrets

def generate_secret_key():
    # Generate a 32-byte secret key (can be longer for more security)
    key = secrets.token_hex(32)  # 32 bytes = 64 hex characters
    print(f"Generated Secret Key: {key}")

    # Save the key to a .env file or print it so you can use it
    with open('.env', 'a') as env_file:
        env_file.write(f"SECRET_KEY={key}\n")

if __name__ == "__main__":
    generate_secret_key()