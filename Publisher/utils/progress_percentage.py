import sys
import threading


class ProgressPercentage(object):

    def __init__(self, filename, file_size, socketio, socket_id):
        self._filename = filename
        self._size = float(file_size)
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._socketio = socketio
        self._socket_id = socket_id

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            message = "\r%s  %s / %s  (%.2f%%)" % (
                self._filename, self._seen_so_far, self._size,
                percentage)
            sys.stdout.write(message)
            self._socketio.emit("update progress", percentage, to=self._socket_id)
            sys.stdout.flush()
