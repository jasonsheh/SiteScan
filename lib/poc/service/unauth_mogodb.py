#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import pymongo


class MongodbUnauthorized(POC):
    def __init__(self, ip):
        self.ip = ip

    def info(self):
        info = {
            'name': 'MongodbUnauthorized',
            'level': 'high',
            'type': 'unauthorized',
        }
        return info

    def check(self):
        try:
            conn = pymongo.MongoClient(self.ip, 27017)
            dbname = conn.list_database_names()
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    print(MongodbUnauthorized('218.95.177.150').check())
