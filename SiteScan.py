#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.factory import init
from lib.factory import info_collect
from lib.factory import vul_scan
from lib.factory import git_scan

import sys
import argparse
import time

sys.path.append('C:\Code\SiteScan')

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--info",
                    help="collect info related to this domain")
parser.add_argument('-s', "--scan",
                    help='find vulnerabilities related to this domain')
parser.add_argument('-g', "--git",
                    help='find leaked info form Github')
parser.add_argument('--sub', default="false",
                    help='whether get all sub domains')
parser.add_argument("--install",
                    help="install SiteScan")
args = parser.parse_args()

print(''' ____  _ _       ____''')
print('''/ ___|(_) |_ ___/ ___|  ___ __ _ _ __''')
print('''\___ \| | __/ _ \___ \ / __/ _` | '_  \ ''')
print(''' ___) | | ||  __/___) | (_| (_| | | | |''')
print('''|____/|_|\__\___|____/ \___\__,_|_| |_|''')
print('\t\t written by Jason_Sheh')
t1 = time.time()
9
try:
    if args.info:
        info_collect(init(args.info))
    if args.scan:
        vul_scan(args.scan)
    if args.git:
        git_scan(args.git)
    t2 = time.time()
    print('\nTotal time: ' + str(t2 - t1))
except KeyboardInterrupt:
    print('用户中断')
    sys.exit(0)

