#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import memcache


class MemcachedUnauthorized(POC):
    def __init__(self, ip):
        self.ip = ip

    def info(self):
        info = {
            'name': 'MemcachedUnauthorized',
            'level': 'high',
            'type': 'unauthorized',
        }
        return info

    def check(self):
        try:
            conn = memcache.Client([str(self.ip)+':11211'])
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    MemcachedUnauthorized('45.32.116.229').check()
