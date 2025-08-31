#!/usr/bin/env -S python3
#-*- coding:utf-8 -*-

from sys import argv
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

def main():
    if len(argv) < 2:
        print("Usage: %s message" % (argv[0]))
        return 0
    message = string_to_int(argv[1])
    p = next_prime(random.getrandbits(1024))
    q = next_prime(p**2)
    N = p*q
    e = 65537
    c = pow(message, e, N)
    f = open("output.txt", "wt")
    f.write("N = %d\n" % (N))
    f.write("c = %d\n" % (c))
    f.close()
    return 0

if __name__ == "__main__":
    main()