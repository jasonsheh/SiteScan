#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from database.database import Database

from lib.subdomain import Domain
from lib.crawler import Crawler
from lib.port import Port
from lib.sendir import Sendir
from lib.vul import Vul

import requests


def site_scan(domain):
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

    id = Database().insert_task(domain)

    domains = Domain(domain, id).run()

    # , [y for x in self.domains.values() for y in x]

    real_domains = []
    for domain in [x for x in domains.keys()]:
        try:
            r = requests.get('http://'+domain, timeout=4, allow_redirects=False)
            if r.status_code not in [400, 403, 500]:
                real_domains.append(domain)
        except:
            continue
        '''
        except requests.exceptions.ConnectTimeout:
            removed_domains.append(domain)
            continue
        except requests.exceptions.ConnectionError:
            removed_domains.append(domain)
            continue
        except requests.exceptions.TooManyRedirects:
            removed_domains.append(domain)
            continue
        except requests.exceptions.ReadTimeout:
            removed_domains.append(domain)
            continue
        '''

    Sendir(real_domains, id).run()

    Port(domains, id).run()

    '''
    print('漏洞扫描')
    for domain in domains:
        url = Crawler(domain).scan()
        Vul(url, id).run()
    '''
