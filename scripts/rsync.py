#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import socket


class Rsync:
    def __init__(self, target):
        self.target = target

    def connect(self):
        s = socket.socket()
        socket.setdefaulttimeout(5)
        try:
            port = 873
            s.connect((self.target, port))
            print('Rsync未授权访问')
        except Exception as e:
            print(e)
            pass
        s.close()

    def run(self):
        self.connect()


def main():
    f = Rsync(target='78.22.115.230')
    f.run()

if __name__ == '__main__':
    main()
