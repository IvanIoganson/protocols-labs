#!/usr/bin/env -S python3
#-*- coding:utf-8 -*-

from hashlib import shake_256
from sys import argv

def hash_message_to_generator_Fp(m, p, p_1_factors):
    g = m
    h = shake_256()
    g_len = (len(bin(p)) - 2) // 8 + 1
    while True:
        s = hex(g)[2:]
        if len(s) % 2 == 1:
            s = "0" + s
        h.update(bytes.fromhex(s))
        g = int(h.hexdigest(g_len), 16) % p
        if g == 0 or g == 1:
            continue
        is_generator = True
        for f in p_1_factors:
            if pow(g, (p-1) // f, p) == 1:
                is_generator = False
                break
        if is_generator:
            return g     

def my_hash(m):
    while len(m) % 8 != 0:
        m += b"\x00"
    h = b"\x01\x23\x45\x67\x89\xab\xcd\xef"
    for i in range(0, len(m), 8):
        chunk = m[i:i+8]
        Sg = [hash_message_to_generator_Fp(mi, 257, [2]) for mi in chunk]
        L = [pow(sgi, mi, 257)-1 for sgi, mi in zip(Sg, chunk)]
        next_h = bytes([hi ^ li for hi, li in zip(h, L)])
        h = next_h
    return h

def main():
    if len(argv) < 2:
        print("Usage: %s message" % (argv[0]))
        return 0
    h = my_hash(argv[1].encode())
    print(h.hex())
    return 0


if __name__ == "__main__":
    main()