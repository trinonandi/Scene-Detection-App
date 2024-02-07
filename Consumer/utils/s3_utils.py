# Configure AWS credentials
import os
import pathlib
import sys

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# create a client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)


cwd = pathlib.Path(__file__).parent

def upload_file(body, file_name):
    s3.put_object(Body=body,
                  Bucket=AWS_BUCKET_NAME,
                  Key=file_name
                  )
    print("Response stored in S3")


def download_file(file_name):
    meta_data = s3.head_object(Bucket=AWS_BUCKET_NAME, Key=file_name)
    total_length = int(meta_data.get('ContentLength', 0))
    downloaded = 0

    def progress(chunk):
        nonlocal downloaded
        downloaded += chunk
        done = int(50 * downloaded / total_length)
        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
        sys.stdout.flush()

    path = os.path.join(cwd.parent, f'video/{file_name}')
    print(path)
    with open(path, 'wb') as file:
        print("Downloading Started")
        s3.download_fileobj(AWS_BUCKET_NAME, file_name, file, Callback=progress)