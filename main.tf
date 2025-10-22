terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.0.0"
    }
  }
}

#aws keys configured in the local with aws cli to avoid hard coding 
provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "pdf_files_bucket" {
    bucket = "pdf-statements-expensee"
    
    tags = {
      Name = "expenSee"
      Environment = "dev" 
    }
}

resource "aws_sns_topic" "textract_sns" {
    name = "textract_job_complete_sns.fifo"
    fifo_topic = true
}

resource "aws_sqs_queue" "textract_result_queue" {
    name = "textract_result_queue.fifo"
    fifo_queue = true

}

resource "aws_sqs_queue_policy" "sns_to_sqs" {
    queue_url = aws_sqs_queue.textract_result_queue.id
    
    policy = jsonencode(
        {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SendMessageToSQS",
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": aws_sqs_queue.textract_result_queue.arn,
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": aws_sns_topic.textract_sns.arn
        }
      }
    }
  ]
}
    )
}

resource "aws_sns_topic_subscription" "subscribe_to_sqs" {
    topic_arn = aws_sns_topic.textract_sns.arn
    protocol = "sqs"
    endpoint = aws_sqs_queue.textract_result_queue.arn
}

