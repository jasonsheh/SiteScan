#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import requests


class ElasticSearchUnauthorized(POC):
    def __init__(self, ip):
        self.ip = ip

    def info(self):
        info = {
            'name': 'ElasticSearchUnauthorized',
            'level': 'high',
            'type': 'unauthorized',
        }
        return info

    def check(self):
        try:
            resp = requests.get('http://{}:9200'.format(self.ip))
            if 'You Know, for Search' in resp.text:
                return True
            return False
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    ElasticSearchUnauthorized('101.132.42.189').check()
