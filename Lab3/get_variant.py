#!/usr/bin/env -S python3
#-*- coding:utf-8 -*-

from sys import argv

alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"    

def get_variant(m):
    h = 0
    for c in m.upper():
        h += alphabet.find(c) + 1
    return (h % 3) + 1

def main():
    if len(argv) < 2:
        print("Usage: %s ФамилияИОФамилияИО..." % (argv[0]))
        return 0
    h = get_variant(argv[1])
    print(h)
    return 0

if __name__ == "__main__":
    main()