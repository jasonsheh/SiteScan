#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import json
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
        self.thread_num = 10
        self.ip = []
        self.domain = []
        self.domains = {}

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
        self.ilink()
        if not self.domain:
            self.chaxunla()
        elif not self.domain or len(self.domain) < 3:
            self.brute()
        self.get_ip()
        return self.domains

    def ilink(self):
        print('\nilink子域名查询')
        url = 'http://i.links.cn/subdomain/'
        data = {'domain': self.target, 'b2': '1', 'b3': '1', 'b4': '1'}
        try:
            r = requests.post(url, data=data)
            pattern = re.compile('<div class=domain><input.*?value="(.*?)">')
            self.domain = re.findall(pattern, r.text)
            '''for domain in self.domain:
                print(domain)'''
        except requests.exceptions.ConnectionError:
            self.domain = []

    def chaxunla(self):
        print('\nchaxunla子域名查询')
        url = 'http://api.chaxun.la/toolsAPI/getdomain/'
        data = {'k': 'www.' + self.target, 'action': 'moreson'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        r = requests.post(url, data=data, headers=headers)
        url = json.loads(r.text)
        if url['status'] == 0:
            print('域名流量太小或者域名错误')
            self.domain = []
        elif url['status'] == 3:
            print('请求次数过多')
            self.domain = []
        else:
            list = url['data']
            for domain in list:
                self.domain.append('http://'+domain['domain'])

    def brute(self):
        t1 = time.time()
        try:
            print('\n子域名爆破...')
            with open('./dict/domain.txt', 'r') as dirt:
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

        except KeyboardInterrupt as e:
            print('\n')
            print(e)

        t2 = time.time()

        print('\nTotal time: ' + str(t2 - t1) + '\n')

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

    def get_ip(self):
        for domain in self.domain:
            try:
                if domain.startswith('http://'):
                    ip = socket.gethostbyname(domain[7:])
                else:
                    ip = socket.gethostbyname(domain)
                self.domains[domain] = ip
            except:
                continue

        for domain, ip in self.domains.items():
            print(domain+': '+ip)


def main():
    s = Domain(target="www.xyhcms.com")
    domain = s.run()
    return domain

if __name__ == '__main__':
    main()
