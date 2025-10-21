import requests
import boto3
from datetime import datetime

s3 = boto3.client('s3', region_name='us-east-1')
S3_BUCKET = 'aws-learning-source-bucket'

# JSONPlaceholder - guaranteed to work
api_url = "https://jsonplaceholder.typicode.com/posts"

response = requests.get(api_url, timeout=30)
response.raise_for_status()

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
file_name = f"posts_data_{timestamp}.json"

s3.put_object(
    Bucket=S3_BUCKET,
    Key=f"raw/{file_name}",
    Body=response.content,
    ContentType="application/json"
)

print(f"✅ Uploaded {file_name} to s3://{S3_BUCKET}/raw/{file_name}")
print(f"📊 Records: {len(response.json())}")
print(f"📦 File size: {len(response.content) / 1024:.2f} KB")