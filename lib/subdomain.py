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

from database.database import Database
from lib.fingerprint import FingerPrint


class Domain:
    def __init__(self, target, id=''):
        self.target = target
        self.q = queue.Queue(0)
        self.thread_num = 10
        self.ip = []
        self.dns_ip = ['1.1.1.1', '127.0.0.1', '0.0.0.0', '202.102.110.203', '202.102.110.204',
                                  '220.250.64.225']
        self.c_count = {}
        self.domain = []
        self.domains = {}
        self.title = {}
        self.appname = {}
        self.id = id

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
        self.target = self.target.strip('/')

    def run(self):
        self.init()
        # self.ilink()
        # if not self.domain:
        # self.chaxunla()
        # elif not self.domain or len(self.domain) < 3:
        self.brute()
        self.output()
        self.appname = FingerPrint([x for x in self.domains.keys()]).run()
        Database().insert_subdomain(self.domains, self.title, self.appname, self.id)
        return [x for x in self.domains.keys()], [y for x in self.domains.values() for y in x]

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
                if ip in self.domains.keys():
                    self.domains[ip].append(domain)
                    # print(domain + '\t' + ip)
                    time.sleep(0.1)
                else:
                    self.domains[ip] = [domain]
                    # print(domain + '\t' + ip)
                    time.sleep(0.1)
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
        with open('/home/jasonsheh/Tools/python/SiteScan/dict/domain.txt', 'r') as dirt:
            for i in dirt:
                self.q.put(i.strip())

    def sub_domain_dict(self):
        with open('/home/jasonsheh/Tools/python/SiteScan/dict/sub_domain.txt', 'r') as dirt:
            for i in dirt:
                self.q.put(i.strip())

    def brute(self):
        t1 = time.time()

        print('\n子域名爆破...')
        self.domain_dict()

        try:
            url = 'this_subdomain_will_never_exist' +'.' + self.target
            answers = dns.resolver.query(url)
            ips = [answer.address for answer in answers]
            for ip in ips:
                self.dns_ip.append(ip)
        except dns.resolver.NoAnswer:
            pass

        threads = []
        for i in range(int(self.thread_num)):
            t = threading.Thread(target=self._brute)
            threads.append(t)
        for item in threads:
            item.start()
        for item in threads:
            item.join()

        print('\n二级子域名爆破...')
        self.domain = list(set([x for x in self.domains.keys()]))
        self.sub_domain_dict()
        threads = []
        for i in range(int(self.thread_num)):
            t = threading.Thread(target=self.sub_brute)
            threads.append(t)
        for item in threads:
            item.start()
        for item in threads:
            item.join()

        '''
        print('\nc段扫描...')
        self.c_check()
        threads = []
        for i in range(int(self.thread_num)):
            t = threading.Thread(target=self.c_duan)
            threads.append(t)
        for item in threads:
            item.start()
        for item in threads:
            item.join()

        t2 = time.time()
        print('\nTotal time: ' + str(t2 - t1) + '\n')
        '''

        print('\n网站标题扫描')
        self.enqueue_title()
        threads = []
        for i in range(int(self.thread_num)):
            t = threading.Thread(target=self.get_title)
            threads.append(t)
        for item in threads:
            item.start()
        for item in threads:
            item.join()

        t3 = time.time()
        print('\nTotal time: ' + str(t3 - t1) + '\n')

    def _brute(self):
        while not self.q.empty():
            flag = 1
            dom = self.q.get()
            url = dom + '.' + self.target

            try:
                answers = dns.resolver.query(url)
                ips = [answer.address for answer in answers]

                for ip in ips:
                    if ip in self.dns_ip:
                        flag = 0
                        break
                if flag:
                    self.domains[url] = ips
                    print(url)
                    time.sleep(0.1)
            except:
                continue

    def sub_brute(self):
        while not self.q.empty():
            flag = 1
            dom = self.q.get()
            for target in self.domain:
                url = dom + '.' + target
                try:
                    answers = dns.resolver.query(url)
                    ips = [answer.address for answer in answers]
                    for ip in ips:
                        if ip in self.dns_ip:
                            flag = 0
                            break
                    if flag:
                        self.domains[url] = ips
                        print(url)
                        time.sleep(0.1)
                except:
                    continue

    @staticmethod
    def same_ip(ip):
        url = 'http://cn.bing.com/search?q=ip:' + ip
        r = requests.get(url)
        pattern = re.compile('<a target="_blank" href="http://(.*?)"')
        urls = re.findall(pattern, r.text)
        host = []
        for url in urls:
            if url.split('/', 1)[0] not in host:
                host.append(url.split('/', 1)[0])
        return list(set(host))

    def c_duan(self):
        while not self.q.empty():
            ip = self.q.get()
            try:
                r = requests.get('http://' + ip, timeout=3)
                domain = self.same_ip(ip)
                if domain:
                    for url in domain:
                        if url in self.domains.values():
                            self.domains[url] += ip
                            time.sleep(0.1)
                        else:
                            self.domains[url] = [ip]
                            time.sleep(0.1)

            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.ReadTimeout:
                continue

    def c_check(self):
        for ip in [y for x in self.domains.values() for y in x]:# ips
            ip = ip.rsplit('.', 1)[0]

            if ip not in self.c_count.keys():
                self.c_count[ip] = 0
            self.c_count[ip] = self.c_count[ip] + 1

        for ip, count in self.c_count.items():
            if count > 5:
                temp = []
                for _ip in [y for x in self.domains.values() for y in x]:
                    if _ip.startswith(ip):
                        temp.append(_ip.rsplit('.', 1)[1])
                _max = int(max(temp))
                _min = int(min(temp))
                for x in range(_min, _max):
                    _ip = ip + '.' + str(x)
                    self.q.put(_ip)

    def enqueue_title(self):
        for url in sorted(self.domains.keys()):
            self.q.put(url)

    def get_title(self):
        while not self.q.empty():
            url = self.q.get()
            try:
                r = requests.get('http://' + url, timeout=3)
                if not r.text:
                    self.title[url] = ''
                    continue
                if not r.encoding:
                    if re.findall('[charset]=[\'|\"](.*?)[\'|\"]', r.text, re.I | re.S):
                        r.encoding = re.findall('charset=[\'|\"](.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    elif re.findall('encoding=[\'|\"](.*?)[\'|\"]', r.text, re.I | re.S):
                        r.encoding = re.findall('encoding=[\'|\"](.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    else:
                        self.title[url] = ''
                        continue
                if re.findall('<title>(.*?)</title>', r.text, re.I | re.S) and r.encoding.split(',')[0] in ['utf-8', 'gb2312', 'GBK']:
                    self.title[url] = re.findall('<title>(.*?)</title>', r.text, re.I | re.S)[0].strip()
                elif re.findall('<title>(.*?)</title>', r.text, re.I | re.S):
                    self.title[url] = re.findall('<title>(.*?)</title>', r.text, re.I | re.S)[0].encode(r.encoding.split(',')[0]).decode('utf-8').strip()
                else:
                    self.title[url] = ''
                # print(url, self.title[url])
            except UnicodeDecodeError:
                self.title[url] = ''
                continue
            except requests.exceptions.ReadTimeout:
                self.title[url] = ''
                continue
            except requests.exceptions.ConnectionError:
                self.title[url] = ''
                continue
            except requests.exceptions.TooManyRedirects:
                self.title[url] = ''
                continue

    def output(self):
        for url, ips in sorted(self.domains.items()):
            print(url + ':\t' + self.title[url])
            for ip in ips:
                print('\t' + ip)



def main():
    Domain(target="www.njnu.edu.cn").run()

if __name__ == '__main__':
    main()
