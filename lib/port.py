#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
sys.path.append('/home/jasonsheh/Tools/python/SiteScan')

import nmap
from scripts.ftp import Ftp
from database.database import Database
from celery import Celery


app = Celery('port', broker='redis://localhost')


@app.task()
def scan(ip):
    nm = nmap.PortScanner()
    print('\n# 端口扫描...')
    nm.scan(ip, arguments='-sT -P0 -sV')

    '''
    nm.scan(ip, arguments='-sT -P0 -sV --script=banner -p T:21-25,80-89,110,143,443,513,873,1080,1433,'
                                '1521,1158,3306-3308,3389,3690,5900,6379,7001,8000-8090,9000,9418,27017-27019,5'
                                '0060,111,11211,2049 --unprivileged')
    '''

    for host in nm.all_hosts():
        print('-------------------------------------------')
        print('Host : %s (%s)' % (host, nm[host].hostname()))
        print('State : %s' % nm[host].state())
        for proto in nm[host].all_protocols():
            print('----------')
            print('Protocol :%s' % proto)

            ports = list(nm[host][proto].keys())
            ports.sort()
            print('port\tstate\tname\tproduct\tversion')
            for port in ports:
                print('%s\t%s\t%s\t%s\t%s' %
                      (port, nm[host][proto][port]['state'], nm[host][proto][port]['name'],
                       nm[host][proto][port]['product'], nm[host][proto][port]['version']))

            Database().insert_port(host, nm[host][proto])
            # analysis(host, proto, ports)

            for port in ports:
                if port == 21 and nm[host][proto][port]['state'] == 'open':
                    print('ftp open')
                    p = Ftp(ip)
                    p.run()

                if port == 80 and nm[host][proto][port]['state'] == 'open':
                    print('http open')
                if port == 3306 and nm[host][proto][port]['state'] == 'open':
                    print('mysql open')
                if port == 6379 and nm[host][proto][port]['state'] == 'open':
                    print('redis open')
                if port == 27017 and nm[host][proto][port]['state'] == 'open':
                    print('mongodb open')
                if port == 7001 and nm[host][proto][port]['state'] == 'open':
                    print('WebLogic open')
                if port == 8080 and nm[host][proto][port]['state'] == 'open':
                    print('Jboss open')
                if port == 9080 and nm[host][proto][port]['state'] == 'open':
                    print(nm[host][proto][port]['name'] + ' open')


if __name__ == '__main__':
    scan(ip='221.226.37.164')
