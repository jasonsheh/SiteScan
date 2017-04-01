#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.factory import SiteScan
from lib.subdomain import Domain
<<<<<<< HEAD

import argparse
import time
import sys


=======

import argparse
import time


>>>>>>> b48090a64e299874ab424d042b7633900f626713
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

<<<<<<< HEAD
    try:
        for url in urls:
            s = SiteScan(url)
            s.site_scan()
        t2 = time.time()
        print('\nTotal time: ' + str(t2 - t1))
    except KeyboardInterrupt:
        print('用户中断')
        sys.exit(0)
=======
    for url in urls:
        s = SiteScan(url)
        s.site_scan()
    t2 = time.time()
    print('\nTotal time: ' + str(t2 - t1))
>>>>>>> b48090a64e299874ab424d042b7633900f626713

if __name__ == '__main__':
    main()
