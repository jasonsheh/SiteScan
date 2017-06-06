#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3
import re
import requests


class FingerPrint:
    def __init__(self, url):
        self.conn = sqlite3.connect('/home/jasonsheh/Tools/python/SiteScan/db/Rules.db')
        self.cursor = self.conn.cursor()
        self.target = url

    def init(self):
        if self.target.startswith('http://www.'):
            self.target = self.target[11:]
        elif self.target.startswith('https://www.'):
            self.target = self.target[12:]
        elif self.target.startswith('http://'):
            self.target = self.target[7:]
        elif self.target.startswith('https://'):
            self.target = self.target[8:]

    def scan(self):
        self.init()
        r = requests.get('http://' + self.target)
        sql = 'select * from application'
        self.cursor.execute(sql)
        rules = self.cursor.fetchall()
        for item in rules:

            app = item[1]
            rule = item[2].split(', ')
            # print(app, rule)
            for _rule in rule:
                _rule = _rule.split(':', 1)
                place = _rule[0]
                __rule = _rule[1]
                if place in ['body', 'title']:
                    if -1 != r.text.find(__rule):
                        print(app)
                elif place in ['header', 'server']:
                    if -1 != str(r.headers).find(__rule):
                        print(app)

if __name__ == '__main__':
    FingerPrint(url='www.ecshop.tv').scan()

