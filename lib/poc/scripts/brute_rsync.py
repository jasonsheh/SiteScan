#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import socket


class RsyncUnauthorized(POC):
    def __init__(self, ip):
        self.ip = ip

    def info(self):
        info = {
            'name': 'RsyncUnauthorized',
            'level': 'high',
            'type': 'unauthorized',
        }
        return info

    def check(self):
        s = socket.socket()
        socket.setdefaulttimeout(5)
        try:
            s.connect((self.ip, 873))
            s.close()
            return True
        except Exception as e:
            return False


if __name__ == '__main__':
    RsyncUnauthorized('78.22.115.230').check()
