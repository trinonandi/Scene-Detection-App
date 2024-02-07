import json
import os
import pika
import ssl

from dotenv import load_dotenv

from utils import rekognition_util, s3_utils
from utils.sqs_utils import get_sqs_message_success


load_dotenv()

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
connection_params = pika.ConnectionParameters(
    host=os.getenv('RABBITMQ_HOST'),
    port=int(os.getenv('RABBITMQ_PORT')),
    virtual_host=os.getenv('RABBITMQ_VHOST'),
    heartbeat=30,
    ssl_options=pika.SSLOptions(context=ssl_context),
    credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))
)


def consume():
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.basic_consume(queue='my_queue', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


def callback(ch, method, properties, body):
    message = json.loads(body.decode('utf-8'))
    print(message)
    video_identifier = message.get('file_name')
    pyscene_threshold = int(message.get('pyscene_threshold'))
    min_scene_length = int(message.get('min_scene_length'))

    # call the rekognition apu and start the job with a jobid
    job_id = rekognition_util.start_detect(video_identifier)
    if job_id is not None:
        # pass the jodid and match with the messages received and sqs and check status
        # if status success get the result
        # store the result to s3
        get_sqs_message_success(job_id, video_identifier)
        rekognition_util.get_result(job_id, video_identifier, pyscene_threshold, min_scene_length)


if __name__ == '__main__':
    consume()
