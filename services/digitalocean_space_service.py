# services/digitalocean_space_service.py
import os
import boto3
from botocore.exceptions import NoCredentialsError
from werkzeug.utils import secure_filename

# Load DigitalOcean Spaces credentials from environment variables
DO_SPACE_ACCESS_KEY = os.getenv("DO_SPACE_ACCESS_KEY")
DO_SPACE_SECRET_KEY = os.getenv("DO_SPACE_SECRET_KEY")
DO_SPACE_REGION = "nyc3"  # Adjust if you created it in a different region
DO_SPACE_NAME = "law-firm-documenting-storage"  # Your Space name
DO_SPACE_ENDPOINT = f"https://{DO_SPACE_NAME}.{DO_SPACE_REGION}.digitaloceanspaces.com"

# Initialize the boto3 client
s3_client = boto3.client(
    's3',
    region_name=DO_SPACE_REGION,
    endpoint_url=DO_SPACE_ENDPOINT,
    aws_access_key_id=DO_SPACE_ACCESS_KEY,
    aws_secret_access_key=DO_SPACE_SECRET_KEY
)

def upload_file_to_space(file, folder="documents"):
    """
    Uploads a file to DigitalOcean Spaces and returns the file's URL.
    """
    try:
        # Secure the file name and create a path in the Space
        file_name = secure_filename(file.filename)
        file_path = f"{folder}/{file_name}"

        # Upload the file to DigitalOcean Spaces
        s3_client.upload_fileobj(
            file,
            DO_SPACE_NAME,
            file_path,
            ExtraArgs={"ACL": "public-read"}  # Make the file publicly accessible
        )

        # Return the file URL
        file_url = f"{DO_SPACE_ENDPOINT}/{file_path}"
        return file_url

    except NoCredentialsError:
        print("Credentials not available")
        return None

def delete_file_from_space(file_path):
    """
    Deletes a file from DigitalOcean Spaces.
    """
    s3_client.delete_object(Bucket=DO_SPACE_NAME, Key=file_path)
