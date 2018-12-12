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

from lib.poc.common.xss import Xss
from lib.poc.common.sqli import Sqli
from lib.poc.common.struts2 import Struts2

from lib.poc.service.unauth_redis import RedisUnauthorized
from lib.poc.service.unauth_mogodb import MongodbUnauthorized
from lib.poc.service.unauth_zookeeper import ZookeeperUnauthorized
from lib.poc.service.unauth_elastic_search import ElasticSearchUnauthorized
from lib.poc.service.unauth_memcache import MemcachedUnauthorized
from lib.poc.service.unauth_hadoop import HadoopUnauthorized

from lib.port import PortScan
from lib.tools.baidu import Baidu
from lib.git.gitscan import GitScan
from lib.crawler import Crawler


def init_domain(domain):
    removed_prefix = ['http://www.', 'https://www.', 'https://', 'https://', 'www.']
    for prefix in removed_prefix:
        if domain.startswith(prefix):
            domain = domain.replace(prefix, '')
    return domain.strip('/')


def info_collect(domain):
    """
    信息收集
    """
    # id = Database().insert_task(domain)
    domains = AllDomain(domain).run()
    title = GetTitle([x for x in domains.keys()]).run()
    fingerprint = FingerPrint([x for x in domains.keys()]).run()
    dirs = SenDir([x for x in domains.keys()]).run()
    SaveToFile(domain, domains, title, fingerprint, dirs).save()


def service_scan(ip):
    """
    网络服务常见漏洞扫描
    """
    ports = PortScan([ip]).nmap_scan()
    for ip, port in ports.items():
        if 6379 in port:
            if RedisUnauthorized(ip).check():
                print('redis_unauthorized')
        if 27017 in port:
            if MongodbUnauthorized(ip).check():
                print('mongodb_unauthorized')
        if 2181 in port:
            if ZookeeperUnauthorized(ip).check():
                print('zookeeper_unauthorized')
        if 9200 in port:
            if ElasticSearchUnauthorized(ip).check():
                print('elastic_search_unauthorized')
        if 11211 in port:
            if MemcachedUnauthorized(ip).check():
                print('memcached_unauthorized')
        if 50070 in port:
            if HadoopUnauthorized(ip).check():
                print('hadoop_unauthorized')


def poc_scan():
    pass


def vul_scan(domain):
    """
    常见漏洞扫描
    """
    urls = Crawler(target=domain, dynamic=False).run()
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
