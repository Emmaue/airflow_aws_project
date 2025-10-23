import boto3
import json
import os
import csv
from io import StringIO

s3 = boto3.client('s3')

def lambda_handler(event, context):
    source_bucket = os.environ['SOURCE_BUCKET']
    dest_bucket = os.environ['DESTINATION_BUCKET']  # ✅ fixed here

    record = event['Records'][0]
    source_key = record['s3']['object']['key']
    dest_key = f"cleaned/{os.path.splitext(os.path.basename(source_key))[0]}.csv"

    print(f"Cleaning and converting {source_key} from {source_bucket} to CSV...")

    obj = s3.get_object(Bucket=source_bucket, Key=source_key)
    raw_data = json.loads(obj['Body'].read().decode('utf-8'))

    cleaned_data = []
    for country in raw_data:
        try:
            name = country.get('name', {}).get('common', '').strip().title()
            population = country.get('population', 0)
            region = country.get('region', 'Unknown').strip().title()

            if name and population > 0:
                cleaned_data.append({
                    'Country': name,
                    'Population': population,
                    'Region': region
                })
        except Exception as e:
            print(f"Skipping record due to error: {e}")

    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=['Country', 'Population', 'Region'])
    writer.writeheader()
    writer.writerows(cleaned_data)

    s3.put_object(
        Bucket=dest_bucket,
        Key=dest_key,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )

    print(f"✅ Cleaned CSV uploaded to {dest_bucket}/{dest_key}")
    return {"statusCode": 200, "body": f"File cleaned and saved as {dest_key}"}
