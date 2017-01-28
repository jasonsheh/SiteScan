#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import nmap


class Port:
    def __init__(self, ip):
        self.ip = ip

    def run(self):
        print('端口扫描...')
        nm = nmap.PortScanner()
        nm.scan(self.ip, arguments='-Pn')

        for host in nm.all_hosts():
            print('--------------------------------------------------')
            print('Host : %s (%s)' % (host, nm[host].hostname()))
            print('State : %s' % nm[host].state())
            for proto in nm[host].all_protocols():
                print('----------')
                print('Protocol : %s' % proto)

                lport = list(nm[host][proto].keys())
                lport.sort()
                print('port\tstate\tname')
                for port in lport:
                    print('%s\t%s\t%s' %
                          (port, nm[host][proto][port]['state'], nm[host][proto][port]['name']))
