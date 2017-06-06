#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import requests
import threading
import queue
import time
from database.database import Database


class Sendir:
    def __init__(self, target):
        self.target = target
        self.q = queue.Queue(0)
        self.thread_num = 3
        self.sensitive = []
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}

    def dirt(self):
        while not self.q.empty():
            try:
                _dir = self.q.get()
                url = self.target + _dir
                r = requests.get(url, timeout=2, allow_redirects=False)

                if r.status_code in [200, 403]:
                    self.sensitive.append(url)

                time.sleep(0.1)
            except:
                continue

    def run(self):
        try:
            print('\n# 检测敏感目录...')

            with open('/home/jasonsheh/Tools/python/SiteScan/dict/dir.txt', 'r') as file:
                for eachline in file:
                    self.q.put(eachline.strip())

            threads = []
            for i in range(int(self.thread_num)):
                t = threading.Thread(target=self.dirt)
                threads.append(t)
            for item in threads:
                item.start()
            for item in threads:
                item.join()

            if len(self.sensitive) < 20:
                for url in self.sensitive:
                    print(url)
            Database().insert_sendir(self.sensitive)
            return self.sensitive
        except Exception as e:
            print(e)
            return self.sensitive


def main():
    Sendir(target='http://dkxy.jit.edu.cn').run()

if __name__ == '__main__':
    main()
