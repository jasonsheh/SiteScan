#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.factory import SiteScan
from lib.subdomain import Domain

import argparse


def sub_domain(url):
    s = Domain(url)
    return s.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain",
                        help="domain name")
    parser.add_argument('-m', '--mode', default="s",
                        help='single or all')
    args = parser.parse_args()

    print(''' ____  _ _       ____''')
    print('''/ ___|(_) |_ ___/ ___|  ___ __ _ _ __''')
    print('''\___ \| | __/ _ \___ \ / __/ _` | '_  \ ''')
    print(''' ___) | | ||  __/___) | (_| (_| | | | |''')
    print('''|____/|_|\__\___|____/ \___\__,_|_| |_|''')
    print('\t\t written by Jason_Sheh')

    urls = sub_domain(args.domain)

    for url in urls:
        s = SiteScan(url)
        s.site_scan()

if __name__ == '__main__':
    main()
