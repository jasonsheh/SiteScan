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

from lib.vuls.xss import Xss
from lib.vuls.sqli import Sqli
from lib.vuls.struts2 import Struts2

from lib.service.port import PortScan
from lib.service.Unauthorized import redis_unauthorized
from lib.service.Unauthorized import mongodb_unauthorized
from lib.service.Unauthorized import zookeeper_unauthorized
from lib.service.Unauthorized import elastic_search_unauthorized
from lib.service.Unauthorized import memcached_unauthorized


from lib.tools.baidu import Baidu

from lib.git.gitscan import GitScan

from lib.crawler import Crawler


def init_domain(domain):
    removed_prefix = ['http://www.', 'https://www.', 'https://', 'https://', 'www.']
    for prefix in removed_prefix:
        if domain.startswith(prefix):
            domain = domain.replace(prefix, '')
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


def service_scan(ip):
    """
    网络服务常见漏洞扫描
    """
    ports = PortScan([ip]).nmap_scan()
    for ip, port in ports.items():
        if 6379 in port:
            if redis_unauthorized(ip):
                print('redis_unauthorized')
        if 27017 in port:
            if mongodb_unauthorized(ip):
                print('mongodb_unauthorized')
        if 2181 in port:
            if zookeeper_unauthorized(ip):
                print('zookeeper_unauthorized')
        if 9200 in port:
            if elastic_search_unauthorized(ip):
                print('elastic_search_unauthorized')
        if 11211 in port:
            if memcached_unauthorized(ip):
                print('memcached_unauthorized')


def vul_scan(domain):
    """
    漏洞扫描
    """
    urls = Crawler(target=domain, dynamic=0).run()
    Xss(targets=urls).scan()
    Sqli(targets=urls).scan()
    Struts2(urls).scan()


def all_scan(keywords):
    """
    基于搜索引擎的批量网站扫描
    """
    websites = Baidu(keyword=keywords).run()
    for website in websites:
        print(website)
        vul_scan(website)


def git_scan(keyword):
    GitScan(keyword)
