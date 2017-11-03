#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3
import re
import requests
import sys
sys.path.append('C:\Code\SiteScan')

from setting import user_path


class FingerPrint:
    def __init__(self, urls):
        self.conn = sqlite3.connect(user_path + '/db/Rules.db')
        self.cursor = self.conn.cursor()
        self.targets = urls
        self.result = {}
        sql = 'select * from application'
        self.cursor.execute(sql)
        self.rules = self.cursor.fetchall()

    def init(self):
        if self.target.startswith('http://'):
            self.target = self.target[7:]
        elif self.target.startswith('https://'):
            self.target = self.target[8:]
        self.target = self.target.strip('/')

    def scan(self):
        finger_print = ''
        self.init()
        try:
            r = requests.get('http://' + self.target, timeout=3)
            for item in self.rules:
                app = item[1]
                rules = item[2].split(', ')
                # print(app, rule)
                for rule in rules:
                    rule = rule.split(':', 1)
                    place = rule[0]
                    _rule = rule[1]
                    if place in ['body']:
                        if -1 != r.text.find(_rule):
                            finger_print += app+' '
                            break
                    elif place in ['title']:
                        if re.search('<title>.*?'+_rule+'.*?</title>', r.text):
                            finger_print += app+' '
                            break
                    elif place in ['header', 'server']:
                        if -1 != str(r.headers).find(_rule):
                            finger_print += app+' '
                            break
            self.result[self.target] = finger_print

        except requests.exceptions.ConnectionError:
            self.result[self.target] = ''
        except requests.exceptions.ReadTimeout:
            self.result[self.target] = ''
        except requests.exceptions.TooManyRedirects:
            self.result[self.target] = ''

    def run(self):
        print('服务指纹识别')
        for self.target in self.targets:
            self.scan()
            # Database().insert_finger(self.target, self.result[self.target])
        return self.result


if __name__ == '__main__':
    FingerPrint(urls=['http://www.jit.edu.cn/']).run()
