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

from lib.git.gitscan import GitScan

from setting import sudomain_scan_size, github_scan_size


def info_collect():
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


def git_leak():
    ranges = GitLeak().select_range(count=github_scan_size)

    g = GitLeak()
    for _ in ranges:
        t1 = time.time()
        # 扫描单个站点
        leaks = GitScan(_['domain']).run()

        already_scanned = GitLeak().select_leak(domain_id=_["domain_id"])
        for leak in leaks:
            is_scanned = False
            for scanned in already_scanned:
                if leak["repository_name"] == scanned["repository_name"] and leak["code"].split('\n') == scanned["code"]:
                    is_scanned = True
                    break
            if not is_scanned:
                already_scanned.append(leak)
                g.insert_leak(leak, _["domain_id"], -1)
        # 更新扫描时间
        g.update_scan_time(_["id"])

        time.sleep(5)
        print(time.time() - t1)
    g.clean()


if __name__ == '__main__':
    git_leak()
