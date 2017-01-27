#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import requests
import threading
import queue
import time


class Sendir:

    def __init__(self, target):
        self.target = target
        self.q = queue.Queue(0)
        self.thread_num = 5

    def dirt(self):
        while not self.q.empty():
            try:
                sys.stdout.write('# 剩余目录个数' + str(self.q.qsize()) + '\r')
                sys.stdout.flush()
                _dir = self.q.get()
                url = self.target + _dir
                r = requests.get(url, timeout=1, allow_redirects=False)

                if r.status_code == 200:
                    # with open('res.txt', 'w+') as file:
                        # file.write(url + '\n')
                    print(url)
                    time.sleep(0.2)
            except:
                continue

    def run(self):
        print('\n检测敏感目录...')
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        with open('dict/dir.txt', 'r') as dirt:
            for i in dirt:
                self.q.put(i.strip())

        # with open('res.txt', 'w+') as file:
            # file.write('sensitive direction:\n\n')

        try:
            threads = []
            for i in range(int(self.thread_num)):
                t = threading.Thread(target=self.dirt)
                threads.append(t)
            for item in threads:
                item.start()

            for item in threads:
                item.join()
            print('\n')
        except KeyboardInterrupt as e:
            print('\n')
            print(e)
