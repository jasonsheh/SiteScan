#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.factory import SiteScan
import argparse


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
    print('''|____/|_|\__\___|____/ \___\__,_|_| |_|\t\t''')
    print('\t\t written by Jason_Sheh')

    s = SiteScan(args)
    s.site_scan()

if __name__ == '__main__':
    main()
