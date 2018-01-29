#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-


from setting import user_path
import sys
sys.path.append(user_path)

from lib.crawler import Crawler
from lib.info.sendir import SenDir
from lib.port import Port
from lib.info.subdomain import AllDomain

from database.database import Database

from celery import Celery
cel = Celery('cel', broker='redis://localhost:6379')


@cel.task()
def crawl_scan(domain):
    Crawler(domain, dynamic=1).run()


@cel.task()
def port_scan(ip):
    Port(list(ip)).scan()


@cel.task()
def domain_scan(domain):
    AllDomain(domain).run()


@cel.task()
def sendir_scan(domain):
    SenDir(list(domain)).run()


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
    domains, ips = AllDomain(domain, id).run()
    for domain in domains:
        url = Crawler(domain).run()
    SenDir(domains, id).run()
    Port(id).scan()
