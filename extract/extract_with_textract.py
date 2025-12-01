from io import StringIO
from dateutil import parser
from datetime import datetime
from trp import Document
import pandas as pd
import boto3
import time
import os
import re
import numpy as np


s3_client = boto3.client('s3', region_name = 'us-east-1')
textract_client = boto3.client('textract', region_name = 'us-east-1')

def extract_table_with_textract(file_path, bucket_name = 'pdf-statements-expensee',max_retries = 60, poll_interval=5):
    """
    Extract tables from PDF using Amazon Textract async API.
    
    Args:
        file_path: Local path to PDF file
        bucket_name: S3 bucket for uploading PDF
        max_retries: Max number of polling attempts (120 * 5 seconds = 10 minutes)
        poll_interval: Seconds to wait between polls
    
    Returns:
        pandas.DataFrame: Extracted table as DataFrame, or None if failed
    """
    print(f"[Textract] Uploading {file_path} to S3...")
    
    object_name = os.path.basename(file_path)
    s3_client.upload_file(file_path, bucket_name, object_name)
    print(f"[Textract] ✓ Uploaded to s3://{bucket_name}/{object_name}")

    # STEP 2: Start async Textract job
    print(f"[Textract] Starting async Textract job...")
    response = textract_client.start_document_analysis(
        DocumentLocation={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': object_name
            }
        },
        FeatureTypes=['TABLES'],
        NotificationChannel={
            'SNSTopicArn': 'arn:aws:sns:us-east-1:390844745124:textract_job_complete_sns.fifo',
            'RoleArn': 'arn:aws:iam::390844745124:role/lambda_textract_role'
        }
    )

    job_id = response['JobId']

    # STEP 3: Poll for job completion
    print(f"[Textract] ✓ Job started: {job_id}")

    print(f"[Textract] Polling for completion (max {max_retries * poll_interval}s)...")
    poll_count = 0

    while poll_count < max_retries:
        response = textract_client.get_document_analysis(JobId=job_id)
        status = response['JobStatus']
        
        if status == 'SUCCEEDED':
            print(f"[Textract] ✓ Job SUCCEEDED")
            break
        elif status == 'FAILED':
            print(f"[Textract] ✗ Job FAILED: {response.get('StatusMessage', 'Unknown error')}")

        elif status == 'PARTIAL_SUCCESS':
            print(f"[Textract] ⚠ Job PARTIAL_SUCCESS - proceeding with partial results")
            break
    
        poll_count += 1
        if poll_count % 10 == 0:  # Print every 10 polls
            print(f"[Textract] Polling... ({poll_count}/{max_retries})")
        time.sleep(poll_interval)

    if poll_count >= max_retries:
        print(f"[Textract] ✗ Polling timeout after {max_retries * poll_interval}s")

    print(f"[Textract] Retrieving full results...")
    
    # STEP 4: Retrieve full result blocks
    all_blocks = []
    next_token = None

    while True:
        if next_token:
            response = textract_client.get_document_analysis(JobId=job_id, NextToken=next_token)
        else:
            response = textract_client.get_document_analysis(JobId=job_id)
        
        all_blocks.extend(response.get('Blocks', []))
        next_token = response.get('NextToken')
        
        if not next_token:
            break
            
    print(f"[Textract] ✓ Retrieved {len(all_blocks)} blocks")

    # STEP 5: Extract tables
    print(f"[Textract] Extracting tables...")
    doc = Document({'Blocks': all_blocks})

    valid_df = []
    for page_idx, page in enumerate(doc.pages):
        for table_idx, table in enumerate(page.tables):
            rows = []
            for row in table.rows:
                cells_text = [cell.text.strip() for cell in row.cells]
                rows.append(cells_text)

            
            if rows:
                # Try to infer header row (usually first row)
                print(f"[Textract] ✓ Extracted Table {table_idx + 1}: {len(rows)} rows × {len(rows[0]) if rows else 0} columns")
                
                patterns = {
                    'date': r'(trans(action)?\s*)?date',           # Matches: "date", "trans date", "transaction date"
                    'description': r'(desc(ription)?|merchant)',   # Matches: "description", "desc", "merchant"
                    'amount': r'(amount|charge|debit)'      # Matches: "amount", "charge", "debit", "credit"
                }
                
                found = {}
                header_row = 0  # Initialize to 0 instead of None (first row is usually the header)
                for idx, row in enumerate(rows):
                    row_text = " ".join(row).lower()
                    if any(re.search(p, row_text) for p in patterns.values()):
                        header_row = idx
                        break

                df = pd.DataFrame(rows[header_row+1:], columns=rows[header_row])
                
                for key, pattern in patterns.items():
                    # Search in columns first
                    for col in df.columns:
                        if re.search(pattern, str(col), re.IGNORECASE):
                            found[key] = col
                            break

                    
                # Check if all required fields were found
                if len(found) != 3:
                    missing = set(patterns.keys()) - set(found.keys())
                    print(f"[Warning] Missing required fields: {missing}. Skipping this table.\n")
                    continue

                print(found)
                #Remove Noise
                if found['description'] == found['amount']:
                    merged_header = found['description']
                    print(f"[!] Merged header detected: {merged_header}")

                    # Rename the merged header temporarily
                    df.rename(columns={merged_header: 'Description_Amount'}, inplace=True)

                    # Split merged column into Description + Amount using regex pattern
                    df[['Description', 'Amount']] = df['Description_Amount'].str.extract(
                        r'(.+?)\s+(\$?\s*[\d,]+(?:\.\d{2})?)'  # text + numeric pattern
                    )
                    
                    # Drop original merged col
                    df.drop(columns=['Description_Amount'], inplace=True)

                    # Now safely overwrite found mapping
                    found['description'] = 'Description'
                    found['amount'] = 'Amount'
                    
                df.rename(columns={
                found['date']: 'Date',
                found['description']: 'Description',
                found['amount']: 'Amount'
                }, inplace=True)


                # Clean and parse dates
                def parse_date(value):
                    if pd.isna(value):
                        return pd.NaT
                    try:
                        # default=datetime.now() fills in missing parts (like year) with current date
                        dt = parser.parse(str(value), default=datetime.now())
                        return dt.date()
                    except (ValueError, TypeError):
                        return pd.NaT

                # Apply parsing
                df['Date'] = df['Date'].apply(parse_date)

                df.replace(['', '-', 'nan'], np.nan, inplace=True)
                df.dropna(subset=['Date', 'Description', 'Amount'], inplace=True)
                transactions_df = df[['Date', 'Description', 'Amount']]

                valid_df.append(transactions_df)


    df1 = pd.concat(valid_df, ignore_index=True)

    return df1

if __name__ == '__main__':
    file_path = './test_pdf_statements/Apple Card Statement - March 2025.pdf'
    df = extract_table_with_textract(file_path)
    print(df)

