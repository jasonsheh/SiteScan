#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import requests
import threading
import time
import gevent
from gevent.queue import Queue
from gevent import monkey
monkey.patch_all()

'''
from database.database import Database
from setting import user_path
'''
sys.path.append('C:\Code\SiteScan')
from setting import user_path


class SenDir:
    def __init__(self, targets, id=''):
        self.targets = targets
        self.id = id
        self.queue = Queue()
        self.thread_num = 100
        self.sensitive = {}
        self.count = 0
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}

    def output(self):
        print('\n')
        for directory, status in sorted(self.sensitive.items()):
            print(directory + ':\t' + str(status))

    def enqueue_dir(self):
        with open(user_path+'/dict/dir.txt', 'r') as file:
            for eachline in file:
                self.queue.put_nowait(eachline.strip())

    def directory_brute(self):
        '''
        对网站进行敏感目录检测
        :return:
        '''
        while not self.queue.empty():
            _dir = self.queue.get()
            for target in self.targets:
                try:
                    url = target + _dir
                    self.count += 1
                    sys.stdout.write('\r目录扫描数: ' + str(self.count))
                    sys.stdout.flush()
                    r = requests.get('http://' + target + _dir, allow_redirects=False)

                    if r.status_code in [200, 403]:
                        self.sensitive[url] = r.status_code
                except requests.exceptions.ReadTimeout:
                    continue
                except requests.exceptions.ConnectionError:
                    continue
                except requests.exceptions.TooManyRedirects:
                    continue

    def error_page(self):
        '''
        判断有无错误界面，有则把该网站删除列表
        :return:
        '''
        need_be_removed = []
        for target in self.targets:
            try:
                url = target + '/.this_page_will_never_exists_lalala'
                r = requests.get('http://' + url, timeout=3, allow_redirects=False)
                # print(url, r.status_code)
                if r.status_code in [200, 403]:
                    need_be_removed.append(target)
                    continue

                for not_exist in ['', '/', '.config', '.sql', '.inc', '.bak', '.jsp', '.asp', '.aspx', '.php', '.html']:
                    url = target + '/this_page_will_never_exists' + not_exist
                    r = requests.get('http://' + url, timeout=3, allow_redirects=False)
                    # print(url, r.status_code)
                    if r.status_code in [200, 403]:
                        need_be_removed.append(target)
                        break

            except requests.exceptions.ConnectTimeout:
                continue
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.TooManyRedirects:
                continue
            except requests.exceptions.ReadTimeout:
                continue

        for removed in list(set(need_be_removed)):
            self.targets.pop(removed)

    def run(self):
        print('\n# 检测敏感目录...')
        self.error_page()
        self.enqueue_dir()

        threads = [gevent.spawn(self.directory_brute) for _ in range(self.thread_num)]
        gevent.joinall(threads)

        self.output()

        # Database().insert_sendir(self.sensitive, self.id)
        return self.sensitive


if __name__ == '__main__':
    SenDir(targets=[]).run()
