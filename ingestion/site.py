import requests
import boto3
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to fetch posts data and upload to S3
    Returns True on success, raises exception on failure
    """
    s3 = boto3.client('s3', region_name='us-east-1')
    S3_BUCKET = 'aws-learning-source-bucket'

    # JSONPlaceholder - guaranteed to work
    api_url = "https://jsonplaceholder.typicode.com/posts"

    try:
        logger.info("🔄 Fetching posts data...")
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"posts_data_{timestamp}.json"

        logger.info(f"📦 Uploading {file_name} to S3...")
        
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=f"raw/{file_name}",
            Body=response.content,
            ContentType="application/json"
        )

        logger.info(f"✅ Uploaded {file_name} to s3://{S3_BUCKET}/raw/{file_name}")
        logger.info(f"📊 Records: {len(response.json())}")
        logger.info(f"📦 File size: {len(response.content) / 1024:.2f} KB")
        
        return True

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()