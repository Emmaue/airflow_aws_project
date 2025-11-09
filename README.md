# AWS Serverless & Orchestration Data Pipeline: ETL with Airflow and Lambda

### Project Goal
This project demonstrates how to build a scalable, serverless data pipeline on AWS, integrating multiple heterogeneous data sources, transforming data using AWS Lambda, and orchestrating the entire workflow using Apache Airflow deployed on an EC2 instance.

The pipeline combines orchestration, automation, version control, and event-driven execution to simulate a real-world enterprise data engineering environment.
The goal is to showcase proficiency in:
- Building scalable, cloud-native pipelines.
- Using serverless transformation with AWS Lambda.
- Managing task dependencies using Airflow DAGs.
- Working with multiple data sources and S3 buckets.
  
## Architecture Overview
```
        +------------------------+
        |   REST Countries API   |
        +-----------+------------+
                    |
        +-----------v------------+
        |   Airflow Ingestion    |
        | (PythonOperators)      |
        +-----------+------------+
                    |
        +-----------v------------+
        |  S3 Source Bucket      |
        |  (Raw Data)            |
        +-----------+------------+
                    |
                    | S3 Trigger (ObjectCreated)
        +-----------v------------+
        |     AWS Lambda         |
        |  Transform JSON → CSV  |
        +-----------+------------+
                    |
        +-----------v------------+
        | S3 Destination Bucket  |
        |  (Cleaned Data)        |
        +-----------+------------+
```

## Implementation:
Each ingestion source is handled by a dedicated Python script (country.py, site.py, file.py) managed by Airflow.
PythonOperators in the DAG trigger these scripts in parallel, ensuring efficient execution.
```
Sample DAG dependency:
[task_ingest_country, task_ingest_site, task_ingest_file] >> task_lambda_countries_clean
```

## Tech Stack
| Category           | Tool / Service                                 | Purpose                                             |
| ------------------ | ---------------------------------------------- | --------------------------------------------------- |
| **Cloud Services** | AWS S3                                         | Acts as a data lake — staging raw and cleaned data. |
|                    | AWS Lambda                                     | Performs event-driven transformation (JSON → CSV).  |
|                    | EC2                                            | Hosts Apache Airflow for orchestration.             |
| **Orchestration**  | Apache Airflow                                 | Manages task scheduling and dependencies.           |
| **Programming**    | Python (Pandas, Boto3, Requests)               | Used for ingestion scripts and Lambda functions.    |
| **Data Sources**   | REST Countries API, JSONPlaceholder, Local CSV | Simulates diverse real-world ingestion sources.     |


## Pipeline Steps
This step ingests data from three different sources into an S3 source bucket (aws-learning-source-bucket/raw/).
1. Extraction & Loading (E–L)
Custom Python scripts (executed via Airflow) fetch and upload data from:
- REST Countries API → countries_data.json
```
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
```
- JSONPlaceholder API → site_data.json
```
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
```
- Local CSV File (cand1.csv)
```
import boto3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    s3 = boto3.client('s3', region_name='us-east-1')
    
    SOURCE_BUCKET = 'aws-learning-source-bucket'
    DEST_BUCKET = 'aws-learning-destination-bucket'
    
    source_key = 'raw/cand1.csv'
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

```

All are loaded into the source S3 bucket:
```
aws-learning-source-bucket/raw/
```
| Task             | Source              | Description                                                 |
| ---------------- | ------------------- | ----------------------------------------------------------- |
| `ingest_country` | REST Countries API  | Fetches country data, uploads JSON to S3 (triggers Lambda). |
| `ingest_site`    | JSONPlaceholder API | Fetches posts and uploads JSON to S3.                       |
| `ingest_file`    | Local CSV           | Uploads static local file to S3.                            |


Source S3 bucket empty
<img width="1280" height="484" alt="image" src="https://github.com/user-attachments/assets/c6d406c4-e71a-42cc-bdbc-e8054d877350" />

Destination S3 bucket empty
<img width="1280" height="521" alt="image" src="https://github.com/user-attachments/assets/1c0af993-9630-44be-94a4-2f4ee899c6c3" />

Why These Sources?
- API data simulates a dynamic external source requiring transformation.
- Local CSV represents company-internal structured data uploads.
- Web JSON represents unstructured, third-party data from SaaS systems.

Expected Behavior:
- Airflow triggers each Python ingestion task.
- Each script extracts and uploads its dataset to s3://aws-learning-source-bucket/raw/
- The upload of the countries_data.json file automatically triggers Lambda via S3 event notification. 



## Event-Driven Transformation with AWS Lambda
Goal:
To automatically transform the raw JSON data into a structured CSV format immediately when new data arrives — using serverless computing (AWS Lambda).

### What Happens:

1. Trigger:
Lambda is invoked when the countries_data.json file is uploaded to the S3 source bucket.

2. Execution Steps:
- Reads the S3 event details (bucket name + object key).
- Fetches the uploaded JSON file.
- Uses Pandas to flatten nested JSON fields like capital, languages, and currencies.
- Converts the cleaned dataset into a CSV format.
- Uploads the CSV into the destination S3 bucket (aws-learning-destination-bucket/cleaned/).

3. Validation:
CloudWatch logs confirm the successful transformation and upload.

### Why Use Lambda?
- Serverless & Cost-Efficient: Runs only when triggered.
- Scalable: Handles variable workloads automatically.
- Event-Driven: Reduces manual scheduling overhead.
- Lightweight: Ideal for quick transformations (no infrastructure management).

### Expected Behavior:
- After ingestion completes, Lambda executes automatically.
- The cleaned CSV file (countries_data.csv) appears in the destination S3 bucket.

### IAM Roles & Security
- Lambda Execution Role: Grants read access to the source S3 bucket and write access to the destination bucket.
- Airflow EC2 IAM Role: Allows Airflow tasks to upload to S3 securely without hardcoded credentials.

The Lambda function in VScode:
```
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
```

Lambda function in AWS:
<img width="1280" height="512" alt="image" src="https://github.com/user-attachments/assets/76afd888-d983-468c-be47-5b19a2b6873b" />

## Airflow Orchestration on EC2
### Goal:
To orchestrate ingestion workflows, manage dependencies, and automate scheduling.

### Setup:
- Deployed Airflow on AWS EC2 (Ubuntu instance).
- Installed and configured Airflow manually with:
```
sudo apt update
sudo apt install -y python3-pip
pip install apache-airflow
airflow db init
airflow webserver -p 8080
airflow scheduler
```
- Used LocalExecutor instead of SequentialExecutor for parallel task execution — allowing multiple ingestion jobs to run concurrently on a single machine.

### IAM & Networking Considerations
- EC2 IAM role provides S3 access permissions to ingestion scripts.
- Security group configured to allow inbound ports 22 (SSH) and 8080 (Airflow Web UI).

### Expected Behavior:
- DAG (aws_ingestion_pipeline) runs daily (@daily schedule).
- Ingestion tasks execute concurrently.
- Final validation task ensures the Lambda trigger succeeded.

  Airflow dag:
```
  import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# --- Add project folder to Python path ---
sys.path.append('/home/ubuntu/airflow_aws_project')

# --- Import your functions from ingestion scripts ---
from ingestion.country import main as ingest_country
from ingestion.file import main as ingest_file
from ingestion.site import main as ingest_site

# --- Import your lambda trigger ---
from lambda_functions.countries import main as lambda_countries_clean

# --- Default arguments ---
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

# --- Define the DAG ---
with DAG(
    dag_id='aws_ingestion_pipeline',
    default_args=default_args,
    description='ETL pipeline: Ingest → Clean → Move',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    task_ingest_country = PythonOperator(
        task_id='ingest_country',
        python_callable=ingest_country,
    )

    task_ingest_file = PythonOperator(
        task_id='ingest_file',
        python_callable=ingest_file,
    )

    task_ingest_site = PythonOperator(
        task_id='ingest_site',
        python_callable=ingest_site,
    )

    task_lambda_countries_clean = PythonOperator(
        task_id='lambda_countries_clean',
        python_callable=lambda_countries_clean,
    )

    # Set task order: Ingest files first, then trigger Lambda cleaning
    [task_ingest_country, task_ingest_file, task_ingest_site] >> task_lambda_countries_clean
```

#### Airflow DAG structure
<img width="1280" height="544" alt="image" src="https://github.com/user-attachments/assets/242c1307-f777-4089-bdd4-07a6f7780557" />

#### Airflow Dag during run:
<img width="1280" height="442" alt="image" src="https://github.com/user-attachments/assets/f3a1cea4-6a8a-4a0b-8968-9b4d5ca45bcc" />

#### Airflow Task Instances (Success)
<img width="1280" height="533" alt="image" src="https://github.com/user-attachments/assets/8f8c1aad-d83a-4dab-adfd-acf04abc8f8d" />


#### S3 Source bucket with ingested objects
<img width="1280" height="511" alt="image" src="https://github.com/user-attachments/assets/232cfbc4-aa8d-4f2b-9dfc-a2a67fc26f2d" />

#### S3 Destination bucket with ingested files
<img width="1280" height="521" alt="image" src="https://github.com/user-attachments/assets/74955521-f1ac-4e25-9e8a-1f3c71d74bcd" />

#### Cloudwatch logging lambda succesful cleaing and moving file from source to destination bucket
<img width="1280" height="508" alt="image" src="https://github.com/user-attachments/assets/8ea7d67b-250f-4685-8b7d-193fb2493170" />


## Version Control & CI
- The entire project is versioned using Git.
- All scripts (ingestion, lambda_function, dags) are pushed to a private/public GitHub repository.
- Each logical change (Lambda, Airflow DAGs, IAM updates) is tracked via separate commits with descriptive messages.


## Key Takeaway
This project demonstrates how serverless and orchestrated systems can coexist effectively to build a resilient, event-driven data pipeline that’s automated, secure, and version-controlled.

It highlights:
- Hands-on experience with AWS ecosystem (Lambda, S3, EC2, IAM, CloudWatch).
- Strong understanding of orchestration logic via Airflow.
- Application of data engineering best practices in ingestion, transformation, and automation.


## Project by Emmanuel Justice



