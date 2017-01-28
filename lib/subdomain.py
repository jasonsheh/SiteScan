#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import requests
import threading
import queue
import time
import socket
import re


class Domain:
    def __init__(self, target):
        self.target = target
        self.q = queue.Queue(0)
        self.thread_num = 15
        self.ip = []
        self.domain = []

    def init(self):
        if self.target.startswith('http://www.'):
            self.target = self.target[11:]
        elif self.target.startswith('https://www.'):
            self.target = self.target[12:]
        elif self.target.startswith('http://'):
            self.target = self.target[7:]
        elif self.target.startswith('https://'):
            self.target = self.target[8:]

    def run(self):
        self.init()
        print('\ni.links.cn子域名查询')
        self.search()
        if not self.domain:
            self.brute()
        return self.domain

    def search(self):
        url = 'http://i.links.cn/subdomain/'
        data = {'domain': self.target, 'b2': '1', 'b3': '1', 'b4': '1'}
        r = requests.post(url, data=data)
        pattern = re.compile('<div class=domain><input.*?value="(.*?)">')
        self.domain = re.findall(pattern, r.text)
        for domain in self.domain:
            print(domain)

    def brute(self):
        t1 = time.time()
        try:
            print('\n子域名爆破...')
            with open('dict/domain.txt', 'r') as dirt:
                for i in dirt:
                    self.q.put(i.strip())

            threads = []
            for i in range(int(self.thread_num)):
                t = threading.Thread(target=self._brute)
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

    def _brute(self):
        while not self.q.empty():
            dom = self.q.get()
            url = dom + '.' + self.target
            sys.stdout.write('# 剩余子域名个数' + str(self.q.qsize()) + '\r')
            sys.stdout.flush()
            try:
                ip = socket.gethostbyname(url)
                # A = dns.resolver.query(url)
                # r = requests.get(url, timeout=0.1, allow_redirects=False)
                # if r.status_code == 200:
                if ip not in self.ip:
                    self.ip.append(ip)
                    self.domain.append('http://'+url)
                    print(url + '\t\t'+ip)
                    time.sleep(0.1)
            except:
                continue


def main():
    target = input('请输入域名:')
    s = Domain(target)
    s.run()

if __name__ == '__main__':
    main()
