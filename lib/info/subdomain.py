#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from gevent.queue import Queue
from gevent import monkey

monkey.patch_all()

import dns.resolver
import sys
import requests
import time
import socket
import re
import gevent

from typing import List, Dict
from utils.timer import timer
from setting import user_path, user_agent, vt_api_key, subdomain_thread_num


class Domain(object):
    def __init__(self, target, info_id=0):
        self.info_id: int = info_id
        self.target: str = target
        self.thread_num: int = subdomain_thread_num
        self.ip: List = []
        self.error_ip: List = []
        self.headers: Dict = {'User-Agent': user_agent}
        self.removed_prefix: List = ['http://www.', 'https://www.', 'https://', 'https://', 'www.']
        self.queue = Queue()
        self.c_count = {}
        self.domain = []
        self.domains = {}
        self.removed_domains = []

    def output(self):
        print("\n")
        for url, ips in sorted(self.domains.items()):
            print(url)
            print(ips)


class BruteDomain(Domain):
    def __init__(self, target, info_id=0):
        super().__init__(target, info_id)
        self.dns = ['119.29.29.29', '119.28.28.28', '223.5.5.5', '223.6.6.6', '182.254.116.116', '114.114.114.114',
                    '114.114.115.115', '114.114.114.119', '114.114.115.119', '180.76.76.76']

    def domain_dict(self):
        with open(user_path + '/dict/domain_full.txt', 'r') as dicts:
            for i in dicts:
                self.queue.put_nowait(i.strip())

    def sub_domain_dict(self):
        with open(user_path + '/dict/sub_domain.txt', 'r') as dicts:
            for i in dicts:
                for domain in self.domain:
                    self.queue.put_nowait('{}.{}'.format(i.strip(), domain))

    def sub_domain(self):
        for domain in self.domain:
            self.queue.put_nowait(domain)

    def remove_error_subdomain(self, dns_number):
        while not self.queue.empty():
            domain = self.queue.get()
            error_domain = 'this_subdomain_will_never_exist.{}'.format(domain)
            resolvers = dns.resolver.Resolver(configure=False)
            resolvers.nameservers = [self.dns[dns_number % len(self.dns)]]
            resolvers.timeout = 4.0
            try:
                answers = dns.resolver.query(error_domain)
                ips = [answer.address for answer in answers]
                for ip in ips:
                    if ip in self.error_ip:
                        continue
                    self.removed_domains.append(domain)
                    break
            except dns.resolver.NXDOMAIN:
                pass
            except dns.resolver.NoAnswer:
                pass
            except dns.exception.Timeout:
                pass

    def add_local_error_dns(self, domain):
        try:
            url = 'this_subdomain_will_never_exist.{}'.format(domain)
            answers = dns.resolver.query(url)
            ips = [answer.address for answer in answers]
            for ip in ips:
                self.error_ip.append(ip)
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.NoAnswer:
            pass
        except dns.exception.Timeout:
            pass

    def run_brute(self):
        print('\n子域名爆破...')
        self.domain_dict()
        self.add_local_error_dns(self.target)
        threads = [gevent.spawn(self.gevent_brute, dns_number) for dns_number in range(self.thread_num)]
        gevent.joinall(threads)

        # 第一次移除错误域名
        self.domain = list(set([x for x in self.domains.keys()]))
        self.sub_domain()
        threads = [gevent.spawn(self.remove_error_subdomain, dns_number) for dns_number in
                   range(int(self.thread_num / 5))]
        gevent.joinall(threads)
        for domain in self.removed_domains:
            self.domain.remove(domain)

        print('\n二级子域名爆破...')
        self.sub_domain_dict()
        threads = [gevent.spawn(self.sub_brute, dns_number) for dns_number in range(self.thread_num)]
        gevent.joinall(threads)

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

    def gevent_brute(self, dns_number):
        while not self.queue.empty():
            sub = self.queue.get()
            domain = sub + '.' + self.target
            resolvers = dns.resolver.Resolver(configure=False)
            resolvers.nameservers = [self.dns[dns_number % len(self.dns)]]
            resolvers.lifetime = resolvers.timeout = 4.0
            try:
                sys.stdout.write('\r子域名数: ' + str(len(self.domains.keys())) + '剩余爆破数: ' + str(self.queue.qsize()))
                sys.stdout.flush()
                answers = resolvers.query(domain)
                ips = [answer.address for answer in answers]
                for ip in ips:
                    if ip not in self.error_ip:
                        if domain in self.domains.keys() and ip not in self.domains[domain]:
                            self.domains[domain].append(ip)
                        else:
                            self.domains[domain] = [ip]
            except dns.resolver.NXDOMAIN:
                continue
            except dns.resolver.NoAnswer:
                continue
            except dns.name.EmptyLabel:
                continue
            except dns.exception.Timeout:
                continue
            except Exception as e:
                print(e)
                continue

    def sub_brute(self, dns_number):
        """
        多线程2级子域名扫描
        :param dns_number:
        :return:
        """
        while not self.queue.empty():
            domain = self.queue.get()
            resolvers = dns.resolver.Resolver(configure=False)
            resolvers.nameservers = [self.dns[dns_number % len(self.dns)]]
            resolvers.timeout = 4.0
            try:
                sys.stdout.write('\r子域名数: ' + str(len(self.domains.keys())) + '剩余爆破数: ' + str(self.queue.qsize()))
                sys.stdout.flush()
                answers = resolvers.query(domain)
                ips = [answer.address for answer in answers]
                for ip in ips:
                    if ip not in self.error_ip:
                        if domain in self.domains.keys() and ip not in self.domains[domain]:
                            self.domains[domain].append(ip)
                        else:
                            self.domains[domain] = [ip]
            except dns.resolver.NXDOMAIN:
                continue
            except dns.resolver.NoAnswer:
                continue
            except dns.name.EmptyLabel:
                continue
            except dns.exception.Timeout:
                continue
            except dns.resolver.NoNameservers:
                continue


class SearchDomain(Domain):
    # 从搜索引擎或api中获取子域名
    def __init__(self, target, info_id=''):
        super().__init__(target, info_id)
        self.search_depth: int = 15

    def run_search(self):
        self.ilink()
        self.crt_sh()
        self.virustotal()
        self.baidu()
        self.bing()
        self.so360()

        self.remove_spread_record()

    def get_ip(self, domains):
        for domain in domains:
            try:
                if domain not in self.domains.keys():
                    ip = socket.gethostbyname(domain)
                    self.domains[domain] = [ip]
                else:
                    continue
            except socket.gaierror:
                continue

    def ilink(self):
        print('ilink子域名查询')
        url: str = 'http://i.links.cn/subdomain/'
        data: Dict = {'domain': self.target, 'b2': '1', 'b3': '1', 'b4': '1'}
        try:
            r = requests.post(url, data=data, headers=self.headers)
            pattern = re.compile('<div class=domain><input.*?value="http://(.*?)">')
            domains = re.findall(pattern, r.text)
            self.get_ip(domains)
        except requests.exceptions.ConnectionError:
            self.domains = {}

    def crt_sh(self):
        print('crt.sh子域名查询')
        url = 'https://crt.sh/?q=%.{}'.format(self.target)
        try:
            r = requests.get(url)
            pattern = re.compile("<TD>(.*?" + self.target + ")</TD>")
            text = r.text.replace('*.', '')
            domains = re.findall(pattern, text)
            domains = list(set(domains))
            self.get_ip(domains)
        except requests.exceptions.ConnectionError:
            pass

    def virustotal(self):
        print('virustotal子域名查询')
        url = 'https://www.virustotal.com/vtapi/v2/domain/report'
        params = {'apikey': vt_api_key, 'domain': self.target}
        r = requests.get(url, params=params)
        self.get_ip(r.json()['subdomains'])

    def baidu(self):
        print('Baidu子域名查询')
        domains = []
        url = 'http://www.baidu.com/s?wd=site:{}&pn='.format(self.target)
        pattern = re.compile('<a.*?class="c-showurl".*?>(.*?)/&nbsp;</a>')
        for page in range(1, self.search_depth):
            r = requests.get(url + str(page), headers=self.headers)
            domains += re.findall(pattern, r.text)

        domains = self.remove_irrelevant_domain(domains)
        self.get_ip(domains)

    def bing(self):
        print('Bing子域名查询')
        domains = []
        url = 'https://cn.bing.com/search?q=site:{}&first='.format(self.target)
        pattern = re.compile('<cite>(.*?)</strong>')
        for page in range(0, self.search_depth):
            try:
                r = requests.get(url + str(page * 10), headers=self.headers)
                domains += re.findall(pattern, r.text)
            except requests.exceptions.ChunkedEncodingError:
                continue
        for domain in domains:
            domains[domains.index(domain)] = domain.replace('<strong>', '')

        domains = self.remove_irrelevant_domain(domains)
        self.get_ip(domains)

    def so360(self):
        print('360搜索子域名查询')
        domains = []
        url = 'https://www.so.com/s?q=site:{}&pn='.format(self.target)
        pattern = re.compile('<cite>(.*?)</cite>')
        for page in range(0, self.search_depth):
            r = requests.get(url + str(page), headers=self.headers)
            domains += re.findall(pattern, r.text)

        domains = self.remove_irrelevant_domain(domains)
        self.get_ip(domains)

    def remove_spread_record(self):
        need_to_be_removed = []
        for domain in self.domains.keys():
            if len(domain.replace(self.target, '').split('.')) > 2:
                _domain = 'this_subdomain_will_never_exist' + '.' + domain.split('.', 1)[1]
                try:
                    socket.gethostbyname(_domain)
                    need_to_be_removed.append(domain)
                except socket.gaierror:
                    continue
        for domain in need_to_be_removed:
            self.domains.pop(domain)

    def remove_irrelevant_domain(self, domains):
        _ = []
        domains = list(set(domains))
        for domain in domains:
            if domain.endswith(self.target):
                _.append(domain)
        return _

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
        while not self.queue.empty():
            ip = self.queue.get()
            try:
                requests.get('http://' + ip, timeout=3)
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
        for ip in [y for x in self.domains.values() for y in x]:
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
                    self.queue.put(_ip)


class AllDomain(SearchDomain, BruteDomain):
    def __init__(self, target, info_id=0):
        super().__init__(target, info_id)

    @timer
    def run(self):
        super().run_search()
        super().run_brute()
        super().output()
        return self.domains


if __name__ == '__main__':
    AllDomain('bilibili.com').run()
