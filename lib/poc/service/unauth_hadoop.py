#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import requests


class HadoopUnauthorized(POC):
    def __init__(self, ip):
        self.ip = ip

    def info(self):
        info = {
            'name': 'HadoopUnauthorized',
            'level': 'high',
            'type': 'unauthorized',
        }
        return info

    def check(self):
        try:
            resp = requests.get('http://{}:50070'.format(self.ip))
            if 'hadoop' in resp.text.lower():
                return True
            return False
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    HadoopUnauthorized('185.93.31.44').check()
