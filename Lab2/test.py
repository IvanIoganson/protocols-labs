#!/usr/bin/env python3

import os
import socketserver
import threading
import time
import sys

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.request.settimeout(600)

    def handle(self):
        max_recv_size = 1024

        while True:
            self.request.sendall("1+1=?\n".encode())
            buffer = self.request.recv(max_recv_size)
            try:
                if int(buffer) == 2:
                        self.request.sendall("Correct!\n".encode())
                        break
                else:
                    self.request.sendall("Incorrect...\n".encode())
            except Exception as e:
                error = getattr(e, 'message', repr(e))
                self.request.sendall("Error: {}\n".format(error).encode())
                break


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def start_server(port=0):
    with ThreadedTCPServer(('0.0.0.0', port), ThreadedTCPRequestHandler) as server:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        while True:
            if threading.active_count() > 75:
                raise Exception()
            time.sleep(100)

        server_thread.join()

start_server(port=60000)