import os
import threading
from utils import redis_util


class ProgressPercentage(object):

    def __init__(self, filename, file_size):
        self._filename = filename
        self._size = float(file_size)
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            message = "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage)
            redis_util.redis_client.publish(os.getenv('REDIS_CHANNEL_NAME'), f"Progress: {percentage}")
