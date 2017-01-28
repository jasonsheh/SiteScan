#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-


from lib.basicinfo import Info
from lib.crawler import Crawler
from lib.sqltest import Sql
from lib.sendir import Sendir
from lib.subdomain import Domain
from lib.xss import Xss
from lib.port import Port
import sys
import getopt
import time


class SiteScan:
    def __init__(self):
        self.target = ''
        self.ip = ''
        self.language = ''
        self.server = ''
        self.version = '1.0.1'
        self.url_set = []
        self.sitemap = []
        self.site_file = []
        self.domain = []

    @staticmethod
    def usage():
        print("Usage:%s [-h|-c] [--help|--version] -h || --help target...." % sys.argv[0])

    def run(self):
        try:
            print(''' ____  _ _       ____''')
            print('''/ ___|(_) |_ ___/ ___|  ___ __ _ _ __''')
            print('''\___ \| | __/ _ \___ \ / __/ _` | '_  \\''')
            print(''' ___) | | ||  __/___) | (_| (_| | | | |''')
            print('''|____/|_|\__\___|____/ \___\__,_|_| |_|\t\t''' + self.version)

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
                    self.site_scan()
                    
        except getopt.GetoptError as e:
            print(e)
            self.usage()
            sys.exit(1)

    def init(self):
        if (not self.target.startswith('http://')) and (not self.target.startswith('https://')):
            self.target = 'http://' + self.target
        if self.target.endswith('/'):
            self.target = self.target[:-1]

        # format http://example.com

    def site_scan(self):
        t1 = time.time()
        self.basic_info()
        self.site_crawl()

        # 漏洞测试
        self.sql_test()  # here test the sql injection
        self.xss_test()
        self.sensitive_dir()
        self.port_test()
        self.sub_domain()

        t2 = time.time()
        print('\nTotal time: ' + str(t2 - t1))

    def basic_info(self):
        s = Info(self.target)
        self.ip, self.language, self.server = s.run()

    def site_crawl(self):
        s = Crawler(self.target)
        self.url_set, self.sitemap = s.run()

    def sensitive_dir(self):
        s = Sendir(self.target)
        s.run()

    def sub_domain(self):
        s = Domain(self.target)
        self.domain = s.run()

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
        print("Usage: python %s [-h|-u|-c] [--help|--version] -c target...." % sys.argv[0])
        sys.exit()
    s = SiteScan()
    s.run()


if __name__ == '__main__':
    main()
