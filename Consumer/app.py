import threading

from flask import Flask

import rabbit_consumer

app = Flask(__name__)

# Start RabbitMQ consumer in a separate thread
rabbitmq_thread = threading.Thread(target=rabbit_consumer.consume)
rabbitmq_thread.start()


@app.route('/')
def index():
    return "Consumer Up!", 200


if __name__ == '__main__':
    app.run(port=8000)
