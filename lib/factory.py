#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from database.database import Database

from lib.subdomain import Domain
from lib.crawler import Crawler
from lib.port import Port
from lib.sendir import Sendir
from lib.vul import Vul


def site_scan(domain):
    if domain.startswith('http://www.'):
        domain = domain[11:]
    elif domain.startswith('https://www.'):
        domain = domain[12:]
    elif domain.startswith('http://'):
        domain = domain[7:]
    elif domain.startswith('https://'):
        domain = domain[8:]

    id = Database().insert_task(domain)

    domains, ips = Domain(domain, id).run()

    print('漏洞扫描')
    for domain in domains:
        url = Crawler(domain).scan()
        Vul(url, id).run()

    print('敏感信息泄露')
    Sendir(domains, id).run()

    print('端口扫描')
    Port(id).run(ips)
