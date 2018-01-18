#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.info.subdomain import AllDomain
from lib.info.sendir import SenDir

from lib.crawler import Crawler

from lib.vuls.xss import Xss
from lib.vuls.sqli import Sqli

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
    # id = Database().insert_task(domain)
    domains = AllDomain(domain).run()
    SenDir(domains).run()


def vul_scan(domain):
    urls = Crawler(target=domain, dynamic=1).run()
    Xss(targets=urls).scan()
    Sqli(targets=urls).scan()


def git_scan(keyword):
    GitScan(keyword)
