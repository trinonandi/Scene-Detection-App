import threading

from flask import Flask

from utils import consumer

app = Flask(__name__)

# Start RabbitMQ consumer in a separate thread
rabbitmq_thread = threading.Thread(target=consumer.consume)
rabbitmq_thread.start()


@app.route('/')
def index():
    return "Consumer Up!", 200


if __name__ == '__main__':
    app.run()
