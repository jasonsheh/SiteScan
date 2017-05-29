#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.basicinfo import Info
from lib.crawler import Crawler
from lib.sqltest import Sql
from lib.sendir import Sendir
from lib.xss import Xss
from lib.struts2 import Struts2
from lib.port import Port


class SiteScan:
    def __init__(self, target):
        self.target = target
        self.ip = ''
        self.domains = {}
        self.server = ''
        self.xss = []
        self.sql = []
        self.sensitive = []
        self.url_set = []
        self.urls = []

    def init(self):
        """
        规范目标url格式
        format http://example.com
        :return:
        """
        if (not self.target.startswith('http://')) and (not self.target.startswith('https://')):
            self.target = 'http://' + self.target
        if not self.target.endswith('/'):
            self.target = self.target + '/'

        print(self.target)

        # r = requests.get(self.target)

    def site_scan(self):
        self.init()
        print('--------------------------------------------------')
        self.basic_info()
        # 漏洞测试
        self.site_crawl()
        if self.url_set:
            self.sql_test()  # here test the sql injection
            self.xss_test()
            self.struts2()
        self.sensitive_dir()
        self.port_test()

    def basic_info(self):
        s = Info(self.target)
        self.ip, self.server = s.run()

    def site_crawl(self):
        s = Crawler(self.target)
        self.url_set, self.urls = s.run()

    def sql_test(self):
        s = Sql(self.urls)
        self.sql = s.run()

    def xss_test(self):
        s = Xss(self.urls)
        self.xss = s.run()

    def struts2(self):
        s = Struts2(self.urls)
        s.run()

    def port_test(self):
        s = Port(self.ip)
        s.run()

    def sensitive_dir(self):
        s = Sendir(self.target)
        self.sensitive = s.run()
