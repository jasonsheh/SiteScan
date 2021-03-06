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
from database.gitLeak import GitLeak

from lib.info.subdomain import AllDomain
from lib.info.siteinfo import SiteInfo

from lib.git.gitscan import GitScan
# from utils.mail import MyMail
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
    for site in ranges:
        # 扫描单个站点
        leaks = GitScan(site['domain']).run()
        for leak in leaks:
            already_scanned = g.select_leak(repository_name=leak["repository_name"])
            already_scanned += g.select_leak(domain=leak["domain"])

            is_scanned = False
            for scanned in already_scanned:
                if leak["code"] == scanned["code"]:
                    is_scanned = True
                    break
            if not is_scanned:
                already_scanned.append(leak)
                g.insert_leak(leak, site["domain_id"])
        # 更新扫描时间
        g.update_scan_time(site["id"])

        # TODO 发送邮件告警
        # MyMail().send_mail(leaks, "Github 信息泄露告警")
    g.clean()


if __name__ == '__main__':
    git_leak()
