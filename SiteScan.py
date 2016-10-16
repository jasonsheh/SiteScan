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
        self.version = '0.10'

    def usage(self):
        print("Usage:%s [-h|-u|-c] [--help|--version] -u || -c target...." % sys.argv[0])

    def run(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hu=:c=:", ["help", "version"])
            for op, value in opts:
                self.target = args[0]
                if op in ('--help', '-h'):
                    print('#' + '-'*60 + '#')
                    print('  This tool help get the basic information of one site')
                    print('\t Such as ip, build_language, server_info')
                    print('#' + '-'*60 + '#')
                    print('  -h or --help : help you know how to use this tool')
                    print('  -u : detect basic information')
                    print('  -c : crawl the site get the sitemap')
                elif op == '--version':
                    print('Current version is ' + self.version)
                elif op == '-u':
                    self.get_ip()
                    self.get_server()
                elif op == '-c':
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
            pattern_1 = re.compile(r'<a href="(.*?)"')
            res = re.findall(pattern_1, r.text)
            pattern_2 = re.compile(r'src="(.*?)"')
            res2 = re.findall(pattern_2, r.text)
            res += res2
            return res
        except Exception as e:
            print(e)
            return []

    def get_category(self, res):  # this should be used later
        res_path = []
        for url in res:
            res_path.append(urlparse(url).path)
        res_path = list(set(res_path))
        return res_path

    def get_url(self, res):
        for url in res:
            if '?' in url:
                url2 = url.split('?')[0]
                res.remove(url)
                res.append(url2)
        res = list(set(res))
        new_url = []
        for url in res:
            if url.startswith('http:') and not url.startswith(self.target):
                continue
            if '.' not in url:
                continue
            if 'javascript:' in url:
                continue
            if not url.startswith('/') and not url.startswith('http'):
                url = '/' + url
            if '/' in url and not url.startswith('http:'):
                url = self.target[:-1] + url
            if url.startswith(self.target):
                new_url.append(url)
        return new_url

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
            res = self.get_category(res)
            print(res)

            folder = []
            for url in res:
                url = url.split('/')
                for i in url:
                    j = 0
                    print('-'*j + i + '\n')
                    j += 1


        except Exception as e:
            print(e)

    '''def site_analyse(self):
        with open('')'''


def main():
    if len(sys.argv) == 1:
        print("Usage: python %s [-h|-u|-c] [--help|--version] -u||-c target...." % sys.argv[0])
        sys.exit()
    s = SiteScan()
    s.run()


if __name__ == '__main__':
    main()
