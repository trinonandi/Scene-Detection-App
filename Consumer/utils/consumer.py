import os
import pika
import ssl

from dotenv import load_dotenv

from utils import rekognition
from utils.sqs_util import get_sqs_message_success

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
    print(f"Received message: {body.decode('utf-8')}")
    # call the rekognition apu and start the job with a jobid
    job_id = rekognition.start_detect(body.decode('utf-8'))
    if job_id is not None:
        # pass the jodid and match with the messages received and sqs and check status
        # if status success get the result
        # store the result to s3
        get_sqs_message_success(job_id, body.decode('utf-8'))


if __name__ == '__main__':
    consume()
