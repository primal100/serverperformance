import unittest
import os
import socket
import multiprocessing


class BaseTestCase(unittest.TestCase):
    num_to_send = 100
    msg_size = 100
    stop_event = multiprocessing.Event()
    done_event = multiprocessing.Event()

    def run_server(self, *args):
        raise NotImplementedError

    def start_server_process(self, s, h, e, a):
        process = multiprocessing.Process(target=self.run_server,
                                          args=(s, h, e, a))
        process.start()

    def wait_done(self):
        self.done_event.wait(timeout=30)

    def close_server_process(self):
        self.stop_event.set()

    def stop_server(self):
        self.stop_event.set()

    def run_client(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect(('localhost', 9999))
            for i in range(0, 100):
                data = os.urandom(self.msg_size)
                sock.sendall(data)
        finally:
            sock.close()
