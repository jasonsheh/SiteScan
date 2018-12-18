#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from lib.controller import init_domain
from lib.controller import info_collect
from lib.controller import vul_scan
from lib.controller import service_scan
from lib.controller import all_scan
from lib.controller import git_scan

from lib.server import SRCKiller
from utils.timer import timer

import sys
import argparse

from setting import user_path
sys.path.append(user_path)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--info",
                    help="collect info related to this domain")
parser.add_argument('-s', "--scan",
                    help='find vulnerabilities related to this domain')
parser.add_argument('-p', "--port",
                    help='find port-related vulnerabilities on this ip')
parser.add_argument('-a', "--all",
                    help='auto scan all related website')
parser.add_argument('-g', "--git",
                    help='find leaked info form Github')
parser.add_argument('--sub', default="false",
                    help='whether get all sub domains')
parser.add_argument("--install",
                    help="install SiteScan")
parser.add_argument("--server",
                    help="run as service")
args = parser.parse_args()

print(r''' ____  _ _       ____''')
print(r'''/ ___|(_) |_ ___/ ___|  ___ __ _ _ __''')
print(r'''\___ \| | __/ _ \___ \ / __/ _` | '_  \ ''')
print(r''' ___) | | ||  __/___) | (_| (_| | | | |''')
print(r'''|____/|_|\__\___|____/ \___\__,_|_| |_|''')
print('\t\t written by Jason_Sheh')


@timer
def main():
    try:
        if args.info:
            info_collect(init_domain(args.info))
        if args.scan:
            vul_scan(init_domain(args.scan))
        if args.port:
            service_scan(args.port)
        if args.all:
            all_scan(args.all)
        if args.git:
            git_scan(args.git)
        if args.server:
            SRCKiller().info_collect()
    except KeyboardInterrupt:
        print('用户中断')
        sys.exit(0)


if __name__ == '__main__':
    main()
