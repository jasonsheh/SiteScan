#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import json
import dns.resolver
from urllib.parse import urlparse
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
        elif self.target.startswith('www.'):
            self.target = self.target[4:]

    def run(self):
        self.init()
        self.ilink()
        # if not self.domain:
        # self.chaxunla()
        # elif not self.domain or len(self.domain) < 3:
        self.brute()
        self.output()
        return list(set(self.domains.values()))

    def ilink(self):
        print('\nilink子域名查询')
        url = 'http://i.links.cn/subdomain/'
        data = {'domain': self.target, 'b2': '1', 'b3': '1', 'b4': '1'}
        try:
            r = requests.post(url, data=data)
            pattern = re.compile('<div class=domain><input.*?value="http://(.*?)">')
            self.domain = re.findall(pattern, r.text)
            for domain in self.domain:
                ip = socket.gethostbyname(domain)
                self.domains[ip] = domain
        except requests.exceptions.ConnectionError:
            self.domain = []
        except Exception as e:
            print(e)

    def chaxunla(self):
        print('\nchaxunla子域名查询')
        url = 'http://api.chaxun.la/toolsAPI/getdomain/'
        data = {'k': 'www.' + self.target, 'action': 'moreson'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        r = requests.post(url, data=data, headers=headers)
        url = json.loads(r.text)
        if url['status'] == 0:
            print('域名流量太小或者域名错误')
        elif url['status'] == 3:
            print('请求次数过多')
        else:
            list = url['data']
            for domain in list:
                self.domain.append(domain['domain'])

    def domain_dict(self):
        with open('D://tools/python/SiteScan/dict/domain.txt', 'r') as dirt:
            for i in dirt:
                self.q.put(i.strip())

    def sub_domain_dict(self):
        with open('D://tools/python/SiteScan/dict/sub_domain.txt', 'r') as dirt:
            for i in dirt:
                self.q.put(i.strip())

    def brute(self):
        t1 = time.time()
        try:
            print('子域名爆破...')
            self.domain_dict()
            threads = []
            for i in range(int(self.thread_num)):
                t = threading.Thread(target=self._brute)
                threads.append(t)
            for item in threads:
                item.start()
            for item in threads:
                item.join()

            '''print('二级子域名爆破...')
            self.domain = list(set(self.domains.values()))
            self.sub_domain_dict()
            threads = []
            for i in range(int(self.thread_num)):
                t = threading.Thread(target=self.sub_brute)
                threads.append(t)
            for item in threads:
                item.start()
            for item in threads:
                item.join()'''

        except KeyboardInterrupt as e:
            print('\n')
            print(e)

        t2 = time.time()

        print('\nTotal time: ' + str(t2 - t1) + '\n')

    def _brute(self):
        while not self.q.empty():
            dom = self.q.get()
            url = dom + '.' + self.target

            try:
                answers = dns.resolver.query(url)
                if answers:
                    ips = [answer.address for answer in answers]

                # r = requests.get(url, timeout=0.1, allow_redirects=False)
                # if r.status_code == 200:
                    for ip in ips:
                        if ip in ['1.1.1.1', '127.0.0.1', '0.0.0.0', '202.102.110.203', '202.102.110.204']:
                            continue
                        if ip not in self.domains.keys():
                            self.domains[ip] = url
                            # print(url + '\t' + ip)
                            time.sleep(0.1)
            except:
                continue

    def sub_brute(self):
        while not self.q.empty():
            dom = self.q.get()
            for target in self.domain:
                url = dom + '.' + target
                try:
                    answers = dns.resolver.query(url)
                    if answers:
                        ips = [answer.address for answer in answers]

                        for ip in ips:
                            if ip in ['1.1.1.1', '127.0.0.1', '0.0.0.0', '202.102.110.203', '202.102.110.204']:
                                continue
                            if ip not in self.domains.keys():
                                self.domains[ip] = url
                                # print(url + '\t' + ip)
                                time.sleep(0.1)
                except:
                    continue

    def output(self):
        for ip, url in sorted(self.domains.items()):
            print('%s:\t%s' % (url, ip))


def main():
    s = Domain(target="cqsxdb.com")
    domain = s.run()
    return domain

if __name__ == '__main__':
    main()
