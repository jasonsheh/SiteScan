#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import redis


class RedisUnauthorized(POC):
    def __init__(self, ip):
        self.ip = ip

    def info(self):
        info = {
            'name': 'RedisUnauthorized',
            'level': 'high',
            'type': 'unauthorized',
        }
        return info

    def check(self):
        try:
            conn = redis.Redis(host=ip, port=6379, decode_responses=True)
            conn.set('test', 'test', ex=3, nx=True)
            if conn['test'] == 'test':
                return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    RedisUnauthorized('192.155.86.88').check()
