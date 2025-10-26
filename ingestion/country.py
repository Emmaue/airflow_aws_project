import requests
import boto3
import json

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
    print("🔄 Fetching countries data...")
    response = requests.get(api_url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    response.raise_for_status()

    json_data = response.json()
    file_name = "countries_data.json"

    print(f"📦 Uploading {file_name} to S3...")
    
    # ✅ Use json.dumps for proper JSON
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"raw/{file_name}",
        Body=json.dumps(json_data, indent=2),
        ContentType="application/json"
    )

    print(f"✅ Uploaded {file_name} to s3://{S3_BUCKET}/raw/{file_name}")
    print(f"📊 Total countries: {len(json_data)}")
    print(f"\n🎯 Lambda should now automatically process this file!")
    print(f"📝 Check logs: aws logs tail /aws/lambda/DataCleaningFunction --follow --region eu-north-1")

except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e}")
    print(f"Response content: {response.text[:500]}")
except Exception as e:
    print(f"❌ Error: {e}")