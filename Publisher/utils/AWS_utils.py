# Configure AWS credentials
import os

import boto3
from dotenv import load_dotenv
from utils.ProgressPercentage import ProgressPercentage

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# create a client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)


def upload_file(file, file_size):
    s3.upload_fileobj(file,
                      AWS_BUCKET_NAME,
                      file.filename,
                      Callback=ProgressPercentage(file.filename, file_size)
                      )