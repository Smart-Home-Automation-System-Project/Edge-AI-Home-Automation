from botocore.exceptions import NoCredentialsError
import boto3
import os
import re
import tarfile
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# AWS credentials from the .env file
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

# S3 bucket details
bucket_name = 'smart-home-automation-data'
s3_folder = 'models/'

# Windows path
local_model_tar_path = r'C:\Users\sahan\OneDrive\Desktop\Project\model.tar.gz' # path\to\model.tar.gz
extracted_model_path = r'C:\Users\sahan\OneDrive\Desktop\Project\model.h5' # path\to\model.h5

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

def get_most_recent_model():
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder)
    model_keys = [obj['Key'] for obj in objects.get('Contents', []) if re.match(r'^models/iot-lstm-job-\d+/output/model\.tar\.gz$', obj['Key'])]
    model_keys.sort(key=lambda x: int(re.search(r'(\d+)', x).group(1)), reverse=True)
    return model_keys[0] if model_keys else None

try:
    model_key = get_most_recent_model()
    if model_key:
        s3.download_file(bucket_name, model_key, local_model_tar_path)
        print(f"Downloaded model to {local_model_tar_path}")

        if tarfile.is_tarfile(local_model_tar_path):
            with tarfile.open(local_model_tar_path, 'r:gz') as tar:
                tar.extractall(path=os.path.dirname(local_model_tar_path))
                print(f"Model extracted to {extracted_model_path}")
        else:
            print("Downloaded file is not a valid tar.gz")
    else:
        print("No model found.")
except Exception as e:
    print(f"Error downloading or extracting model: {e}")
