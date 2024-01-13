import os
import sys
import time
import json

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from utils.rekognition import get_result

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_SQS_URL = os.getenv('AWS_SQS_URL')

sqs = boto3.client('sqs', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name='ap-south-1')


def get_sqs_message_success(job_id, file_name):
    global rekMessage
    jobFound = False
    succeeded = False

    dotLine = 0
    while not jobFound:
        try:
            sqsResponse = sqs.receive_message(QueueUrl=AWS_SQS_URL, MessageAttributeNames=['ALL'],
                                          MaxNumberOfMessages=10)
            if sqsResponse:

                if 'Messages' not in sqsResponse:
                    if dotLine < 40:
                        print('.', end='')
                        dotLine = dotLine + 1
                    else:
                        print()
                        dotLine = 0
                    sys.stdout.flush()
                    time.sleep(5)
                    continue

                for message in sqsResponse['Messages']:
                    notification = json.loads(message['Body'])
                    rekMessage = json.loads(notification['Message'])
                    if rekMessage['JobId'] == job_id:
                        print('Matching Job Found:' + rekMessage['JobId'])
                        jobFound = True
                        if rekMessage['Status'] == 'SUCCEEDED':
                            succeeded = True

                        sqs.delete_message(QueueUrl=AWS_SQS_URL,
                                           ReceiptHandle=message['ReceiptHandle'])
                    else:
                        print("Job didn't match:" +
                              str(rekMessage['JobId']) + ' : ' + job_id)

        except ClientError as e:
            # Handle specific client errors
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"ClientError: {error_code} - {error_message}")
            break

    if succeeded:
        get_result(job_id, file_name)
    else:
        print("Job FAILED with reason" + rekMessage['Message'])



