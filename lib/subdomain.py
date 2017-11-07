#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import json
import dns.resolver
from urllib.parse import urlparse
import sys
import requests
import threading
import time
import socket
import re
import gevent
from gevent.queue import Queue
from gevent import monkey
monkey.patch_all()

'''
from database.database import Database
from lib.fingerprint import FingerPrint
'''
sys.path.append('C:\Code\SiteScan')
from setting import user_path

from lib.fingerprint import FingerPrint


class Domain(object):
    def __init__(self, target, id=''):
        self.target = target
        self.id = id
        self.ip = []
        self.dns_ip = ['1.1.1.1', '127.0.0.1', '0.0.0.0', '202.102.110.203', '202.102.110.204',
                       '220.250.64.225']
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        self.queue = Queue()
        self.thread_num = 60
        self.c_count = {}
        self.domain = []
        self.domains = {}
        self.title = {}
        self.appname = {}
        self.removed_domains = []
        self.init()

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

    def output(self, total_time):
        for url, ips in sorted(self.domains.items()):
            print(url + ':\t' + self.title[url] + ' ' + self.appname[url])
            for ip in ips:
                print('\t' + ip)
        print(total_time)

    def run_title(self):
        print('\n网站标题扫描')
        self.enqueue_title()
        threads = [gevent.spawn(self.get_title) for _ in range(self.thread_num)]
        gevent.joinall(threads)

    def enqueue_title(self):
        for url in sorted(self.domains.keys()):
            self.queue.put_nowait(url)

    def get_title(self):
        while not self.queue.empty():
            url = self.queue.get()
            try:
                r = requests.get('http://' + url, timeout=3)
                if not r.text:
                    self.title[url] = ''
                    continue
                if not r.encoding:
                    if re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S):
                        r.encoding = re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    elif re.findall('encoding=[\'|\"]?(.*?)[\'|\"]?', r.text, re.I | re.S):
                        r.encoding = re.findall('encoding=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    else:
                        self.title[url] = ''
                        continue
                if r.encoding == 'ISO-8859-1' and re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S):
                    if re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S):
                        encoding = re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    elif re.findall('encoding=[\'|\"]?(.*?)[\'|\"]?', r.text, re.I | re.S):
                        encoding = re.findall('encoding=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    else:
                        encoding = 'utf-8'
                    self.title[url] = re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S)[0].encode("iso-8859-1").decode(encoding).encode('utf-8').decode('utf-8')
                elif re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S) and r.encoding in [
                    'utf-8', 'gb2312', 'GB2312', 'GBK', 'gbk2312', 'gbk']:
                    self.title[url] = re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S)[0].strip()
                elif re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S):
                    self.title[url] = re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S)[0].encode(r.encoding).decode('utf-8').strip()
                else:
                    self.title[url] = ''
                    # print(url, self.title[url])
            except AttributeError:
                print(url)
                continue
            except LookupError:
                self.title[url] = ''
                continue
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

    def run_clean(self):
        self.enqueue_domain()
        threads = [gevent.spawn(self.remove_error_domain) for _ in range(self.thread_num)]
        gevent.joinall(threads)

        for domain in self.removed_domains:
            self.domains.pop(domain)

    def enqueue_domain(self):
        for domain in [x for x in self.domains.keys()]:
            self.queue.put_nowait(domain)

    def remove_error_domain(self):
        while not self.queue.empty():
            domain = self.queue.get()
            try:
                r = requests.get('http://' + domain, timeout=4, allow_redirects=False)
                if r.status_code not in [400, 403, 500]:
                    continue
            except requests.exceptions.ConnectTimeout:
                self.removed_domains.append(domain)
                continue
            except requests.exceptions.ConnectionError:
                self.removed_domains.append(domain)
                continue
            except requests.exceptions.TooManyRedirects:
                self.removed_domains.append(domain)
                continue
            except requests.exceptions.ReadTimeout:
                self.removed_domains.append(domain)
                continue
            except:
                continue


class BruteDomain(Domain):
    def __init__(self, target, id=''):
        super().__init__(target, id)
        self.thread_num = 100
        self.dns = ['223.5.5.5', '223.6.6.6', '119.29.29.29', '182.254.116.116']

    def run_brute(self):
        self.brute()
        # self.output()

    def domain_dict(self):
        with open(user_path + '/dict/domain.txt', 'r') as dirt:
            for i in dirt:
                self.queue.put_nowait(i.strip())

    def sub_domain_dict(self):
        with open(user_path + '/dict/sub_domain.txt', 'r') as dirt:
            for i in dirt:
                self.queue.put_nowait(i.strip())

    def brute(self):
        print('\n子域名爆破...')
        self.domain_dict()
        try:
            url = 'this_subdomain_will_never_exist' + '.' + self.target
            answers = dns.resolver.query(url)
            ips = [answer.address for answer in answers]
            for ip in ips:
                self.dns_ip.append(ip)
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.NoAnswer:
            pass
        threads = [gevent.spawn(self._brute, d) for d in range(self.thread_num)]
        gevent.joinall(threads)

        '''
        print('\n二级子域名爆破...')
        self.domain = list(set([x for x in self.domains.keys()]))
        self.sub_domain_dict()
        threads = [gevent.spawn(self.sub_brute, d) for d in range(self.thread_num)]
        gevent.joinall(threads)

        
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

    def _brute(self, d):
        while not self.queue.empty():
            sub = self.queue.get()
            domain = sub + '.' + self.target
            resolvers = dns.resolver.Resolver(configure=False)
            resolvers.nameservers = [self.dns[d % len(self.dns)]]
            try:
                answers = resolvers.query(domain)
                ips = [answer.address for answer in answers]
                for ip in ips:
                    if ip not in self.dns_ip:
                        if domain in self.domains.keys() and ip not in self.domains[domain]:
                            self.domains[domain].append(ip)
                        else:
                            self.domains[domain] = [ip]
                        sys.stdout.write('\r'+str(len(self.domains.keys())))
                        sys.stdout.flush()
            except dns.resolver.NXDOMAIN:
                pass
            except dns.resolver.NoAnswer:
                pass
            except Exception as e:
                print(e)
                continue

    def sub_brute(self, d):
        while not self.queue.empty():
            sub = self.queue.get()
            resolvers = dns.resolver.Resolver(configure=False)
            resolvers.nameservers = [self.dns[d % len(self.dns)]]
            for target in self.domain:
                domain = sub + '.' + target
                try:
                    answers = resolvers.query(domain)
                    ips = [answer.address for answer in answers]
                    for ip in ips:
                        if ip not in self.dns_ip:
                            if domain in self.domains.keys() and ip not in self.domains[domain]:
                                self.domains[domain].append(ip)
                            else:
                                self.domains[domain] = [ip]
                    sys.stdout.write('\r子域名数: ' + str(len(self.domains.keys())))
                    sys.stdout.flush()
                except dns.resolver.NXDOMAIN:
                    pass
                except dns.resolver.NoAnswer:
                    pass
                except dns.name.EmptyLabel:
                    pass
                except Exception as e:
                    print(e)
                    pass


class SearchDomain(Domain):
    def __init__(self, target, id=''):
        super().__init__(target, id)

    def run_search(self):
        self.ilink()
        self.chaxunla()
        # self.threatcrowd()
        self.virustotal()
        self.yahoo()
        self.baidu()
        self.bing()
        self.so360()

        self.remove_spread_record()
        # print(self.domains)
        return self.domains

    def get_ip(self, domains):
        for domain in domains:
            try:
                ip = socket.gethostbyname(domain)
                if domain in self.domains.keys() and ip not in self.domains[domain]:
                    self.domains[domain].append(ip)
                else:
                    self.domains[domain] = [ip]
            except socket.gaierror:
                continue

    def ilink(self):
        print('ilink子域名查询')
        url = 'http://i.links.cn/subdomain/'
        data = {'domain': self.target, 'b2': '1', 'b3': '1', 'b4': '1'}
        try:
            r = requests.post(url, data=data)
            pattern = re.compile('<div class=domain><input.*?value="http://(.*?)">')
            domains = re.findall(pattern, r.text)
            self.get_ip(domains)
        except requests.exceptions.ConnectionError:
            self.domains = {}

    def chaxunla(self):
        print('chaxunla子域名查询')
        url = 'http://api.chaxun.la/toolsAPI/getdomain/'
        data = {'k': 'www.' + self.target, 'action': 'moreson'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        r = requests.post(url, data=data, headers=headers)
        url = json.loads(r.text)
        if url['status'] == 0:
            print('\t域名流量太小或者域名错误')
        elif url['status'] == 3:
            print('\t请求次数过多')
        else:
            list = url['data']
            for domain in list:
                try:
                    ip = socket.gethostbyname(domain['domain'])
                    if domain['domain'] in self.domains.keys() and ip not in self.domains[domain['domain']]:
                        self.domains[domain['domain']].append(ip)
                    else:
                        self.domains[domain['domain']] = [ip]
                except socket.gaierror:
                    continue

    def threatcrowd(self):
        print('threatcrowd子域名查询')
        url = 'https://www.threatcrowd.org/searchApi/v2/domain/report/'
        params = {'domain': self.target}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        r = requests.get(url, params=params, headers=headers)
        self.get_ip(r.json()['subdomains'])

    def virustotal(self):
        print('virustotal子域名查询')
        url = 'http://www.virustotal.com/vtapi/v2/domain/report'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        params = {'apikey': '842f3920e6c5b8f15c3ab1d4b3b09b6ae2327936ccca66416e44d42d9753cda5', 'domain': self.target}
        r = requests.get(url, params=params, headers=headers)
        self.get_ip(r.json()['subdomains'])

    def yahoo(self):
        print('yahoo子域名查询')
        domains = []
        total_page = 30
        url = 'https://search.yahoo.com/search?p = site:' + self.target + '&pz=10&b='
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        pattern = re.compile('<span class=" fz-ms fw-m fc-12th wr-bw lh-17">(.*?)</b>')
        for page in range(1, total_page):
            r = requests.get(url + str(page+1), headers=headers)
            domains += re.findall(pattern, r.text)
        domains = list(set(domains))
        removed = []
        for domain in domains:
            domains[domains.index(domain)] = domain.replace('<b>', '')

        for domain in domains:
            if '/' in domain:
                domains[domains.index(domain)] = domain.split('/')[0]
                continue
            if not domain.endswith(self.target):
                removed.append(domain)
        domains = list(set(domains))
        for remove in removed:
            domains.remove(remove)

        self.get_ip(domains)

    def baidu(self):
        print('baidu子域名查询')
        domains = []
        total_page = 30
        url = 'http://www.baidu.com/s?wd=site:'+self.target+'&pn='
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        pattern = re.compile('<a.*?class="c-showurl".*?>(.*?)/&nbsp;</a>')
        for page in range(1, total_page):
            r = requests.get(url+str(page), headers=headers)
            domains += re.findall(pattern, r.text)
        domains = list(set(domains))
        removed = []
        for domain in domains:
            if domain.startswith('https://'):
                domains[domains.index(domain)] = domain.replace('https://', '')
                continue
            elif '/' in domain:
                domains[domains.index(domain)] = domain.split('/')[0]
                continue
            if not domain.endswith(self.target):
                removed.append(domain)
        domains = list(set(domains))
        for remove in removed:
            domains.remove(remove)

        self.get_ip(domains)

    def bing(self):
        print('bing子域名查询')
        domains = []
        total_page = 30
        url = 'https://cn.bing.com/search?q=site:' + self.target + '&first='
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        pattern = re.compile('<cite>(.*?)</strong>')
        for page in range(0, total_page):
            r = requests.get(url + str(page*10), headers=headers)
            domains += re.findall(pattern, r.text)
        domains = list(set(domains))
        removed = []
        for domain in domains:
            domains[domains.index(domain)] = domain.replace('<strong>', '')

        for domain in domains:
            if domain.startswith('https://'):
                domains[domains.index(domain)] = domain.replace('https://', '')
                continue
            elif '/' in domain:
                domains[domains.index(domain)] = domain.split('/')[0]
                continue

        for domain in domains:
            if not domain.endswith(self.target):
                removed.append(domain)
        domains = list(set(domains))
        for remove in removed:
            domains.remove(remove)

        self.get_ip(domains)

    def so360(self):
        print('360搜索子域名查询')
        domains = []
        total_page = 10
        url = 'https://www.so.com/s?q=site:' + self.target + '&pn='
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        pattern = re.compile('<cite>(.*?)</cite>')
        for page in range(0, total_page):
            r = requests.get(url + str(page), headers=headers)
            domains += re.findall(pattern, r.text)
        domains = list(set(domains))
        removed = []

        for domain in domains:
            if domain.startswith('https://'):
                domains[domains.index(domain)] = domain.replace('https://', '')
                continue
            elif '/' in domain:
                domains[domains.index(domain)] = domain.split('/')[0]
                continue

        for domain in domains:
            if not domain.endswith(self.target):
                removed.append(domain)
        domains = list(set(domains))
        for remove in removed:
            domains.remove(remove)

        self.get_ip(domains)

    def remove_spread_record(self):
        need_to_be_removed = []
        for domain in self.domains.keys():
            if len(domain.replace(self.target, '').split('.')) > 2:
                _domain = 'this_subdomain_will_never_exist'+'.'+domain.split('.', 1)[1]
                try:
                    socket.gethostbyname(_domain)
                    need_to_be_removed.append(domain)
                except socket.gaierror:
                    continue
        for domain in need_to_be_removed:
            self.domains.pop(domain)

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


class AllDomain(SearchDomain, BruteDomain):
    def __init__(self, target, id=''):
        super().__init__(target, id)

    def run(self):
        t1 = time.time()
        # super().run_search()
        super().run_brute()
        super().run_title()
        super().run_clean()
        self.appname = FingerPrint([x for x in self.domains.keys()]).run()

        t2 = time.time()
        total_time = str(t2 - t1)
        super().output(total_time)
        return self.domains
        # Database().insert_subdomain(self.domains, self.title, self.appname, self.id)


if __name__ == '__main__':
    AllDomain('www.jit.edu.cn').run()
