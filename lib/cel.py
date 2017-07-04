#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
sys.path.append('/home/jasonsheh/Tools/python/SiteScan')

from lib.crawler import Crawler
from lib.sendir import Sendir
from lib.port import Port
from lib.subdomain import Domain
from lib.vul import Vul

from database.database import Database

from celery import Celery
cel = Celery('cel', broker='redis://localhost:6379')


@cel.task()
def crawl_scan(domain):
    Crawler(domain).scan()


@cel.task()
def port_scan(ip):
    Port().scan(ip)


@cel.task()
def domain_scan(domain):
    Domain(domain).run()


@cel.task()
def sendir_scan(domain):
    Sendir(domain).run()


@cel.task()
def vul_scan(domain):
    url = Crawler(domain).scan()
    Vul(url).run()


@cel.task()
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
    for domain in domains:
        url = Crawler(domain).scan()
        Vul(url, id).run()
    Sendir(domains, id).run()
    Port(id).run(ips)
