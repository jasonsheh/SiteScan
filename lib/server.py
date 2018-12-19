#!/usr/bin/python
# __author__ = 'JasonSheh'
# __email__ = 'qq3039344@gmail.com'
# -*- coding:utf-8 -*-

# !/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

"""
对所有脚本进行统一规划管理
"""

from database.srcList import SrcList
from database.database import Database

from lib.info.subdomain import AllDomain
from lib.info.siteinfo import SiteInfo
from lib.info.sendir import SenDir
from lib.info.save2file import SaveToFile

from lib.poc.common.xss import Xss
from lib.poc.common.sqli import SqlInjection
from lib.poc.common.struts2 import Struts2

from lib.tools.baidu import Baidu
from lib.git.gitscan import GitScan
from lib.crawler import Crawler


class SRCKiller:
    def __init__(self):
        self.src_scan_list = SrcList().select_un_scan_src_list()
        self.src_scan_list = [
            {'id': 155, 'name': 'bilibili bilisrc', 'src_id': 34, 'url': "*.biligame.com", 'scan_time': "2018-12-17"}]

    def info_collect(self):
        for domain in self.src_scan_list:
            src_id = domain['src_id']
            domain_id = domain['id']
            url = domain['url']
            domain = domain['url'][2:]

            domains = AllDomain(domain).run()

            print(len(domains.keys()))

            info = SiteInfo([x for x in domains.keys()]).run()
            Database().insert_subdomain(domains, info, domain_id, src_id)
            SrcList().update_scan_time(url)


def vul_scan(domain):
    """
    常见漏洞扫描
    """
    urls = Crawler(target=domain, dynamic=False).run()
    Xss(targets=urls).scan()
    SqlInjection(targets=urls).scan()
    Struts2(urls).scan()


def git_scan(keyword):
    GitScan(keyword)


if __name__ == '__main__':
    SRCKiller().info_collect()
