import json
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

from utils.s3_utils import upload_file

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
rek = boto3.client('rekognition', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY,
                   region_name='ap-south-1')


def start_detect(file_name):
    try:
        res = rek.start_segment_detection(
            Video={
                'S3Object': {
                    "Bucket": AWS_BUCKET_NAME,
                    "Name": file_name
                },
            },
            SegmentTypes=["SHOT"],
            Filters={
                "ShotFilter": {
                    "MinSegmentConfidence": 90
                }
            },
            NotificationChannel={
                'SNSTopicArn': 'arn:aws:sns:ap-south-1:709303393478:AmazonRekognitionShotStatus',
                'RoleArn': 'arn:aws:iam::709303393478:role/AmazonRekognitionFullAccess',
            }
        )

        startJobId = res['JobId']
        print('Start Job Id: ' + startJobId)
        return startJobId
    except BotoCoreError as e:
        # Handle general BotoCore errors
        print(f"BotoCoreError: {e}")
    except ClientError as e:
        # Handle specific client errors
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"ClientError: {error_code} - {error_message}")
    except Exception as e:
        # Handle other exceptions
        print(f"An unexpected error occurred: {e}")
    return None


def get_result(job_id, file_name):
    response = rek.get_segment_detection(JobId=job_id)
    # Convert JSON data to string
    json_str = json.dumps(response['Segments'])
    file_name = file_name.replace("video", "result").split(".")[0] + ".json"
    print(file_name)
    print(json_str)
    upload_file(json_str, file_name)

