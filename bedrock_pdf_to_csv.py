import logging
import boto3
import json
from pathlib import Path
import os

from botocore.exceptions import ClientError

def extract_pdf_with_bedrock(file_path):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    client = boto3.client("bedrock-runtime", region_name = "us-east-1")

    model_id  = "amazon.nova-pro-v1:0"

    with open(file_path, "rb") as file:
        document_bytes = file.read()
        
        conversation = [
            {
                "role": "user",
                "content": [ 
                    {"text": """
                                You are a PDF parser. Extract only the 'Purchases', 'Balance Transfers', and 'Other Charges' tables 
                                from the credit card statement. Return only the transaction rows with the header row. 
                                Exclude totals, fees, interest, or summary rows. 
    
                                Output format requirements:
                                - Return ONLY valid CSV text.
                                - Do not include code blocks, markdown fences, or any explanations.
                                - Do not prepend or append labels such as ```csv or "Here is the file".
                                - The first row must be the header, followed only by transaction rows.
                            """
                            },
                    {
                        "document": {
                            "format": "pdf",
                            "name": f"{Path(file_path).stem}",
                            "source": { "bytes": document_bytes}
                        }
                    }
                ]
            }
        ]

    try: 
        response = client.converse(
            modelId = model_id,
            messages = conversation,
            inferenceConfig={"maxTokens": 2500, "temperature": 0.1},
        )

        response_text = response["output"]["message"]["content"][0]["text"]
        return(response_text)
        
    except ClientError as e:
        logging.error(f"Can't invoke model {model_id}. Response: {e}")
        raise
