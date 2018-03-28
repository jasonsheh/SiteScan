#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import json
import dns.resolver
import sys
import requests
import time
import socket
import re
from multiprocessing import Pool, Process
import gipc
import gevent
from gevent.queue import Queue
from gevent import monkey
monkey.patch_all()

'''
from database.database import Database
'''
from setting import user_path


class Domain(object):
    def __init__(self, target, id=''):
        self.target = target
        self.id = id
        self.ip = []
        self.dns_ip = ['1.1.1.1', '127.0.0.1', '0.0.0.0', '202.102.110.203', '202.102.110.204',
                       '220.250.64.225']
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        self.queue = Queue()
        self.thread_num = 200
        self.c_count = {}
        self.domain = []
        self.domains = {}
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

    # def output(self, total_time):
    #     for url, ips in sorted(self.domains.items()):
    #         print(url + ':\t' + self.title[url])
    #         for ip in ips:
    #             print('\t' + ip)
    #     print(total_time)

    # def save2file(self):
    #     with open(user_path+'./result/'+self.target+'.txt', 'w', encoding='utf-8') as file:
    #         for url, ips in sorted(self.domains.items()):
    #             file.writelines(url + ':\t' + self.title[url] + '\n')
    #             for ip in ips:
    #                 file.writelines('\t' + ip + '\n')

    def run_clean(self):
        print('\n清除无法访问子域名')
        self.enqueue_domain()
        self.removed_domains = []
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
                r = requests.get('http://' + domain, timeout=2, allow_redirects=False)
                if r.status_code in [400, 403, 500]:
                    self.removed_domains.append(domain)
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
        self.thread_num = 200
        self.process_num = 4
        self.dns = ['223.5.5.5', '223.6.6.6', '119.29.29.29', '182.254.116.116', '114.114.114.114', '114.114.115.115',
                    '123.125.81.6', '114.114.114.119', '114.114.115.119', '180.76.76.76']

    def domain_dict(self):
        with open(user_path + '/dict/domain.txt', 'r') as dirt:
            for i in dirt:
                self.queue.put_nowait(i.strip())

    def sub_domain_dict(self):
        with open(user_path + '/dict/sub_domain.txt', 'r') as dirt:
            for i in dirt:
                for domain in self.domain:
                    self.queue.put_nowait(i.strip()+'.'+domain)

    def sub_domian(self):
        for domain in self.domain:
            self.queue.put_nowait(domain)

    def remove_error_subdomain(self, d):
        while not self.queue.empty():
            domain = self.queue.get()
            domain = 'this_subdomain_will_never_exist' + '.' + domain
            resolvers = dns.resolver.Resolver(configure=False)
            resolvers.nameservers = [self.dns[d % len(self.dns)]]
            resolvers.timeout = 4.0
            try:
                answers = dns.resolver.query(domain)
                ips = [answer.address for answer in answers]
                for ip in ips:
                    if ip in self.dns_ip:
                        continue
                    self.removed_domains.append(domain)
            except dns.resolver.NXDOMAIN:
                pass
            except dns.resolver.NoAnswer:
                pass
            except dns.exception.Timeout:
                pass
            except:
                pass

    def run_brute(self):
        print('\n子域名爆破...')
        self.domain_dict()
        self.add_local_error_dns()
        self._brute()

        # 第一次移除错误域名
        self.domain = list(set([x for x in self.domains.keys()]))
        threads = [gevent.spawn(self.remove_error_subdomain, d) for d in range(int(self.thread_num / 2))]
        gevent.joinall(threads)
        for domain in self.removed_domains:
            self.domain.remove(domain)

        print('\n二级子域名爆破...')
        self.sub_domain_dict()
        threads = [gevent.spawn(self.sub_brute, d) for d in range(self.thread_num)]
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

    def add_local_error_dns(self):
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

    def _multiprocess_brute(self):
        print('多进程测试')
        p = Pool(self.thread_num)
        for _ in [gevent.spawn(self.gevent_brute, d) for d in range(self.thread_num)]:
            p.apply_async(_)
        p.join()

    def multiprocess_brute(self):
        all_process = []
        for _ in range(self.process_num):
            p = Process(target=self._multiprocess_brute)
            all_process.append(p)
            p.start()
        for p in all_process:
            p.join()

    def gipc_brute(self):
        print('gipc多进程测试')
        for _ in range(self.process_num):
            g = gipc.start_process(self._brute)
            g.join()

    def _brute(self):
        threads = [gevent.spawn(self.gevent_brute, d) for d in range(self.thread_num)]
        gevent.joinall(threads)

    def gevent_brute(self, d):
        while not self.queue.empty():
            sub = self.queue.get()
            domain = sub + '.' + self.target
            resolvers = dns.resolver.Resolver(configure=False)
            resolvers.nameservers = [self.dns[d % len(self.dns)]]
            resolvers.lifetime = resolvers.timeout = 4.0
            try:
                answers = resolvers.query(domain)
                ips = [answer.address for answer in answers]
                for ip in ips:
                    if ip not in self.dns_ip:
                        if domain in self.domains.keys() and ip not in self.domains[domain]:
                            self.domains[domain].append(ip)
                        else:
                            self.domains[domain] = [ip]
                        sys.stdout.write('\r子域名数:'+str(len(self.domains.keys())))
                        sys.stdout.flush()
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

    def sub_brute(self, d):
        """
        多线程2级子域名扫描
        :param d:
        :return:
        """
        while not self.queue.empty():
            domain = self.queue.get()
            resolvers = dns.resolver.Resolver(configure=False)
            resolvers.nameservers = [self.dns[d % len(self.dns)]]
            resolvers.timeout = 4.0
            try:
                sys.stdout.write('\r子域名数: '+str(len(self.domains.keys()))+'剩余爆破数: '+str(self.queue.qsize()))
                sys.stdout.flush()
                answers = resolvers.query(domain)
                ips = [answer.address for answer in answers]
                for ip in ips:
                    if ip not in self.dns_ip:
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
    def __init__(self, target, id=''):
        super().__init__(target, id)

    def run_search(self):
        self.ilink()
        # self.chaxunla()
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
        print(r.text)
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
        url = 'https://www.virustotal.com/vtapi/v2/domain/report'
        params = {'apikey': '842f3920e6c5b8f15c3ab1d4b3b09b6ae2327936ccca66416e44d42d9753cda5', 'domain': self.target}
        r = requests.get(url, params=params)
        self.get_ip(r.json()['subdomains'])

    def yahoo(self):
        print('yahoo子域名查询')
        domains = []
        total_page = 20
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
        total_page = 25
        url = 'https://cn.bing.com/search?q=site:' + self.target + '&first='
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        pattern = re.compile('<cite>(.*?)</strong>')
        for page in range(0, total_page):
            r = requests.get(url + str(page*10), headers=headers)
            domains += re.findall(pattern, r.text)
        domains = list(set(domains))
        for domain in domains:
            domains[domains.index(domain)] = domain.replace('<strong>', '')

        for domain in domains:
            if domain.startswith('https://'):
                domains[domains.index(domain)] = domain.replace('https://', '')
                continue
            elif '/' in domain:
                domains[domains.index(domain)] = domain.split('/')[0]
                continue
        removed = []
        domains = list(set(domains))
        for domain in domains:
            if not domain.endswith(self.target):
                removed.append(domain)
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

        domains = list(set(domains))
        for domain in domains:
            if not domain.endswith(self.target):
                removed.append(domain)
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
        super().run_search()
        super().run_brute()
        super().run_clean()

        t2 = time.time()
        total_time = str(t2 - t1)
        # super().output(total_time)
        # super().save2file()
        return self.domains, self.target
        # Database().insert_subdomain(self.domains, self.title, self.appname, self.id)


if __name__ == '__main__':
    AllDomain('jit.edu.cn').run()
