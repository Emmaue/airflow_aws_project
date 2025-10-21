import boto3
import os

# Initialize S3 client
s3 = boto3.client('s3', region_name='us-east-1')

# Bucket and file details
S3_BUCKET = 'aws-learning-source-bucket'  # your existing bucket
local_file_path = r"C:\Users\HP\Documents\aws\files\cand1.csv"
s3_key = "raw/candidates/cand1.csv"  # path inside S3 bucket

try:
    # Upload file
    s3.upload_file(local_file_path, S3_BUCKET, s3_key)

    # Get object version info
    response = s3.head_object(Bucket=S3_BUCKET, Key=s3_key)
    version_id = response.get('VersionId', 'No version info (check versioning)')

    print(f"✅ Uploaded {local_file_path} to s3://{S3_BUCKET}/{s3_key}")
    print(f"🆕 Version ID: {version_id}")

except Exception as e:
    print(f"❌ Upload failed: {e}")
