#!/usr/bin/python
# __author__ = 'JasonSheh'
# __email__ = 'qq3039344@gmail.com'
# -*- coding:utf-8 -*-
# !/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3
import re
import requests
from typing import List, Dict
from setting import user_path, user_agent


class SiteInfo:
    def __init__(self, targets):
        self.conn = sqlite3.connect(user_path + '/db/Rules.db')
        self.cursor = self.conn.cursor()
        self.targets: List = targets
        self.protocol: str = 'http://'
        self.headers: Dict = {'User-Agent': user_agent}
        self.results: List = []
        sql = 'select * from fingerprint'
        self.cursor.execute(sql)
        self.rules: Dict = {}
        for item in self.cursor.fetchall():
            self.rules[item[1]] = item[2].split(', ')

        self.title_pattern = "<title.*?>(.*?)</title.*?>"
        self.encoding_pattern = "encoding=[\'|\"]?(.*?)[\'|\"]"

    def get_title(self, r):
        try:
            encoding = r.encoding
            if not r.text:
                return ''
            if not encoding:
                if re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S):
                    encoding = re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                elif re.findall(self.encoding_pattern + '?', r.text, re.I | re.S):
                    encoding = re.findall(self.encoding_pattern, r.text, re.I | re.S)[0]
                else:
                    return ''
            if encoding == 'ISO-8859-1' and re.findall(self.title_pattern, r.text, re.I | re.S):
                if re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S):
                    encoding = re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                elif re.findall(self.encoding_pattern + '?', r.text, re.I | re.S):
                    encoding = re.findall(self.encoding_pattern, r.text, re.I | re.S)[0]
                else:
                    encoding = 'utf-8'
                return re.findall(self.title_pattern, r.text, re.I | re.S)[0].encode(
                    "iso-8859-1").decode(encoding).encode('utf-8').decode('utf-8', errors='ignore')
            elif re.findall(self.title_pattern, r.text, re.I | re.S) and encoding.lower() in ['utf-8', 'gb2312',
                                                                                              'gbk2312', 'gbk']:
                return re.findall(self.title_pattern, r.text, re.I | re.S)[0].strip()
            elif re.findall(self.title_pattern, r.text, re.I | re.S):
                return re.findall(self.title_pattern, r.text, re.I | re.S)[0].encode(
                    encoding).decode('utf-8', errors='ignore').strip()
            else:
                return ''
        except AttributeError:
            return ''
        except LookupError:
            return ''

    def run(self):
        for domain in self.targets:
            result = {'domain': domain, 'title': '', 'text': '', 'headers': [], 'app': []}
            try:
                r = requests.get(self.protocol + domain, timeout=3, headers=self.headers)
            except requests.exceptions:
                return result

            result['title'] = self.get_title(r)
            result['headers'] = [{"key": k, "value": v} for k, v in r.headers.items()]
            result['text'] = r.text

            for appname, rules in self.rules.items():
                for rule in rules:
                    place, rule = rule.split(':', 1)
                    if place in ['body']:
                        if r.text.find(rule) != -1:
                            result['app'].append(appname)
                            break
                    elif place in ['title']:
                        if re.search('<title>.*?' + re.escape(rule) + '.*?</title>', r.text):
                            result['app'].append(appname)
                            break
                    elif place in ['header', 'server']:
                        header = ''
                        for key, value in r.headers.items():
                            header += key + ': ' + value + ' '
                        if re.search(re.escape(rule), header, re.I):
                            result['app'].append(appname)
                            break
            self.results.append(result)
        return self.results


if __name__ == '__main__':
    # _ = input('请输入待识别域名: ')
    for info in SiteInfo(targets=["www.baidu.com", "www.bilibili.com"]).run():
        print(info)
