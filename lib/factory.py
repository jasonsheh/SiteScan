#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

"""
对所有脚本进行统一规划管理
"""

from lib.info.subdomain import AllDomain
from lib.info.getTitle import GetTitle
from lib.info.fingerprint import FingerPrint
from lib.info.sendir import SenDir
from lib.info.save2file import SaveToFile

from lib.crawler import Crawler

from lib.vuls.xss import Xss
from lib.vuls.sqli import Sqli

from lib.port import Port
from lib.git.gitscan import GitScan


def init(domain):
    if domain.startswith('http://www.'):
        domain = domain[11:]
    if domain.startswith('https://www.'):
        domain = domain[12:]
    if domain.startswith('http://'):
        domain = domain[7:]
    if domain.startswith('https://'):
        domain = domain[8:]
    if domain.startswith('www.'):
        domain = domain[4:]
    if domain.endswith('/'):
        domain = domain[:-1]
    return domain


def info_collect(domain):
    """
    信息收集
    """
    # id = Database().insert_task(domain)
    domains, target = AllDomain(domain).run()
    title = GetTitle([x for x in domains.keys()]).run()
    fingerprint = FingerPrint([x for x in domains.keys()]).run()
    dirs = SenDir([x for x in domains.keys()]).run()
    SaveToFile(target, domains, title, fingerprint, dirs).save()


def vul_scan(domain):
    """
    漏洞扫描
    """
    urls = Crawler(target=domain, dynamic=1).run()
    Xss(targets=urls).scan()
    Sqli(targets=urls).scan()


def git_scan(keyword):
    GitScan(keyword)
