#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.factory import site_scan

import sys
import argparse
import time


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

    try:
        site_scan(args.domain)
        t2 = time.time()
        print('\nTotal time: ' + str(t2 - t1))
    except KeyboardInterrupt:
        print('用户中断')
        sys.exit(0)

if __name__ == '__main__':
    main()
