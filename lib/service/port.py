#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

"""
利用python-nmap对目标IP进行扫描
"""

import nmap
import threading
from scapy.all import *
from database.database import Database


class Port:
    def __init__(self, domains=[], ips=[], id=''):
        self.domains = domains
        self.ips = ips
        self.id = id
        # self.scan_port = [21, 22, 23, 2425, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 110, 143, 443, 513, 873, 1080, 1433,
        #                   1521, 1158, 3306, 3307, 3308, 3389, 3690, 5900, 6379, 7001, 8000, 8001, 8080, 8090, 9000,
        #                   9418, 27017, 27018, 27019, 50060, 111, 11211, 2049]
        self.scan_port = [80, 443]
        self.nm = nmap.PortScanner()

    def nmap_scan(self):
        for domain in self.domains:
            # self.nm.scan(ip, arguments='-sT -P0 -sV')

            self.nm.scan(domain, arguments='-sT -P0 -sV -p T:21-25,80-89,110,143,443,513,873,1080,1433,1521,'
                                        '1158,3306-3308,3389,3690,5900,6379,7001,8000-8090,9000,9418,27017-27019,'
                                        '50060,111,11211,2049')

            for host in self.nm.all_hosts():
                print('-------------------------------------------')
                print('Host : %s (%s)' % (host, self.nm[host].hostname()))
                for proto in self.nm[host].all_protocols():
                    print('----------')

                    ports = list(self.nm[host][proto].keys())
                    ports.sort()
                    print('port,state,name,product,version')
                    for port in ports:
                        print('{},{},{},{},{}'.format(port,
                                                      self.nm[host][proto][port]['state'],
                                                      self.nm[host][proto][port]['name'],
                                                      self.nm[host][proto][port]['product'],
                                                      self.nm[host][proto][port]['version']))

                    # Database().insert_port(host, self.nm[host].hostname(), self.nm[host][proto], self.id)
                    self.ips.append(host)
                    # analysis(host, proto, ports)

    def scapy_scan(self):
        self.scapy_scan_send()

    def scapy_scan_send(self):
        for target_ip in self.ips:
            # t = threading.Thread(target=self.scapy_scan_receive, args=(target_ip, ))
            # t.start()
            for target_port in self.scan_port:
                syn_packet = IP(dst=target_ip) / TCP(sport=RandShort(), dport=target_port, flags="S")
                result = send(syn_packet, iface="eth0")

    def scapy_scan_receive(self, ip):
        receive = sniff(filter="tcp and host " + ip, count=2)
        print(receive)


if __name__ == '__main__':
    # Port(['octfive.cn']).nmap_scan()
    Port(ips=['115.159.160.21']).scapy_scan_send()
