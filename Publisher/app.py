from botocore.exceptions import NoCredentialsError
from flask import Flask, request, send_from_directory
from utils import aws_utils, rabbitmq_util
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__, static_url_path='/static')
socketio = SocketIO(app)

# Specify allowed origins. Need to find a better way
CORS(app, resources={r"/sse": {"origins": ["http://127.0.0.1:5000", "http://localhost:63342"]}})


# Testing frontend
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')


@app.route('/upload/<socket_id>', methods=['POST'])
def upload(socket_id):  # put application's code here
    print(request.files.keys())
    uploaded_file = request.files['file']
    file_size = request.values.get('fileSize')
    try:
        aws_utils.upload_file(uploaded_file, file_size, socketio, socket_id)

    # TODO: Remove it
    except NoCredentialsError as e:
        app.logger.error(e)
        return 'AWS credentials not available.', 401

    try:
        rabbitmq_util.publish(uploaded_file.filename)
    except Exception as e:
        app.logger.error(e)
        return "Unexpected error occurred in pika module", 500
    return 'File uploading started successfully', 200


if __name__ == '__main__':
    socketio.run(app=app, debug=True)
