#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
sys.path.append('/home/jasonsheh/Tools/python/SiteScan')

from lib.basicinfo import Info
from lib.crawler import Crawler
from lib.sqltest import Sql
from lib.sendir import Sendir
from lib.xss import Xss
from lib.struts2 import Struts2
from lib.port import Port
from lib.subdomain import Domain

from celery import Celery
cel = Celery('cel', broker='redis://localhost:6379')


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
def site_scan(domain):
    Domain(domain).run()
    Sendir(domain).run()
