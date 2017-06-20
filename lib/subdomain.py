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
    def __init__(self, target):
        self.target = target
        self.q = queue.Queue(0)
        self.thread_num = 15
        self.ip = []
        self.c_count = {}
        self.domain = []
        self.domains = {}
        self.title = {}
        self.appname = {}

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
        self.appname = FingerPrint([y for x in self.domains.values() for y in x]).run()
        Database().insert_subdomain(self.domains, self.title, self.appname)
        return self.domains

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
        try:
            print('\n子域名爆破...')
            self.domain_dict()
            threads = []
            for i in range(int(self.thread_num)):
                t = threading.Thread(target=self._brute)
                threads.append(t)
            for item in threads:
                item.start()
            for item in threads:
                item.join()

            print('\n二级子域名爆破...')
            self.domain = list(set([y for x in self.domains.values() for y in x]))
            self.sub_domain_dict()
            threads = []
            for i in range(int(self.thread_num)):
                t = threading.Thread(target=self.sub_brute)
                threads.append(t)
            for item in threads:
                item.start()
            for item in threads:
                item.join()

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
            print('\nTotal time: ' + str(t3 - t2) + '\n')

        except KeyboardInterrupt as e:
            print('\n')
            print(e)

    def _brute(self):
        while not self.q.empty():
            dom = self.q.get()
            url = dom + '.' + self.target

            try:
                answers = dns.resolver.query(url)
                if answers:
                    ips = [answer.address for answer in answers]
                    for ip in ips:
                        if ip in ['1.1.1.1', '127.0.0.1', '0.0.0.0', '202.102.110.203', '202.102.110.204',
                                  '220.250.64.225']:
                            continue
                        if ip in self.domains.keys():
                            self.domains[ip].append(url)
                            print(url + '\t' + ip)
                            time.sleep(0.1)
                        else:
                            self.domains[ip] = [url]
                            print(url + '\t' + ip)
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
                            if ip in ['1.1.1.1', '127.0.0.1', '0.0.0.0', '202.102.110.203', '202.102.110.204',
                                      '220.250.64.225']:
                                continue
                            if ip in self.domains.keys():
                                # if len(self.domains[ip]) > 20:
                                self.domains[ip].append(url)
                                print(url + '\t' + ip)
                                time.sleep(0.1)
                            else:
                                self.domains[ip] = [url]
                                print(url + '\t' + ip)
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
                if ip in self.domains.keys():
                    self.domains[ip] += domain
                    time.sleep(0.1)
                elif not domain:
                    self.domains[ip] = [ip]
                    time.sleep(0.1)
                else:
                    self.domains[ip] = domain
                    time.sleep(0.1)
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.ReadTimeout:
                continue

    def c_check(self):
        for ip in self.domains.keys():# ips
            ip = ip.rsplit('.', 1)[0]

            if ip not in self.c_count.keys():
                self.c_count[ip] = 0
            self.c_count[ip] = self.c_count[ip] + 1

        for ip, count in self.c_count.items():
            if count > 5:
                temp = []
                for _ip in self.domains.keys():
                    if _ip.startswith(ip):
                        temp.append(_ip.rsplit('.', 1)[1])
                _max = int(max(temp))
                _min = int(min(temp))
                for x in range(_min, _max):
                    _ip = ip + '.' + str(x)
                    self.q.put(_ip)

        print(self.c_count)

    def enqueue_title(self):
        for urls in sorted(self.domains.values()):
            self.q.put(urls)

    def get_title(self):
        while not self.q.empty():
            urls = self.q.get()
            if urls:
                for url in urls:
                    try:
                        r = requests.get('http://' + url, timeout=3)
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
        for ip, urls in sorted(self.domains.items()):
            print(ip + ':')
            if urls:
                for url in urls:
                    print('\t' + url + '\t' + self.title[url])
            else:
                print('\t' + self.title[ip])


def main():
    Domain(target="www.jit.edu.cn").run()

if __name__ == '__main__':
    main()
