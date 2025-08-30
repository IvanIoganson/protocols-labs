#!/usr/bin/env -S python3
#-*- coding:utf-8 -*-

from random import getrandbits

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

def gen_key():
    return getrandbits(64)

def SBox(block):
    s_block = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
    res = 0
    for i in range(16):
        res <<= 4
        res |= s_block[(block >> ((15 - i)*4)) & 0xf]
    return res

def inv_SBox(block):
    inv_s_block = [0x5, 0xE, 0xF, 0x8, 0xC, 0x1, 0x2, 0xD, 0xB, 0x4, 0x6, 0x3, 0x0, 0x7, 0x9, 0xA]
    res = 0
    for i in range(16):
        res <<= 4
        res |= inv_s_block[(block >> ((15 - i)*4)) & 0xf]
    return res

def custom_enc(m, key):
    block_size = 64
    round_numbers = 16
    int_m = string_to_int(m) << (block_size - (len(m) % (block_size//8)) * 8)
    blocks_m = []
    while int_m > 0:
        blocks_m += [int_m & ((1<<block_size) - 1)]
        int_m >>= block_size
    blocks_m = blocks_m[::-1]
    
    enc_blocks_m = []
    for block in blocks_m:
        enc_block = block
        for round_counter in range(round_numbers):
            enc_block ^= key
            enc_block = SBox(enc_block)
        enc_blocks_m += [enc_block]
    
    enc_m = 0
    for enc_block in enc_blocks_m:
        enc_m <<= block_size
        enc_m |= enc_block
    return enc_m

def custom_dec(c, key):
    block_size = 64
    round_numbers = 16
    int_c = c
    blocks_c = []
    while int_c > 0:
        blocks_c += [int_c & ((1<<block_size) - 1)]
        int_c >>= block_size
    blocks_c = blocks_c[::-1]
    
    dec_blocks_c = []
    for block in blocks_c:
        dec_block = block
        for round_counter in range(round_numbers):
            dec_block = inv_SBox(dec_block)
            dec_block ^= key
        dec_blocks_c += [dec_block]
    
    dec_c = 0
    for dec_block in dec_blocks_c:
        dec_c <<= block_size
        dec_c |= dec_block
    return int_to_string(dec_c)

in_f = open("flag.txt", "r")
flag = in_f.read()
in_f.close()

flag = "present{" + flag + "}_just_for_test_1234567890abcef"

out_f = open("output.txt", "wt")
out_f.write(str(custom_enc(flag, gen_key())))
out_f.close()