import os
import ssl
from dotenv import load_dotenv
import pika

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
ROUTING_KEY = 'my_queue'


def publish(message):
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.basic_publish(exchange='test', routing_key=ROUTING_KEY, body=message)
    connection.close()
