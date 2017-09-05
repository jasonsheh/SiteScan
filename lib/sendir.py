#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import requests
import threading
import queue
import time

from database.database import Database
from setting import user_path

class Sendir:
    def __init__(self, targets, id=''):
        self.targets = targets
        self.id = id
        self.q = queue.Queue(0)
        self.thread_num = 5
        self.sensitive = {}
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
        '''
        对网站进行敏感目录检测
        :return:
        '''
        while not self.q.empty():
            _dir = self.q.get()
            for target in self.targets:
                try:
                    url = target + _dir
                    r = requests.get(url, timeout=4, allow_redirects=False)

                    if r.status_code in [200, 403]:
                        self.sensitive[url] = r.status_code
                        print(url+'\t'+str(r.status_code))
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
        _targets = []
        for target in self.targets:
            try:
                for not_exist in ['', '/', '.config', '.jsp', '.asp', '.aspx', '.php', '.html']:
                    url = target + '/this_page_will_never_exists' + not_exist
                    r = requests.get(url, timeout=6, allow_redirects=False)
                    # print(url, r.status_code)
                    if r.status_code in [200, 403]:
                        _targets.append(target)
                        break

                url = target + '/.this_page_will_never_exists_lalala'
                r = requests.get(url, timeout=6, allow_redirects=False)
                # print(url, r.status_code)
                if r.status_code in [200, 403]:
                    _targets.append(target)

            except requests.exceptions.ConnectTimeout:
                continue
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.TooManyRedirects:
                continue
            except requests.exceptions.ReadTimeout:
                continue

        _targets = list(set(_targets))
        for target in _targets:
            self.targets.remove(target)

    def run(self):
        self.init()
        self.error_page()
        print('\n# 检测敏感目录...')

        # 文件入队列
        with open(user_path+'/dict/dir.txt', 'r') as file:
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
    s = Sendir(targets=['http://apollo.yirendai.com/'])
    s.init()
    s.error_page()

if __name__ == '__main__':
    main()
