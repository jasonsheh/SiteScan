#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import nmap
from urllib.parse import urlparse


class Port:
    def __init__(self, ip):
        self.ip = ip
        self.nm = nmap.PortScanner()

    def scan(self):
        print('端口扫描...')
        self.nm.scan(self.ip, arguments='-sT -sV --unprivileged -p 21-25,80-89,110,143,443,513,873,1080,1433,1521,'
                                        '1158,3306-3308,3389,3690,5900,6379,7001,8000-8090,9000,9418,27017-27019,'
                                        '50060,11211,2049 ')

        for host in self.nm.all_hosts():
            print('--------------------------------------------------')
            print('Host : %s (%s)' % (host, self.nm[host].hostname()))
            print('State : %s' % self.nm[host].state())
            for proto in self.nm[host].all_protocols():
                print('----------')
                print('Protocol : %s' % proto)

                ports = list(self.nm[host][proto].keys())
                ports.sort()
                print('port\tstate\tname')
                for port in ports:
                    print('%s\t%s\t%s' %
                          (port, self.nm[host][proto][port]['state'], self.nm[host][proto][port]['name']))
                # self.analysis(host, proto, ports)
            print('\n')

    def analysis(self, host, proto, ports):
        for port in ports:
            if port == 21 and self.nm[host][proto][port]['state'] == 'open':
                print('ftp open')
            if port == 80 and self.nm[host][proto][port]['state'] == 'open':
                print('http open')
            if port == 3306 and self.nm[host][proto][port]['state'] == 'open':
                print('mysql open')
            if port == 6379 and self.nm[host][proto][port]['state'] == 'open':
                print('redis open')
            if port == 27017 and self.nm[host][proto][port]['state'] == 'open':
                print('mongodb open')
            if port == 7001 and self.nm[host][proto][port]['state'] == 'open':
                print('WebLogic open')
            if port == 8080 and self.nm[host][proto][port]['state'] == 'open':
                print('Jboss open')
            if port == 9080 and self.nm[host][proto][port]['state'] == 'open':
                print(self.nm[host][proto][port]['name'] + ' open')

    def run(self):
        self.scan()
        # return self.nm

if __name__ == '__main__':
    s = Port(ip='58.83.202.183')
    s.run()
