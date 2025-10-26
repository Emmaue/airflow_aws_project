import boto3
import json
import os
import csv
import logging
from io import StringIO
from urllib.parse import unquote_plus

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda function to clean countries JSON data and convert to CSV
    """
    try:
        # Get environment variables
        source_bucket = os.environ['SOURCE_BUCKET']
        dest_bucket = os.environ['DESTINATION_BUCKET']

        # Get S3 event details
        record = event['Records'][0]
        source_key = unquote_plus(record['s3']['object']['key'])
        
        # Generate destination key
        dest_key = f"cleaned/{os.path.splitext(os.path.basename(source_key))[0]}.csv"

        logger.info(f"Processing: {source_key} from {source_bucket}")
        logger.info(f"Destination: {dest_key} in {dest_bucket}")

        # Read JSON from S3
        obj = s3.get_object(Bucket=source_bucket, Key=source_key)
        raw_data = json.loads(obj['Body'].read().decode('utf-8'))
        
        logger.info(f"Loaded {len(raw_data)} countries from JSON")

        # Clean and transform data
        cleaned_data = []
        skipped = 0
        
        for country in raw_data:
            try:
                # Extract name (handle nested structure)
                name_obj = country.get('name', {})
                if isinstance(name_obj, dict):
                    name = name_obj.get('common', '').strip().title()
                else:
                    name = str(name_obj).strip().title()
                
                population = country.get('population', 0)
                region = country.get('region', 'Unknown').strip().title()
                
                # Extract area if available
                area = country.get('area', 0)
                
                # Extract capital if available
                capital_list = country.get('capital', [])
                capital = capital_list[0] if capital_list else 'N/A'

                # Only include countries with valid data
                if name and population > 0:
                    cleaned_data.append({
                        'Country': name,
                        'Capital': capital,
                        'Population': population,
                        'Area': area if area else 'N/A',
                        'Region': region
                    })
                else:
                    skipped += 1
                    
            except Exception as e:
                logger.warning(f"Skipping country due to error: {e}")
                skipped += 1

        logger.info(f"Cleaned {len(cleaned_data)} countries (skipped {skipped})")

        # Convert to CSV
        csv_buffer = StringIO()
        fieldnames = ['Country', 'Capital', 'Population', 'Area', 'Region']
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_data)

        # Upload CSV to destination bucket
        s3.put_object(
            Bucket=dest_bucket,
            Key=dest_key,
            Body=csv_buffer.getvalue().encode('utf-8'),
            ContentType='text/csv'
        )

        logger.info(f"✅ Successfully uploaded to s3://{dest_bucket}/{dest_key}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File cleaned and converted to CSV",
                "source": f"s3://{source_bucket}/{source_key}",
                "destination": f"s3://{dest_bucket}/{dest_key}",
                "records_processed": len(cleaned_data),
                "records_skipped": skipped
            })
        }

    except Exception as e:
        logger.error(f"❌ Error processing file: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }