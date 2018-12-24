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
import time


from database.srcList import SrcList
from database.database import Database
from database.gitLeak import GitLeak

from lib.info.subdomain import AllDomain
from lib.info.siteinfo import SiteInfo
from lib.info.sendir import SenDir

from lib.poc.common.xss import Xss
from lib.poc.common.sqli import SqlInjection
from lib.poc.common.struts2 import Struts2

from lib.git.gitscan import GitScan
from lib.crawler import Crawler

from setting import sudomain_scan_size, github_scan_size


class SRCKiller:
    def info_collect(self):
        for domain in SrcList().select_un_scan_src_list(sudomain_scan_size):
            src_id = domain['src_id']
            domain_id = domain['id']
            url = domain['url']
            domain = domain['url'][2:]

            domains = AllDomain(domain).run()

            print(len(domains.keys()))

            info = SiteInfo([x for x in domains.keys()]).run()
            Database().insert_subdomain(domains, info, domain_id, src_id)
            SrcList().update_scan_time(url)

    def git_leak(self):
        ranges = GitLeak().select_range(count=github_scan_size)

        g = GitLeak()
        for _ in ranges:
            leaks = GitScan(_['domain']).run()

            already_scanned = GitLeak().select_leak()

            for leak in leaks:
                # 是否已在库中
                is_scanned = False
                for scanned in already_scanned:
                    if leak["code"] == scanned["code"]:
                        is_scanned = True
                        break
                if not is_scanned:
                    g.insert_leak(leak, _["domain_id"], -1)
            # 更新扫描时间
            g.update_scan_time(_["id"])

            time.sleep(5)
        g.clean()


if __name__ == '__main__':
    SRCKiller().git_leak()
