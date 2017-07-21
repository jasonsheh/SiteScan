#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import requests
import threading
import queue
import time
from database.database import Database


class Sendir:
    def __init__(self, targets, id=''):
        self.targets = targets
        self.id = id
        self.q = queue.Queue(0)
        self.thread_num = 5
        self.sensitive = []
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}

    def init(self):
        self.targets = list(set(self.targets))
        targets = []
        for target in self.targets:
            if not target.startswith('http://') and not target.startswith('https://'):
                target = 'http://' + target
            if target.endswith('/'):
                target = target[0:-1]
            targets.append(target)
        self.targets = targets

    def dirt(self):
        while not self.q.empty():
            _dir = self.q.get()
            for target in self.targets:
                try:
                    url = target + _dir
                    r = requests.get(url, timeout=4, allow_redirects=False)

                    if r.status_code in [200, 403]:
                        self.sensitive.append(url)
                        print(url+'\t'+str(r.status_code))
                except requests.exceptions.ReadTimeout:
                    continue
                except requests.exceptions.ConnectionError:
                    continue
                except requests.exceptions.TooManyRedirects:
                    continue

    def error_page(self):
        _targets = []
        for target in self.targets:
            for not_exist in ['config', 'jsp', 'asp', 'aspx', 'php']:
                try:
                    url = target + '/this_page_will_never_exists.' + not_exist
                    r = requests.get(url, timeout=4, allow_redirects=False)
                    # print(url, r.status_code)
                    if r.status_code in [200, 403]:
                        _targets.append(target)
                        break
                except requests.exceptions.ConnectTimeout:
                    continue
                except requests.exceptions.ConnectionError:
                    continue
                except requests.exceptions.TooManyRedirects:
                    continue
                except requests.exceptions.ReadTimeout:
                    continue

        for target in _targets:
            self.targets.remove(target)

    def run(self):
        self.init()
        self.error_page()
        print('\n# 检测敏感目录...')

        with open('/home/jasonsheh/Tools/python/SiteScan/dict/dir.txt', 'r') as file:
            for eachline in file:
                self.q.put(eachline.strip())

        threads = []
        for i in range(int(self.thread_num)):
            t = threading.Thread(target=self.dirt)
            threads.append(t)
        for item in threads:
            item.start()
        for item in threads:
            item.join()

        Database().insert_sendir(self.sensitive, self.id)
        return self.sensitive


def main():
    s = Sendir(targets=['ylc.njutcm.edu.cn', 'www.njutcm.edu.cn', 'its.njutcm.edu.cn', 'stu.njutcm.edu.cn'])
    s.init()
    s.error_page()

if __name__ == '__main__':
    main()
