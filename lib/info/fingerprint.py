#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3
import re
import asyncio
from asyncio import Queue
import aiohttp
import sys
sys.path.append('C:\Code\SiteScan')

from setting import user_path


class FingerPrint:
    def __init__(self, urls):
        self.conn = sqlite3.connect(user_path + '/db/Rules.db')
        self.cursor = self.conn.cursor()
        self.targets = urls
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()
        self.queue = Queue(loop=self.loop)
        self.thread_num = 100
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        self.result = {}
        sql = 'select * from application'
        self.cursor.execute(sql)
        self.rules = self.cursor.fetchall()

    async def scan(self):
        while not self.queue.empty():
            target = await self.queue.get()
            try:
                async with aiohttp.request('GET', 'http://' + target, headers=self.headers) as r:
                    text = await r.text()
                    headers = r.headers
            except:
                continue
            await self.get_fingerprint(target, text, headers)

    async def get_fingerprint(self, target, text, headers):
        finger_print = ''
        for item in self.rules:
            app = item[1]
            rules = item[2].split(', ')
            # print(app, rule)
            for rule in rules:
                rule = rule.split(':', 1)
                place = rule[0]
                _rule = rule[1]
                if place in ['body']:
                    if -1 != text.find(_rule):
                        finger_print += app + ' '
                        break
                elif place in ['title']:
                    if re.search('<title>.*?' + _rule + '.*?</title>', text):
                        finger_print += app + ' '
                        break
                elif place in ['header', 'server']:
                    header = ''
                    for key, value in headers.items():
                        header += key + ': ' + value + ' '
                    if re.search(re.escape(_rule), header, re.I):
                        finger_print += app + ' '
                        break
                '''
                elif place in ['fullheader', 'fullbody']:
                    if -1 != r.text.find(_rule):
                        finger_print += app+' '
                        break
                    header = ''
                    for key, value in r.headers.items():
                        header += key + ': ' + value + ' '
                    if re.search(re.escape(_rule), header, re.I):
                        finger_print += app+' '
                        break
                '''
        self.result[target] = finger_print

    def run(self):
        print('服务指纹识别')
        self.conn.close()
        self.enqueue_url()
        tasks = [self.scan() for _ in range(self.thread_num)]
        self.loop.run_until_complete(asyncio.wait(tasks))
        self.loop.close()

        return self.result

    def enqueue_url(self):
        for target in self.targets:
            self.queue.put_nowait(target)


if __name__ == '__main__':
    result = FingerPrint(urls=['www.freebuf.com/', 'www.52pojie.cn', 'bbs.ichunqiu.com',
                               'www.zoomeye.org', 'octfive.cn', 'demo.typecho.cc/', 'znyywlw.jit.edu.cn']).run()
    for site, fingerprint in result.items():
        print(site)
        for fp in fingerprint.split(' '):
            print(fp)
