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
    def __init__(self, domains, id=''):
        self.domains = domains
        self.id = id
        self.queue = Queue()
        self.thread_num = 200
        self.sensitive = {}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}

    def enqueue_dir(self):
        with open(user_path+'/dict/dir.txt', 'r') as file:
            for eachline in file:
                for target in self.domains:
                    self.queue.put_nowait(target+eachline.strip())

    def enqueue_error_page(self):
        for target in self.domains:
            url = target + '/.this_page_will_never_exists_lalala'
            self.queue.put_nowait(url)

    def directory_brute(self):
        '''
        对网站进行敏感目录检测
        :return:
        '''
        while not self.queue.empty():
            url = self.queue.get()
            try:
                sys.stdout.write('\r目录扫描数: ' + str(self.queue.qsize()))
                sys.stdout.flush()
                r = requests.get('http://'+url, timeout=3, allow_redirects=False)

                if r.status_code in [200, 403]:
                    if url.split('/')[0] not in self.sensitive.keys():
                        self.sensitive[url.split('/')[0]] = [url + '\t' + str(r.status_code)]
                    else:
                        self.sensitive[url.split('/')[0]].append(url + '\t' + str(r.status_code))
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
        while not self.queue.empty():
            url = self.queue.get()
            try:
                r = requests.get('http://' + url, timeout=2, allow_redirects=False)
                # print(url, r.status_code)
                if r.status_code in [200, 403]:
                    self.domains.remove(url.split('/')[0])
                    continue

                for not_exist in ['', '/', '.config', '.sql', '.inc', '.bak', '.jsp', '.asp', '.aspx', '.php', '.html']:
                    url = url + '/this_page_will_never_exists' + not_exist
                    r = requests.get('http://' + url, timeout=3, allow_redirects=False)
                    if r.status_code in [200, 403]:
                        self.domains.remove(url.split('/')[0])
                        break

            except requests.exceptions.ConnectTimeout:
                continue
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.TooManyRedirects:
                continue
            except requests.exceptions.ReadTimeout:
                continue

    def run(self):
        print('\n# 检测敏感目录...')
        self.enqueue_error_page()
        threads = [gevent.spawn(self.error_page) for _ in range(self.thread_num)]
        gevent.joinall(threads)

        self.enqueue_dir()
        threads = [gevent.spawn(self.directory_brute) for _ in range(self.thread_num)]
        gevent.joinall(threads)
        # self.output()

        # Database().insert_sendir(self.sensitive, self.id)
        return self.sensitive


if __name__ == '__main__':
    SenDir(['jsclx.jit.edu.cn']).run()
