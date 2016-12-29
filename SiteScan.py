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
from sqltest import Sql
from sendir import Sendir


class SiteScan:
    def __init__(self):
        self.target = ''
        self.ip = ''
        self.language = ''
        self.server = ''
        self.version = '0.2'
        self.url_set = []
        self.sitemap = []
        self.sql_in = []
        self.q = queue.Queue(0)

    def usage(self):
        print("Usage:%s [-h|-u|-c] [--help|--version] -h || --help target...." % sys.argv[0])

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
                    print('  -u : detect basic information')
                    print('  -c : crawl the site to get the sitemap')
                elif op == '--version':
                    print('Current version is ' + self.version)
                elif op == '-u':
                    self.target = value
                    self.get_ip()
                    self.get_server()
                elif op == '-c':
                    self.target = value
                    self.site_crawl()
                    
        except getopt.GetoptError as e:
            print(e)
            self.usage()
            sys.exit(1)

    def init(self):
        if not self.target.startswith('http://'):
            self.target = 'http://' + self.target
        if not self.target.endswith('/'):
            self.target += '/'

    def get_ip(self):
        try:
            if self.target.startswith('http://'):
                self.target = self.target[7:]
            if self.target[-1:] == '/':    # ends with slash
                self.target = self.target[:-1]
            self.ip = socket.gethostbyname(self.target)  # get ip
            print('\n Ip address: ' + self.ip)
        except Exception as e:
            print(e)

    def get_server(self):
        try:
            if not self.target.startswith('http://'):
                self.target = 'http://' + self.target
            r = requests.get(self.target)
            self.server = r.headers['Server']
            print(' HostName:' + self.server)
            if 'X-Powered-By' in r.headers:
                self.language = r.headers['X-Powered-By']  # get language
                print(' ' + self.language)
        except Exception as e:
            print(e)

    # return all url in the page
    def conn(self, target):  # get url in one page
        try:
            r = requests.get(target, timeout=1)
            pattern_1 = re.compile(r'href="(.*?)"')
            res = re.findall(pattern_1, r.text)
            pattern_2 = re.compile(r'src="(.*?)"')
            res2 = re.findall(pattern_2, r.text)
            res += res2
            return res
        except Exception as e:
            print(e)
            return []

    def get_dir(self, res):  # this should be used later
        res_path = []
        for url in res:
            res_path.append(urlparse(url).path.rsplit('/', 1)[0])
        res_path = list(set(res_path))
        return res_path

    def get_url(self, res):
        res = list(set(res))
        new_url = []
        for url in res:
            if url.startswith('http:') and not url.startswith(self.target):
                continue
            if '.' not in url:
                continue
            if 'javascript:' in url:
                continue
            if '(' in url:
                continue
            if '+' in url:
                continue
            if ' ' in url:
                continue
            if not url.startswith('/') and not url.startswith('http'):
                url = '/' + url
            if '/' in url and not url.startswith('http:'):
                url = self.target[:-1] + url
            if url.startswith(self.target):
                new_url.append(url)
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
            url = self.q.get()
            try:
                new_res = self.conn(url)
            except:
                self.q.get()
                continue
            res = list(set(self.get_url(new_res)))
            for i in res:
                if i not in self.url_set:
                    self.url_set.append(i)
                    self.q.put(i)

    # almost done need improved
    def site_crawl(self):
        print('crawl may take a while please wait...')
        thread_num = input('set the thread number:')
        self.init()
        try:
            res = self.conn(self.target)
            res = self.get_url(res)
            for i in res:
                self.url_set.append(i)
                self.q.put(i)
            list(set(self.url_set))

            threads = []
            for i in range(int(thread_num)):
                t = threading.Thread(target=self.crawler)
                threads.append(t)
            for item in threads:
                item.setDaemon(True)
                item.start()

            # 以下不需要多线程
            print("检测SQL注入:")
            self.sql_in = self.sqltest()  # here test the sql injection
            if self.sql_in == []:
                print("可能不存在注入")
            else:
                for url in self.sql_in:
                    print(url)
            self.sitemap = self.get_dir(self.url_set)
            self.site_sort()

            with open('res.txt', 'w+') as file:
                file.write('Directory\n')
                for url in self.sitemap:
                    file.write(url+'\n')

            self.sensitive_dir()
        except Exception as e:
            print(e)

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

    def get_sql_in(self):
        pattern = re.compile(self.target+'.*\?.*=.*')
        for url in self.url_set:
            res = re.findall(pattern, url)  # 获取所有可能的注入点
            if res != []:
                flag = 0
                if self.sql_in == []:
                    self.sql_in += res
                for _url in self.sql_in:
                    if urlparse(_url).path == urlparse(res[0]).path:
                        flag = 1
                        break
                if flag == 0:
                    self.sql_in += res

    def sqltest(self):
        self.get_sql_in()
        true_sql_in = []
        if self.sql_in != []:
            for sqli in self.sql_in:  # 进行注入测试
                s = Sql(sqli)
                url = s.waf_scan()
                if url:
                    true_sql_in.append(url)
        return true_sql_in


def main():
    if len(sys.argv) == 1:
        print("Usage: python %s [-h|-u|-c] [--help|--version] -u||-c target...." % sys.argv[0])
        sys.exit()
    s = SiteScan()
    s.run()


if __name__ == '__main__':
    main()
