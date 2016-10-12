#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import getopt
import socket
import requests
import re


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
            print('ip address: ' + self.ip)
        except Exception as e:
            print(e)

    def get_server(self):
        try:
            if not self.target.startswith('http://'):
                self.target = 'http://' + self.target
            r = requests.get(self.target)
            self.server = r.headers['Server']
            print(self.server)
            if 'X-Powered-By' in r.headers:
                self.language = r.headers['X-Powered-By']  # get language
                print(self.language)
        except Exception as e:
            print(e)

    def conn(self, target):  # get url in one page
        r = requests.get(target)
        pattern = re.compile(r'<a href="(.*?)"')
        res = re.findall(pattern, r.text)
        return res

    def site_crawl(self):
        try:
            if not self.target.startswith('http://'):
                self.target = 'http://' + self.target

            res = self.conn(self.target)
            print(res)
            with open('res.txt', 'w') as file:  # get site url from main page
                for i in res:
                    if i.startswith(self.target):  # with no useless pages
                        file.write(i+'\n')  # write into file

            with open('res.txt', 'a+') as file:
                for each_line in file:
                    res = self.conn(each_line)
                    for each_url in res:
                        if each_url.startswith(self.target) and each_url not in file:  # with no useless pages
                            file.write(each_url+'\n')  # write into file
            print('finish!')
        except Exception as e:
            print(e)

    '''def site_analyse(self):
        with open('')'''


def main():
    if len(sys.argv) == 1:
        print("Usage:%s [-h|-u|-c] [--help|--version] -u||-c target...." % sys.argv[0])
        sys.exit()
    s = SiteScan()
    s.run()


if __name__ == '__main__':
    main()
