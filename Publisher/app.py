import logging
import os

from botocore.exceptions import NoCredentialsError
from flask import Flask, request, Response, send_from_directory
from utils import aws_utils, rabbitmq_util, redis_util
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')

# Specify allowed origins. Need to find a better way
CORS(app, resources={r"/sse": {"origins": "http://127.0.0.1:5000"}})


# Testing frontend
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')


# Server side event route to send file upload progress percent
# Recommended to use HTTP/2 to avoid concurrent bottleneck
@app.route('/sse', methods=["GET"])
def sse():
    def sse_events():
        # Initiate Redis pub/sub
        pubsub = redis_util.redis_client.pubsub()
        pubsub.subscribe(os.getenv('REDIS_CHANNEL_NAME'))

        for message in pubsub.listen():
            try:
                data = message.get('data')
                yield f"data: {data}\n\n"
            except Exception as e:
                logging.error(e)

    return Response(sse_events(), mimetype="text/event-stream")


@app.route('/upload', methods=['POST'])
def upload():  # put application's code here
    uploaded_file = request.files['file']
    file_size = int(request.headers.get('Content-Length', 0))
    try:
        aws_utils.upload_file(uploaded_file, file_size)
    except NoCredentialsError as e:
        app.logger.error(e)
        return 'AWS credentials not available.', 401

    try:
        rabbitmq_util.publish(uploaded_file.filename)
    except Exception as e:
        app.logger.error(e)
        return "Unexpected error occurred in pika module", 500
    return 'File Uploaded Successfully', 200


if __name__ == '__main__':
    app.run()
