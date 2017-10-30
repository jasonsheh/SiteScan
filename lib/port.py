#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import nmap
from scripts.ftp import Ftp
from database.database import Database

import time


class Port:
    def __init__(self, domains, id=''):
        self.domains = domains
        self.ips = []
        self.id = id
        self.nm = nmap.PortScanner()

    def run(self):
        t1 = time.time()
        print('\n# 端口扫描...')
        for url, ip_list in self.domains.items():
            ips = [ip for ip in self.ips]
            for ip in ip_list:
                if ip not in ips:
                    self.scan(ip)
        t2 = time.time()
        print(t2-t1)

    def scan(self, ip):
        # self.nm.scan(ip, arguments='-sT -P0 -sV')

        self.nm.scan(ip, arguments='-sT -P0 -sV -p T:21-25,80-89,110,143,443,513,873,1080,1433,'
                                   '1521,1158,3306-3308,3389,3690,5900,6379,7001,8000-8090,9000,9418,27017-27019,'
                                   '50060,111,11211,2049')

        for host in self.nm.all_hosts():
            print('-------------------------------------------')
            print('Host : %s (%s)' % (host, self.nm[host].hostname()))
            for proto in self.nm[host].all_protocols():
                print('----------')

                ports = list(self.nm[host][proto].keys())
                ports.sort()
                print('port\tstate\tname\tproduct\tversion')
                for port in ports:
                    print('%s\t%s\t%s\t%s\t%s' %
                          (port, self.nm[host][proto][port]['state'], self.nm[host][proto][port]['name'],
                           self.nm[host][proto][port]['product'], self.nm[host][proto][port]['version']))

                Database().insert_port(host, self.nm[host].hostname(), self.nm[host][proto], self.id)
                self.ips.append(host)
                # analysis(host, proto, ports)
