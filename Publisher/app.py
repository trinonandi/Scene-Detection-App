from botocore.exceptions import NoCredentialsError
from flask import Flask, request
from utils import AWS_utils, RabbitMQ_utils

app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload():  # put application's code here
    uploaded_file = request.files['file']
    file_size = int(request.headers.get('Content-Length', 0))
    try:
        AWS_utils.upload_file(uploaded_file, file_size)
    except NoCredentialsError as e:
        app.logger.error(e)
        return 'AWS credentials not available.', 401

    try:
        RabbitMQ_utils.publish(uploaded_file.filename)
    except Exception as e:
        app.logger.error(e)
        return "Unexpected error occurred in pika module", 500
    return 'File Uploaded Successfully', 200


if __name__ == '__main__':
    app.run()
