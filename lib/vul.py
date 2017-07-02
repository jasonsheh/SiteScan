#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.vuls.sqltest import Sql
from lib.vuls.struts2 import Struts2
from lib.vuls.xss import Xss

class Vul:
    def __init__(self, urls, id=''):
        self.id = id
        self.urls = urls

    def service(self):
        for url in self.urls:
            if sql(url):
                Sql(url)
            if struts2(url):
                Struts2(url)
            if xss(url):
                Xss(url)
