import requests
import boto3
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to fetch countries data and upload to S3
    Returns True on success, raises exception on failure
    """
    # ✅ Correct region
    s3 = boto3.client('s3', region_name='eu-north-1')
    S3_BUCKET = 'aws-learning-source-bucket'

    # Include fields parameter to get clean JSON
    api_url = "https://restcountries.com/v3.1/all?fields=name,region,population,area,capital"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    try:
        logger.info("🔄 Fetching countries data...")
        response = requests.get(api_url, headers=headers, timeout=30)
        logger.info(f"Status Code: {response.status_code}")
        response.raise_for_status()

        json_data = response.json()
        file_name = "countries_data.json"

        logger.info(f"📦 Uploading {file_name} to S3...")
        
        # ✅ Use json.dumps for proper JSON
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=f"raw/{file_name}",
            Body=json.dumps(json_data, indent=2),
            ContentType="application/json"
        )

        logger.info(f"✅ Uploaded {file_name} to s3://{S3_BUCKET}/raw/{file_name}")
        logger.info(f"📊 Total countries: {len(json_data)}")
        
        return True

    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP Error: {e}")
        logger.error(f"Response content: {response.text[:500]}")
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()