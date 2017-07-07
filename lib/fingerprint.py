#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3
import re
import requests

from database.database import Database


class FingerPrint:
    def __init__(self, urls):
        self.conn = sqlite3.connect('/home/jasonsheh/Tools/python/SiteScan/db/Rules.db')
        self.cursor = self.conn.cursor()
        self.targets = urls
        self.result = {}
        sql = 'select * from application'
        self.cursor.execute(sql)
        self.rules = self.cursor.fetchall()

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
        finger_print = ''
        self.init()
        try:
            r = requests.get('http://' + self.target, timeout=3)
            for item in self.rules:
                app = item[1]
                rule = item[2].split(', ')
                # print(app, rule)
                for _rule in rule:
                    _rule = _rule.split(':', 1)
                    place = _rule[0]
                    __rule = _rule[1]
                    if place in ['body']:
                        if -1 != r.text.find(__rule):
                            finger_print += app+' '
                            break
                    elif place in ['title']:
                        if re.search('<title>.*?'+__rule+'.*?</title>', r.text):
                            finger_print += app+' '
                            break
                    elif place in ['header', 'server']:
                        if -1 != str(r.headers).find(__rule):
                            finger_print += app+' '
                            break
            self.result[self.target] = finger_print

        except requests.exceptions.ConnectionError:
            self.result[self.target] = ''
        except requests.exceptions.ReadTimeout:
            self.result[self.target] = ''

    def run(self):
        print('服务指纹识别')
        for self.target in self.targets:
            self.scan()
            # Database().insert_finger(self.target, self.result[self.target])
            # print(self.result)
        return self.result

if __name__ == '__main__':
    FingerPrint(urls=['http://zkxy.jit.edu.cn/admin/']).run()
