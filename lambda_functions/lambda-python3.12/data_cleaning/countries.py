import boto3
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Trigger or wait for Lambda function to process the countries data.
    
    Since your Lambda is triggered by S3 events, this function will:
    1. Wait for the Lambda to process the file
    2. Check if the cleaned file appears in the destination bucket
    
    Returns True when cleaning is complete
    """
    s3 = boto3.client('s3', region_name='eu-north-1')
    
    SOURCE_BUCKET = 'aws-learning-source-bucket'
    DEST_BUCKET = 'aws-learning-destination-bucket'  # Update with your actual destination bucket
    
    source_key = 'raw/countries_data.json'
    dest_key = 'cleaned/countries_data.csv'
    
    max_wait_time = 300  # 5 minutes
    check_interval = 10  # Check every 10 seconds
    elapsed_time = 0
    
    logger.info(f"⏳ Waiting for Lambda to process {source_key}...")
    logger.info(f"🎯 Expected output: s3://{DEST_BUCKET}/{dest_key}")
    
    try:
        # Wait for the cleaned file to appear
        while elapsed_time < max_wait_time:
            try:
                # Check if cleaned file exists
                s3.head_object(Bucket=DEST_BUCKET, Key=dest_key)
                logger.info(f"✅ Lambda processing complete! File found at s3://{DEST_BUCKET}/{dest_key}")
                return True
                
            except s3.exceptions.NoSuchKey:
                # File doesn't exist yet, keep waiting
                logger.info(f"⏳ Still waiting... ({elapsed_time}s elapsed)")
                time.sleep(check_interval)
                elapsed_time += check_interval
        
        # Timeout reached
        logger.error(f"❌ Timeout: Lambda did not complete processing within {max_wait_time}s")
        raise TimeoutError(f"Lambda processing timed out after {max_wait_time} seconds")
        
    except Exception as e:
        logger.error(f"❌ Error checking Lambda output: {e}")
        raise

if __name__ == "__main__":
    main()