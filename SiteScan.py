#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import getopt
import socket


class SiteScan:
    def __init__(self):
        self.target = ''
        self.ip = ''
        self.language = ''
        self.server = ''
        self.version = '0.01'

    def usage(self):
        print("Usage:%s [-h] [--help|--version] -u target...." % sys.argv[0])

    def run(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hu=:", ["help", "version"])
            for op, value in opts:
                if op in ('--help', '-h'):
                    print('#' + '-'*60 + '#')
                    print('  This tool help get the basic information of one site')
                    print('\t Such as ip, build_language, server_info')
                    print('#' + '-'*60 + '#')
                elif op == '--version':
                    print('Current version is ' + self.version)
                elif op == '-u':
                    self.target = args[0]
                    self.get_ip()
        except getopt.GetoptError as e:
            print(e)
            self.usage()
            sys.exit(1)

    def get_ip(self):
        try:
            self.ip = socket.gethostbyname(str(self.target))
            print('ip address: ' + self.ip)
        except Exception as e:
            print(e)

    def get_language(self):
        


def main():
    if len(sys.argv) == 1:
        print("Usage:%s [-h] [--help|--version] -u target...." % sys.argv[0])
        sys.exit()
    s = SiteScan()
    s.run()


if __name__ == '__main__':
    main()
