#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

"""
利用python-nmap对目标IP进行扫描
"""

import nmap
import threading
import os
from scapy.all import *
from database.database import Database


class PortScan:
    def __init__(self, ips, id=''):
        self.ips = ips
        self.result = {}
        self.id = id
        self.scan_port_large = [21, 22, 23, 2425, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 110, 143, 443, 513, 873, 1080,
                                1433, 1521, 1158, 3306, 3307, 3308, 3389, 3690, 5900, 6379, 7001, 8000, 8001, 8080, 8090,
                                9000, 9418, 27017, 27018, 27019, 50060, 50070, 111, 11211, 2049]
        self.scan_port = [80, 443]
        self.nm = nmap.PortScanner()

    def masscan_scan(self):
        for ip in self.ips:
            result = os.popen(
                'masscan -p21-25,53,80-89,143,443,513,873,990,1027,1080,1443,1433,1521,'
                '1158,1930-1940,2000,3090,3306-3308,3389,3690,5003,5900,6379,7001,8000-8090,9000,9418,9090,27017-27019,'
                '28291,50060,53399,5666,5555,28728,23002,23091,23003,23389,5222,19175,8811,8686,3443,1780,3128,888,874,111,11211,2049 --rate=1000 {ip}'.format(ip=ip))
            result = [_.strip() for _ in result.read().split('\n')[:-1]]
            # Discovered open port 8080/tcp on 218.95.177.150
            # _,         _,   _,   port,    _, ip
            ports = []
            for _ in result:
                _, _, _, port, _, ip = _.split(' ')
                ports.append(port.split('/')[0])
                self.result[ip] = ports
        print(self.result)

    def nmap_scan(self):
        for ip in self.ips:
            # self.nm.scan(ip, arguments='-sT -P0 -sV')

            self.nm.scan(ip, arguments='-sT -P0 -sV -p T:21-25,80-89,110,143,443,513,873,1080,1433,1521,'
                                        '1158,2181,3306-3308,3389,3690,5900,6379,7001,8000-8090,9000,9418,27017-27019,'
                                        '50060, 50070,111,11211,2049')

            for host in self.nm.all_hosts():
                print('Host : %s (%s)' % (host, self.nm[host].hostname()))
                for proto in self.nm[host].all_protocols():
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
                    self.result[host] = ports
        print(self.result)
        return self.result

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
    PortScan(ips=['218.95.177.150']).masscan_scan()
