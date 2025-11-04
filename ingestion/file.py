import boto3
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to upload file to S3
    Returns True on success, raises exception on failure
    """
    # Initialize S3 client
    s3 = boto3.client('s3', region_name='us-east-1')

    # Bucket and file details
    S3_BUCKET = 'aws-learning-source-bucket'
    
    # ⚠️ UPDATED: Use Linux path on EC2 instance
    # You need to either:
    # 1. Upload the file to EC2 first, OR
    # 2. Store it in your project directory
    local_file_path = "/home/ubuntu/airflow_aws_project/data/cand1.csv"
    s3_key = "raw/candidates/cand1.csv"

    try:
        # Check if file exists
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File not found: {local_file_path}")
        
        logger.info(f"📤 Uploading {local_file_path} to S3...")
        
        # Upload file
        s3.upload_file(local_file_path, S3_BUCKET, s3_key)

        # Get object version info
        response = s3.head_object(Bucket=S3_BUCKET, Key=s3_key)
        version_id = response.get('VersionId', 'No version info (check versioning)')

        logger.info(f"✅ Uploaded {local_file_path} to s3://{S3_BUCKET}/{s3_key}")
        logger.info(f"🆕 Version ID: {version_id}")
        
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        logger.error(f"💡 Make sure to upload cand1.csv to your EC2 instance first!")
        raise
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise

if __name__ == "__main__":
    main()