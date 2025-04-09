import boto3
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the AWS credentials from the environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

# Set up S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

# File info
local_file_path = 'C:/Users/sahan/OneDrive/Desktop/Project/iot.csv' #path to  iot.csv file
bucket_name = 'smart-home-automation-data' # don't change
s3_key = 'uploads/iot.csv' # don't change

# Upload
try:
    s3.upload_file(local_file_path, bucket_name, s3_key)
    print("✅ Upload successful.")
except Exception as e:
    print(f"❌ Upload failed: {e}")
