#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-


from lib.sqltest import Sql
from lib.sendir import Sendir
from lib.subdomain import Domain
from lib.xss import Xss
from lib.port import Port
import sys
import getopt
import socket
import requests
import re
from urllib.parse import urlparse
import threading
import queue
import time


class SiteScan:
    def __init__(self):
        self.target = ''
        self.ip = ''
        self.language = ''
        self.server = ''
        self.version = '0.6'
        self.url_set = []
        self.sitemap = []
        self.q = queue.Queue(0)

    @staticmethod
    def usage():
        print("Usage:%s [-h|-c] [--help|--version] -h || --help target...." % sys.argv[0])

    def run(self):
        try:
            print(''' ____  _ _       ____''')
            print('''/ ___|(_) |_ ___/ ___|  ___ __ _ _ __''')
            print('''\___ \| | __/ _ \___ \ / __/ _` | '_  \\''')
            print(''' ___) | | ||  __/___) | (_| (_| | | | |''')
            print('''|____/|_|\__\___|____/ \___\__,_|_| |_|''')

            opts, args = getopt.getopt(sys.argv[1:], "hu:c:", ["help", "version"])
            for op, value in opts:
                if op in ('--help', '-h'):
                    print('\n#' + '-'*60 + '#')
                    print('  This tool help get the basic information of one site')
                    print('\t Such as ip, build_language, server_info and can find')
                    print('\t some simple vulnerabilities')
                    print('\t\t written by Jason_Sheh')
                    print('#' + '-'*60 + '#')
                    print('  -h or --help : help you know how to use this tool')
                    print('  -c : crawl the site and try to find vulnerabilities')
                elif op == '--version':
                    print('Current version is ' + self.version)
                elif op == '-c':
                    self.target = value
                    self.init()
                    self.get_ip()
                    self.get_server()
                    self.site_scan()
                    
        except getopt.GetoptError as e:
            print(e)
            self.usage()
            sys.exit(1)

    def init(self):
        if not self.target.startswith('http://') or not self.target.startswith('https://'):
            self.target = 'http://' + self.target
        if self.target.endswith('/'):
            self.target = self.target[:-1]
            # format http://example.com

    def get_ip(self):
        try:
            target = self.target[7:]
            self.ip = socket.gethostbyname(target)  # get ip address
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

    # return all url in one page
    @staticmethod
    def conn(target):  # get url in one page
        try:
            r = requests.get(target, timeout=1)
            pattern_1 = re.compile(r'href="(.*?)"')
            pattern_2 = re.compile(r'src="(.*?)"')
            res = re.findall(pattern_1, r.text)
            res += re.findall(pattern_2, r.text)
            return res
        except:
            return []

    def get_url(self, res):
        res = list(set(res))
        new_url = []
        for url in res:
            _quit = 0
            # print(url)
            if url.startswith('http') and not url.startswith(self.target):
                continue
            for i in ['javascript:', '(', '.css', '.jpg', '.png', '.pdf',
                      '.xls', '.doc', '.rar', '.ico', '.ppt', '.pptx', ':']:
                if i in url:
                    _quit = 1
                    break
            if _quit:
                continue
            if url.startswith('..'):
                url = url[2:]
            if not url.startswith('/') and not url.startswith('http:') and not url.startswith('www'):
                url = '/' + url
            if '/' in url and not url.startswith('http:'):
                url = self.target + url
            if url.startswith(self.target):
                new_url.append(url)
            # print(url)
        new_url = list(set(new_url))
        return new_url

    def crawler(self):
        while not self.q.empty():
            if self.q.qsize() != 0:
                sys.stdout.write('# 剩余爬取链接个数' + str(self.q.qsize()) + '\r')
                sys.stdout.flush()
            url = self.q.get()
            try:
                new_res = self.conn(url)
                res = self.get_url(new_res)
            except Exception as e:
                print(e)
                continue
            for i in res:
                if i not in self.url_set:
                    self.url_set.append(i)
                    # self.q.put(i)

                if ('?' in i) and (urlparse(i).path.split('?')[0] not in self.sitemap):
                    self.sitemap.append(urlparse(i).path.split('?')[0])
                    self.q.put(i)
                    # print(i)
                elif urlparse(i).path.rsplit('/', 1)[0] == '' and urlparse(i).path not in self.sitemap:
                    self.sitemap.append(urlparse(i).path)
                    self.q.put(i)
                    # print(i)
                elif urlparse(i).path.rsplit('/', 1)[0] not in self.sitemap:  # 伪静态
                    self.sitemap.append(urlparse(i).path.rsplit('/', 1)[0])
                    self.q.put(i)
                    # print(i)
                '''elif i.rsplit('/', 1)[0] not in self.sitemap:
                    self.sitemap.append(i.rsplit('/', 1)[0])
                    self.q.put(i)'''

            time.sleep(0.1)

    # almost done need improved
    def crawl(self):
        res = self.conn(self.target)
        res = self.get_url(res)
        if res == []:
            res = self.conn(self.target + '/index.php')
            res = self.get_url(res)
        for i in res:
            self.url_set.append(i)
            if ('?' in i) and (urlparse(i).path.split('?')[0] not in self.sitemap):
                self.sitemap.append(urlparse(i).path.split('?')[0])
                # print(i)
            elif urlparse(i).path.rsplit('/', 1)[0] == [] and urlparse(i).path not in self.sitemap:
                self.sitemap.append(urlparse(i).path)
                # print(i)
            elif urlparse(i).path.rsplit('/', 1)[0] not in self.sitemap:  # 伪静态
                self.sitemap.append(urlparse(i).path.rsplit('/', 1)[0])
            self.q.put(i)

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

        print('\n\n扫描链接总数:' + str(len(self.url_set)))
        print('Total time: \n' + str(t2-t1))

        self.sitemap.sort()

        print("\n目录结构")
        for url in self.sitemap:
            print(url)

        '''with open('res.txt', 'w+') as file:
            file.write('direction:\n\n')
            for url in self.sitemap:
                print(url)
                file.write(url + '\n')'''

    def site_scan(self):
        self.crawl()

        # 漏洞测试
        self.sql_test()  # here test the sql injection
        self.xss_test()
        self.sensitive_dir()
        self.port_test()
        self.sub_domain()


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

    def sub_domain(self):
        s = Domain(self.target)
        s.run()

    def sql_test(self):
        s = Sql(self.url_set)
        s.run()

    def xss_test(self):
        s = Xss(self.url_set)
        s.run()

    def port_test(self):
        s = Port(self.ip)
        s.run()


def main():
    if len(sys.argv) == 1:
        print("Usage: python %s [-h|-u|-c] [--help|--version] -u||-c target...." % sys.argv[0])
        sys.exit()
    s = SiteScan()
    s.run()


if __name__ == '__main__':
    main()
