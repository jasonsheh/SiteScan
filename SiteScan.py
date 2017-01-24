#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import getopt
import socket
import requests
import re
from urllib.parse import urlparse
import threading
import queue
import time
from sqltest import Sql
from sendir import Sendir
from subdomain import Domain


class SiteScan:
    def __init__(self):
        self.target = ''
        self.ip = ''
        self.language = ''
        self.server = ''
        self.version = '0.6'
        self.url_set = []
        self.sitemap = []
        self.sql_in = []
        self.q = queue.Queue(0)

    @staticmethod
    def usage():
        print("Usage:%s [-h|-c] [--help|--version] -h || --help target...." % sys.argv[0])

    def run(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hu:c:", ["help", "version"])
            for op, value in opts:
                if op in ('--help', '-h'):
                    print('#' + '-'*60 + '#')
                    print('  This tool help get the basic information of one site')
                    print('\t Such as ip, build_language, server_info')
                    print('\t\t written by Jason_Sheh')
                    print('#' + '-'*60 + '#')
                    print('  -h or --help : help you know how to use this tool')
                    print('  -c : crawl the site to get the sitemap')
                elif op == '--version':
                    print('Current version is ' + self.version)
                elif op == '-c':
                    self.target = value
                    self.init()
                    self.get_ip()
                    self.get_server()
                    self.site_crawl()
                    
        except getopt.GetoptError as e:
            print(e)
            self.usage()
            sys.exit(1)

    def init(self):
        if not self.target.startswith('http://') or self.target.startswith('https://'):
            self.target = 'http://' + self.target
        if self.target.endswith('/'):
            self.target = self.target[:-1]

    def get_ip(self):
        try:
            target = self.target[7:]
            self.ip = socket.gethostbyname(target)  # get ip
            print('\n Ip address: ' + self.ip)
        except Exception as e:
            print(e)

    def get_server(self):
        try:
            r = requests.get(self.target)
            self.server = r.headers['Server']
            print(' HostName:' + self.server)
            if 'X-Powered-By' in r.headers:
                self.language = r.headers['X-Powered-By']  # get language
                print(' ' + self.language + '\n')
            else:
                print('\n')
        except Exception as e:
            print(e)

    # return all url in the page
    @staticmethod
    def conn(target):  # get url in one page
        try:
            r = requests.get(target)
            pattern_1 = re.compile(r'href="(.*?)"')
            res = re.findall(pattern_1, r.text)
            return res
        except:
            return []

    '''def get_dir(self, res):  # this should be used later
        res_path = []
        for url in res:
            res_path.append(urlparse(url).path.rsplit('/', 1)[0])
        res_path = list(set(res_path))'''

    def get_url(self, res):
        res = list(set(res))
        new_url = []
        for url in res:
            _quit = 0
            # print(url)
            if url.startswith('http') and not url.startswith(self.target):
                continue
            for i in ['javascript:', '(', '.css', '.jpg', '.png', '.pdf', '.xls', '.doc']:
                if i in url:
                    _quit = 1
                    break
            if _quit:
                continue
            if not url.startswith('/') and not url.startswith('http:') and not url.startswith('www'):
                url = '/' + url
            if '/' in url and not url.startswith('http:'):
                url = self.target + url
            if url.startswith(self.target):
                new_url.append(url)
            # print(url)
        new_url = list(set(new_url))
        return new_url

    def site_sort(self):
        for i in range(0, len(self.sitemap)):
            for j in range(i+1, len(self.sitemap)):
                if self.sitemap[i] > self.sitemap[j]:
                    temp = self.sitemap[i]
                    self.sitemap[i] = self.sitemap[j]
                    self.sitemap[j] = temp

    def crawler(self):
        while not self.q.empty():
            if self.q.qsize() != 0:
                sys.stdout.write('# 剩余爬取链接个数' + str(self.q.qsize()) + '\r')
                sys.stdout.flush()
            url = self.q.get()
            try:
                new_res = self.conn(url)
            except Exception as e:
                print(e)
                continue
            res = self.get_url(new_res)
            for i in res:
                # print(i)
                if i not in self.url_set:
                    self.url_set.append(i)
                    # self.q.put(i)
                if ('?' in i) and (i.split('?')[0] not in self.sitemap):
                    self.sitemap.append(i.split('?')[0])
                    self.q.put(i)
                    # print(i)
                elif i.rsplit('/', 1)[0] not in self.sitemap:
                    self.sitemap.append(i.rsplit('/', 1)[0])
                    self.q.put(i)
            self.url_set = list(set(self.url_set))
            self.sitemap = list(set(self.sitemap))
            time.sleep(0.1)

    # almost done need improved
    def site_crawl(self):
        res = self.conn(self.target)
        res = self.get_url(res)
        if res == []:
            res.append(self.target + '/index.php')
        for i in res:
            self.url_set.append(i)
            if ('?' in i) and (i.split('?')[0] not in self.sitemap):
                self.sitemap.append(i.split('?')[0])
                self.q.put(i)
                # print(i)
            elif i.rsplit('/', 1)[0] not in self.sitemap:
                self.sitemap.append(i.rsplit('/', 1)[0])
                self.q.put(i)
            self.q.put(i)

        # print(self.sitemap)

        t1 = time.time()

        thread_num = 5
        threads = []
        for i in range(int(thread_num)):
            t = threading.Thread(target=self.crawler)
            threads.append(t)
        for item in threads:
            item.start()

        for item in threads:
            item.join()

        t2 = time.time()

        print('\n\nTotal time: \n' + str(t2-t1))

        self.site_sort()

        print("\n目录结构")
        with open('res.txt', 'w+') as file:
            file.write('direction:\n\n')
            for url in self.sitemap:
                print(url)
                file.write(url + '\n')

        # 以下不需要多线程
        self.sqltest()  # here test the sql injection
        # self.sensitive_dir()
        self.subdomain()

    # get whois info
    # not work now
    '''def whois(self):
        if self.target.startswith('www.') or self.target.startswith('http'):
            self.init()
            url = self.target[11:]
        else:
            url = self.target
        url = 'http://whois.alexa.cn/' + url[0:-1]
        r = requests.get(url)
        try:
            pattern = re.compile(r'for detailed information(.*?)Last update of whois database')
            res = re.findall(pattern, r.text)
            # pattern = re.compile(r'<div class="fr WhLeList-right"><div class="block ball"><span>(.*?)</span>')
            print(res)
        except:
            print('查询失败')'''

    def sensitive_dir(self):
        s = Sendir(self.target)
        s.run()

    def subdomain(self):
        s = Domain(self.target)
        s.run()

    def sqltest(self):
        s = Sql(self.url_set)
        s.run()



def main():
    if len(sys.argv) == 1:
        print("Usage: python %s [-h|-u|-c] [--help|--version] -u||-c target...." % sys.argv[0])
        sys.exit()
    s = SiteScan()
    s.run()


if __name__ == '__main__':
    main()
