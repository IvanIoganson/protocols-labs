#!/usr/bin/env -S python3
#-*- coding:utf-8 -*-

import os
import socketserver
import threading
import time
import random

def str_to_int(s):
    return int(bytes.hex(s.encode()),16)
    
def int_to_str(n):
    return bytes.fromhex(hex(n)[2:]).decode()

def get_flag():
    in_f = open("Task1/flag.txt", "r")
    flag = in_f.read()
    in_f.close()
    return flag

#Тест Миллера—Рабина на простоту числа
def is_prime(n, num_of_iter = 20):
    if n%2 == 0:
        return False
    t = n - 1
    s = 0
    while t%2 == 0:
        t //= 2
        s += 1
    for _ in range(num_of_iter):
        a = random.randint(2, n - 1)
        if pow(a, t, n) == 1:
            continue
        i = 0
        while i < s:
            if pow(a, 2**i * t, n) == n-1:
                break
            i += 1
        if i == s:
            return False
    return True

#Функция для генерации простого числа
def next_prime(n):
    res = n
    if res % 2 == 0:
        res += 1
    while not is_prime(res):
        res += 2
    return res

#Расширенный алгоритм Евклида
def ext_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        gcd, x, y = ext_gcd(b % a, a)
    return (gcd, y - (b // a) * x, x)

def rsa_keygen(prime_bits):
    p = next_prime(random.getrandbits(prime_bits))
    q = next_prime(random.getrandbits(prime_bits))
    e = 65537
    d = ext_gcd(e, (p-1)*(q-1))[1]
    return (p, q, e, d)

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.request.settimeout(600)  #10 минут таймаут

    def handle(self):
        try:
            max_recv_size = 1024
            self.request.sendall("RSA Decryption Oracle\nGenerating RSA key pair...\n".encode())
            p, q, e, d = rsa_keygen(1024)
            N = p*q
            enc_flag = pow(str_to_int(get_flag()), e, N)
            self.request.sendall("Public key:\n".encode())
            self.request.sendall("e = {}\n".format(e).encode())
            self.request.sendall("N = {}\n".format(N).encode())
            self.request.sendall("Encrypted flag: {}\n".format(enc_flag).encode())
            self.request.sendall("Ciphertext to decrypt: ".encode())            
            C = int(self.request.recv(max_recv_size))
            if C == enc_flag:
                self.request.sendall("Cannot decrypt the flag!\n".encode())
            else:
                self.request.sendall("Decrypted message: {}\n".format(pow(C, d, N)).encode())
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

start_server(port=61001)
