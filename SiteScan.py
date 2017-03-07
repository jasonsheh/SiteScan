#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.factory import SiteScan
from lib.subdomain import Domain

import argparse
import time


def sub_domain(url, sub):
    if sub == 'true':
        s = Domain(url)
        return s.run()
    else:
        return [url]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain",
                        help="domain name")
    parser.add_argument('-s', '--sub', default="true",
                        help='whether get all sub domains')
    args = parser.parse_args()

    print(''' ____  _ _       ____''')
    print('''/ ___|(_) |_ ___/ ___|  ___ __ _ _ __''')
    print('''\___ \| | __/ _ \___ \ / __/ _` | '_  \ ''')
    print(''' ___) | | ||  __/___) | (_| (_| | | | |''')
    print('''|____/|_|\__\___|____/ \___\__,_|_| |_|''')
    print('\t\t written by Jason_Sheh')
    t1 = time.time()

    urls = sub_domain(args.domain, args.sub)

    for url in urls:
        s = SiteScan(url)
        s.site_scan()
    t2 = time.time()
    print('\nTotal time: ' + str(t2 - t1))

if __name__ == '__main__':
    main()
