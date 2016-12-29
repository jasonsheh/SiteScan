#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests


class Sendir:
    def __init__(self, target):
        self.target = target[:-1]

    def run(self):
        print('\n检测敏感目录...')
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        with open('dir.txt', 'r') as dirt:
            with open('res.txt', 'a+') as file:
                file.write('\nSensitive directory\n')
                for _dir in dirt:
                    url = self.target + _dir.strip()
                    r = requests.get(url)
                    if r.status_code == 200:
                        print(url)
                        file.write(url + '\n')
