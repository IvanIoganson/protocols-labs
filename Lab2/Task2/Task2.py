#!/usr/bin/env -S python3
#-*- coding:utf-8 -*-

import os
import socketserver
import threading
import time

p = 89465071510451101439525273936168511846212445777253520237331698308678503116711043331239104245398349384731391438449504381987949833760932837924368752438143162361048734845462627807539672689912899366514724151681627526140457783428680216876840883532954892702870229862250931999278287416476058989043062146485407855403449
g = 19
y = 30647844200876100331623991677764594348659383358709862404464894077310947688115896216714514674906760959938561827369017433513737387934489781288052406713928150643508607078917491760907503970739687767052853991050484854135323701379976152486903452411422587364742080228378161530191689796166782879086137648697715795619364

def get_flag():
    in_f = open("Task2/flag.txt", "r")
    flag = in_f.read()
    in_f.close()
    return flag

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.request.settimeout(600)  #10 минут таймаут

    def handle(self):
        try:
            max_recv_size = 1024
            self.request.sendall("Prove your knowledge\n".encode())
            correct = True
            for challenge in [0,1,1,0,1]:
                self.request.sendall("Choose C = g^r mod p\n".encode())
                C = int(self.request.recv(max_recv_size))
                if challenge == 0:
                    self.request.sendall("Give me r\n".encode())
                    r = int(self.request.recv(max_recv_size))
                    if pow(g, r, p) != C:
                        correct = False
                        break
                else:
                    self.request.sendall("Give me x+r\n".encode())
                    xr = int(self.request.recv(max_recv_size))
                    if pow(g, xr, p) != (C*y) % p:
                        correct = False
                        break
            if correct:
                self.request.sendall(("Here is your flag: " + get_flag() + "\n").encode())
            else:
                self.request.sendall(("You don't know the Secret...\n").encode())
        except Exception as e:
            error = getattr(e, 'message', repr(e))
            self.request.sendall("Error: {}\n".format(error).encode())
            return


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

start_server(port=61002)
