#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import kazoo.client


class ZookeeperUnauthorized(POC):
    def __init__(self, ip):
        self.ip = ip

    def info(self):
        info = {
            'name': 'ZookeeperUnauthorized',
            'level': 'high',
            'type': 'unauthorized',
        }
        return info

    def check(self):
        try:
            conn = kazoo.client.KazooClient(hosts=str(self.ip)+':2181')
            conn.start()
            conn.stop()
            conn.close()
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    ZookeeperUnauthorized('207.244.79.99').check()
