#!/usr/bin/env -S python3
#-*- coding:utf-8 -*-

import os
import socketserver
import threading
import time
import random

#Расширенный алгоритм Евклида
def ext_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        gcd, x, y = ext_gcd(b % a, a)
    return (gcd, y - (b // a) * x, x)

#Класс для работы в конечном поле GF(p)
class field:
    p = (1<<255) - 19

    def __init__(self, a):
        self.num = a % self.p
    
    def __add__(self, other):
        if other.__class__ == field:
            return field(self.num + other.num) 
        else:
            return field(self.num + other)
        
    def __sub__(self, other):
        if other.__class__ == field:
            return field(self.num - other.num)
        else:
            return field(self.num - other)
        
    def __mul__(self, other):
        if other.__class__ == field:
            return field(self.num * other.num)
        else:
            return field(self.num * other)

    def __truediv__(self, other):
        if other.__class__ == field:
            return field(self.num * ext_gcd(other.num, self.p)[1])
        else:
            return field(self.num * ext_gcd(other, self.p)[1])

    def __pow__(self, other):
        return field(pow(self.num, other, self.p))
    
    def __eq__(self, other):
        if other.__class__ == field:
            return self.num % self.p == other.num % self.p
        else:
            return self.num % self.p == other % self.p

    def __ne__(self, other):
        if other.__class__ == field:
            return self.num % self.p != other.num % self.p
        else:
            return self.num % self.p != other % self.p

#Функции для работы с эллиптическими кривыми Монтгомери
#Умножение точки P на 2 для кривой с коэффициентом A
def montgomery_double(A, P):
    xP = P[0]
    zP = P[1]
    x2P = (xP + zP)**2 * (xP - zP)**2
    z2P = xP*4*zP*((xP - zP)**2 + (A+2) * xP * zP)
    if z2P == 0:
        return (field(1), field(0))
    return (x2P, z2P)

#Cложение точек P и Q (зная PmQ = P - Q) для кривой с коэффициентом A
def montgomery_add(A, P, Q, PmQ):
    xPpQ = PmQ[1] * ((P[0] - P[1])*(Q[0] + Q[1]) + (P[0] + P[1])*(Q[0] - Q[1]))**2
    zPpQ = PmQ[0] * ((P[0] - P[1])*(Q[0] + Q[1]) - (P[0] + P[1])*(Q[0] - Q[1]))**2
    if zPpQ == 0:
        return (field(1), field(0))
    return (xPpQ, zPpQ)

#Алгоритм Монтгомери для умножения точки P на число s для кривой с коэффициентом A
def montgomery_ladder(A, s, P):
    R0 = P
    R1 = montgomery_double(A, P)
    for b in [int(i) for i in bin(s)[3:]]:
        if b == 0:
            R1 = montgomery_add(A, R0, R1, P)
            R0 = montgomery_double(A, R0)
        else:
            R0 = montgomery_add(A, R0, R1, P)
            R1 = montgomery_double(A, R1)
    return R0

#Коэффициент кривой Монтгомери Curve25519
A = field(486662)
#Генераторная точка
P = (field(9),field(1))
#Порядок генераторной точки
P_order = (1<<252)+27742317777372353535851937790883648493

def get_flag():
    in_f = open("Task3/flag.txt", "r")
    flag = in_f.read()
    in_f.close()
    return flag

def get_rand_point():
    return montgomery_ladder(A, random.randint(1, P_order-1), P)

def get_token(id, Q):
    T = montgomery_ladder(A, id, Q)
    token = (T[0] / T[1]).num
    return token

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.request.settimeout(600)  #10 минут таймаут

    def init(self):
        self.max_recv_size = 1024
        self.ID = random.randint(1, 100)
        self.Q = get_rand_point()
        self.my_token = get_token(self.ID, self.Q)
        self.counted_tokens = []
        self.threshold = 10
        self.request.sendall("Welcome to Ellectronic Voting System! Insert your token to vote and get the flag!\n(Input \"H\" to show help)\n".encode())

    def menu(self):
        self.request.sendall("Choose option: ".encode())
        choise = self.request.recv(self.max_recv_size).decode()
        while choise[0] == "H" or choise[0] == "h":
            menu_str = "1 - Show my ID\n2 - Show my token\n3 - Vote\n4 - Print flag\n5 - Exit\nH - This text\n"
            self.request.sendall(menu_str.encode())
            self.request.sendall("Choose option: ".encode())
            choise = self.request.recv(self.max_recv_size).decode()
        return int(choise)
     
    def print_ID(self):
        self.request.sendall(("Your ID: " + str(self.ID) + "\n").encode())
     
    def print_token(self):
        self.request.sendall(("Your token: " + hex(self.my_token)[2:] + "\n").encode())

    def vote(self):
        self.request.sendall("ID: ".encode())
        ID1 = int(self.request.recv(self.max_recv_size))
        self.request.sendall("Token: ".encode())
        token1 = int(self.request.recv(self.max_recv_size), 16)
        if get_token(ID1, self.Q) == token1:
            if not token1 in self.counted_tokens:
                self.request.sendall("Vote is counted!\n".encode())
                self.counted_tokens.append(token1)
            else:
                self.request.sendall("Token is already used!\n".encode())
        else:
            self.request.sendall("Token is incorrect!\n".encode())
     
    def print_flag(self):
        if len(self.counted_tokens) < self.threshold:
            self.request.sendall("{}/{} voted\n".format(len(self.counted_tokens), self.threshold).encode())
        else:
            self.request.sendall(("Here is your flag: " + get_flag() + "\n").encode())
     
    def handle(self):
        try:
            self.init()
            while(True):
                choise = self.menu()
                if choise == 1:
                    self.print_ID()
                elif choise == 2:
                    self.print_token()
                elif choise == 3:
                    self.vote()
                elif choise == 4:
                    self.print_flag()
                elif choise == 5:
                    return
                else:
                    self.request.sendall(("Incorrect choise\n").encode())
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

start_server(port=61003)