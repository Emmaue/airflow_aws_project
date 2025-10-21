import requests
import boto3
from io import BytesIO

s3 = boto3.client('s3', region_name='us-east-1')
S3_BUCKET = 'aws-learning-source-bucket'

# Include fields parameter to get clean JSON
api_url = "https://restcountries.com/v3.1/all?fields=name,region,population,area,capital"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

try:
    response = requests.get(api_url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    response.raise_for_status()

    json_data = response.json()
    file_name = "countries_data.json"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"raw/{file_name}",
        Body=BytesIO(bytes(str(json_data), "utf-8")),
        ContentType="application/json"
    )

    print(f"✅ Uploaded {file_name} - {len(json_data)} countries")

except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e}")
    print(f"Response content: {response.text[:500]}")
except Exception as e:
    print(f"❌ Error: {e}")
