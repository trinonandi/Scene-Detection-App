import os
import ssl

import pika
from flask import Flask, request
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = '/Users/trinanjan/Desktop/Microservice/Publisher/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
connection_params = pika.ConnectionParameters(
    host=os.getenv('RABBITMQ_HOST'),
    port=int(os.getenv('RABBITMQ_PORT')),
    virtual_host=os.getenv('RABBITMQ_VHOST'),
    heartbeat=30,
    ssl_options=pika.SSLOptions(context=ssl_context),
    credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))
)


@app.route('/upload', methods=['POST'])
def upload():  # put application's code here
    uploaded_file = request.files['file']

    # uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename)))

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    queue_name = 'my_queue'
    message = b'Hello, RabbitMQ!'

    channel.basic_publish(exchange='test', routing_key=queue_name, body=message)

    connection.close()

    return 'File Downloaded Successfully', 200


if __name__ == '__main__':
    app.run()
