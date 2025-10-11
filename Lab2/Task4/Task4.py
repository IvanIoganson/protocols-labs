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
    in_f = open("Task4/flag.txt", "r")
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

#Генерация сильного простого числа и генератора простой подгуппы
def gen_strong_prime_and_generator(prime_bits):
    p = next_prime(random.getrandbits(prime_bits))
    f = 2
    while not is_prime(f*p+1):
        f+=1
    g = 2
    while pow(g, p, f*p+1) != 1:
        g+=1
    return (p, f, g)

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.request.settimeout(1)  # 1 секунда таймаут

    def handle(self):
        try:
            max_recv_size = 1024
            self.request.sendall("Strong prime number generator. Better think fast, connection won't stay for long...\nGenerating strong prime number...\n".encode())
            p, f, g = gen_strong_prime_and_generator(1024)
            q = f*p+1
            current_question_number = 0
            total_question_number = 100
            while current_question_number < total_question_number:
                x = pow(g, random.randint(1, p-1), q)               
                a = random.randint(1, p-1)
                self.request.sendall("{}/{}: pow(x,{},{})={}\nx=".format(current_question_number+1, total_question_number, a, q, pow(x,a,q)).encode())
                C = int(self.request.recv(max_recv_size))
                if C != x:
                    break
                current_question_number+=1
            if current_question_number == total_question_number:
                self.request.sendall("Here is flag: {}\n".format(get_flag()).encode())
            else:
                self.request.sendall("You failed. Disconnecting...\n".encode())
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

start_server(port=61004)
