#!/usr/bin/env -S python
#-*- coding:utf-8 -*-

import random

#Преобразуем строку в число
def string_to_int(s):
    res = 0
    for c in s:
        res = res * 256 + ord(c)
    return res
    
#Преобразуем число в строку
def int_to_string(n):
    res = ""
    while n > 0:
        res += chr(n % 256)
        n //= 256
    return res[::-1]

#Сумма элементов списка
def sum(arr):
    res = 0
    for el in arr:
        res = el + res
    return res

#Перемножение элементов списка
def mul(arr):
    res = 1
    for el in arr:
        res = el * res
    return res

#Алгоритм Евклида
def gcd(a,b):
    while a != 0:
        c = a
        a = b%a
        b = c
    return b

#Символ Якоби
def jacobi_symbol(a, b):
    if gcd(a,b) != 1:
        return 0
    r = 1
    if a < 0:
        a = -a
        if b%4 == 3:
            r = -r
    while a != 0:
        t = 0
        while a%2 == 0:
            t += 1
            a = a//2
        if t%2 == 1:
            if b%8 == 3 or b%8 == 5:
                r = -r
        if a%4 == 3 and b%4 == 3:
            r = -r
        c = a
        a = b%c
        b = c
    return r

#Расширенный алгоритм Евклида
def ext_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        gcd, x, y = ext_gcd(b % a, a)
    return (gcd, y - (b // a) * x, x)

#Класс для работы в конечном поле GF(p)
class field:
    p = 5326738796327623094747867617954605554069371494832722337612446642054009560026576537626892113026381253624626941643949444792662881241621373288942880288065659

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

#Функция для генерации подгруппы порожденной точкой P для кривой с коэффициентом A
def montgomery_gen_subgroup(A, P):
    res = [P, montgomery_double(A, P)]
    while res[-1][1] != 0:
        res.append(montgomery_add(A, res[-1], P, res[-2]))
    return res

#Вычисление изогеной кривой для кривой с коэффициентом A по подгруппе P_ker и вычисление значение этой изогении для точки Q
def montgomery_isogeny_eval(A, P_ker, Q):
    ker = montgomery_gen_subgroup(A, P_ker)
    ker = ker[:-1]
    c02 = mul([x/z for x,z in ker])
    sig = sum([x/z - z/x for x,z in ker])
    A1 = c02*(A - sig*3)
    
    for P in ker:
        if Q[0]*P[1] == P[0]*Q[1]:
            return A1, (field(1), field(0))
    phi_x = Q[0]/Q[1] * mul([(x/z * Q[0]/Q[1] - 1) / (Q[0]/Q[1] - x/z) for x,z in ker])
    return A1, (phi_x, field(1))

#Вычисление групповой операции из протокола CSIDH
def csidh_group_action(p, A0, l, v):
    A = field(A0)
    v = list(v)
    points_list = []
    while v != [0] * len(v):
        xP = field(random.randint(1, field.p-1))
        s = jacobi_symbol((xP**3 + A*xP**2 + xP).num, field.p)
        Sv = [i for i in range(len(v)) if v[i] != 0 and v[i] // abs(v[i]) == s]
        if len(Sv) == 0:
            continue
        k = mul([l[i] for i in Sv])
        Ap2 = A
        P = (xP, field(1))
        Q = montgomery_ladder(Ap2, (p+1) // k, P)
        points_list.append((Q[0] / Q[1]).num)
        for i in Sv:
            R = montgomery_ladder(Ap2, k // l[i], Q)
            if R[1] == 0:
                continue
            Ap2, Q = montgomery_isogeny_eval(Ap2, R, Q)
            k = k // l[i]
            v[i] = v[i] - s
        A = Ap2
    return A, points_list

# p = 4 * mul(prime_list) - 1
prime_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 587]

A0 = 0
v = []
for i in range(len(prime_list)):
    v.append(random.randint(-5, 5))
A, points_list = csidh_group_action(field.p, A0, prime_list, v)

inf = open("flag.txt", "rt")
flag = inf.read()
flag = string_to_int(flag)
inf.close()

enc_flag = (A * flag).num

outf = open("output.txt", "wt")
outf.write("enc_flag = " + str(enc_flag) + "\n")
outf.write("points = " + str(points_list) + "\n")
outf.close()