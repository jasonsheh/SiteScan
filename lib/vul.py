#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.subdomain import Domain

from lib.vuls.sqltest import Sql
from lib.vuls.struts2 import Struts2
from lib.vuls.xss import Xss

from database.database import Database

import re


class Vul:
    def __init__(self, urls, id=''):
        self.id = id
        self.urls = urls

    def run(self):
        urls = self.sql(self.urls)
        if urls:
            result = Sql(urls).run()
            print(result)

            Database().insert_vul(result, 'sql', self.id)

        urls = self.struts2(self.urls)
        if urls:
            result = Struts2(urls).run()
            print(result)

            Database().insert_vul(result, 'struts2', self.id)

        urls = self.xss(self.urls)
        if urls:
            result = Xss(urls).run()
            print(result)

            Database().insert_vul(result, 'xss', self.id)

    @staticmethod
    def sql(urls):
        sql_url = []
        pattern = re.compile('(.*\?.*=\d+)|(.*/\d+)')
        for target in urls:
            if re.search(pattern, target):
                sql_url.append(target)  # 获取所有可能的注入点
        return sql_url

    @staticmethod
    def struts2(urls):
        st2_url = []
        pattern = re.compile(".*?\.action.*|.*?\.do.*")
        for url in urls:
            if re.match(pattern, url):
                if '?' in url:
                    st2_url.append(url.split('?')[0])
                else:
                    st2_url.append(url)
        return st2_url

    @staticmethod
    def xss(urls):
        xss_url = urls
        return xss_url

if __name__ == '__main__':
    domains, ips = Domain('www.njutcm.edu.cn').run()
    Vul(domains).run()
