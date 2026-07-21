import os
import boto3
from dotenv import load_dotenv

load_dotenv()



def upload_to_s3(local_file_path, bucket_name, s3_key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    try:
        s3.upload_file(local_file_path, bucket_name, s3_key)
        print(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Upload failed: {e}")


if __name__ == "__main__":
    bucket = os.getenv('AWS_BUCKET_NAME')
    upload_to_s3(
        local_file_path=r'C:\Users\dimit\Documents\loan-project\loans_clean.csv',
        bucket_name=bucket,
        s3_key='lendingclub/cleaned_data.csv'
    )