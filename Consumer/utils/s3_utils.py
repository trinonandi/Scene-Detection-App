# Configure AWS credentials
import os

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# create a client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)


def upload_file(body, file_name):
    s3.put_object(Body=body,
                  Bucket=AWS_BUCKET_NAME,
                  Key=file_name
                  )
    print("Response stored in S3")
