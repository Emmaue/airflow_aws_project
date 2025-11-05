import boto3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    s3 = boto3.client('s3', region_name='us-east-1')
    
    SOURCE_BUCKET = 'aws-learning-source-bucket'
    DEST_BUCKET = 'aws-learning-destination-bucket'
    
    source_key = 'raw/candidates/cand1.csv'
    dest_key = 'cleaned/cand1.csv'
    
    try:
        logger.info(f"📋 Copying file between S3 buckets...")
        logger.info(f"   From: s3://{SOURCE_BUCKET}/{source_key}")
        logger.info(f"   To:   s3://{DEST_BUCKET}/{dest_key}")
        
        # Perform copy
        copy_source = {'Bucket': SOURCE_BUCKET, 'Key': source_key}
        s3.copy_object(
            CopySource=copy_source,
            Bucket=DEST_BUCKET,
            Key=dest_key
        )
        
        # Verify in destination bucket
        response = s3.head_object(Bucket=DEST_BUCKET, Key=dest_key)
        version_id = response.get('VersionId', 'No version info')
        file_size = response.get('ContentLength', 0)
        
        logger.info(f"✅ File copied successfully!")
        logger.info(f"🆕 Version ID: {version_id}")
        logger.info(f"📦 File size: {file_size / 1024:.2f} KB")
        
        return True
        
    except s3.exceptions.NoSuchKey:
        logger.error(f"❌ Source file not found: s3://{SOURCE_BUCKET}/{source_key}")
        logger.error(f"💡 Upload the file to S3 first using AWS Console or AWS CLI")
        raise
    except Exception as e:
        logger.error(f"❌ S3 copy failed: {e}")
        raise

if __name__ == "__main__":
    main()
