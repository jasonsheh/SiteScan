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
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
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
            r = requests.get('http://' + self.target, timeout=3, headers=self.headers)
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
                        header = ''
                        for key, value in r.headers.items():
                            header += key + ': ' + value + ' '
                        if re.search(re.escape(_rule), header, re.I):
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
    result = FingerPrint(urls=['http://www.freebuf.com/', 'http://www.52pojie.cn', 'http://bbs.ichunqiu.com',
                               'http://www.zoomeye.org', 'http://octfive.cn', 'http://demo.typecho.cc/', 'http://znyywlw.jit.edu.cn']).run()
    for site, fingerprint in result.items():
        print(site)
        for fp in fingerprint.split(' '):
            print(fp)
