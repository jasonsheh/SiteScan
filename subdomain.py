#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import requests
import threading
import queue
import time
import socket


class Domain:
    def __init__(self, target):
        self.target = target
        self.q = queue.Queue(0)
        self.thread_num = 10

    def init(self):
        if self.target.startswith('http://www.'):
            self.target = self.target[11:]
        elif self.target.startswith('https://www.'):
            self.target = self.target[12:]
        elif self.target.startswith('http://'):
            self.target = self.target[7:]
        elif self.target.startswith('https://'):
            self.target = self.target[8:]
        print(self.target)

    def run(self):
        self.init()

        print('\n子域名爆破...')
        with open('domain.txt', 'r') as dirt:
            for i in dirt:
                self.q.put(i.strip())

        t1 = time.time()

        try:
            threads = []
            for i in range(int(self.thread_num)):
                t = threading.Thread(target=self.domain)
                threads.append(t)
            for item in threads:
                item.start()

            for item in threads:
                item.join()

            print('\n')

        except KeyboardInterrupt as e:
            print('\n')
            print(e)

        t2 = time.time()

        print('\nTotal time: \n' + str(t2 - t1))

    def domain(self):
        while not self.q.empty():
            dom = self.q.get()
            url = dom + '.' + self.target
            sys.stdout.write('# 剩余子域名个数' + str(self.q.qsize()) + '\r')
            sys.stdout.flush()
            try:
                ip = socket.gethostbyname(url)
                # r = requests.get(url, timeout=0.1, allow_redirects=False)
                # if r.status_code == 200:
                print(url + '\t'+ip)
            except:
                pass

