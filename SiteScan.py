#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import getopt
import socket
import requests
import re
from urllib.parse import urlparse


class SiteScan:
    def __init__(self):
        self.target = ''
        self.ip = ''
        self.language = ''
        self.server = ''
        self.version = '1.0'
        self.sitemap = []

    def usage(self):
        print("Usage:%s [-h|-u|-c] [--help|--version] -u || -c target...." % sys.argv[0])

    def run(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hu=:c=:", ["help", "version"])
            for op, value in opts:
                if op in ('--help', '-h'):
                    print('#' + '-'*60 + '#')
                    print('  This tool help get the basic information of one site')
                    print('\t Such as ip, build_language, server_info')
                    print('\t\t written by Jason_Sheh')
                    print('#' + '-'*60 + '#')
                    print('  -h or --help : help you know how to use this tool')
                    print('  -u : detect basic information')
                    print('  -c : crawl the site get the sitemap')
                elif op == '--version':
                    print('Current version is ' + self.version)
                elif op == '-u':
                    self.target = args[0]
                    self.get_ip()
                    self.get_server()
                elif op == '-c':
                    self.target = args[0]
                    print('crawl may take a while please wait...')
                    self.site_crawl()
                    
        except getopt.GetoptError as e:
            print(e)
            self.usage()
            sys.exit(1)

    def get_ip(self):
        try:
            if self.target.startswith('http://'):
                self.target = self.target[7:]
            if self.target[-1:] == '/':    # ends with slash
                self.target = self.target[:-1]
            self.ip = socket.gethostbyname(self.target)  # get ip
            print(' Ip address: ' + self.ip)
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

    # almost done need improved
    def site_crawl(self):
        try:
            if not self.target.startswith('http://'):
                self.target = 'http://' + self.target
            if not self.target.endswith('/'):
                self.target += '/'

            res = self.conn(self.target)
            res = self.get_url(res)
            for url in res:
                try:
                    new_res = self.conn(url)
                except:
                    res.remove(url)
                    continue
                new_res = self.get_url(new_res)
                res += new_res
                res = list(set(res))

            self.sitemap = self.get_dir(res)
            self.site_sort()

            with open('res.txt', 'w') as file:
                for url in self.sitemap:
                    print(url)
                    file.write(url+'\n')
                file.write('\nSensitive Dict:\n')

            self.sensitive_dir()
        except Exception as e:
            print(e)

    def sensitive_dir(self):
        print('\ndetecting common sensitive dictionaries...')
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        with open('dir.txt', 'r') as dirt:
            with open('res.txt', 'a+') as file:
                for url in dirt:
                    url = self.target + url.strip()
                    r = requests.get(url)
                    if r.status_code == 200:
                        print(url)
                        file.write(url + '\n')


def main():
    if len(sys.argv) == 1:
        print("Usage: python %s [-h|-u|-c] [--help|--version] -u||-c target...." % sys.argv[0])
        sys.exit()
    s = SiteScan()
    s.run()


if __name__ == '__main__':
    main()
