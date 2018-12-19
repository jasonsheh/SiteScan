#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-


from setting import user_path, user_agent, sendir_thread_num
from typing import List, Dict

from gevent.queue import Queue
from gevent import monkey
monkey.patch_all()

import requests
import gevent


class SenDir:
    def __init__(self, domains, id=0):
        self.domains: List = domains
        self.id: int = id
        self.timeout: int = 2
        self.queue = Queue()
        self.sensitive: Dict = {}
        self.headers: Dict = {'User-Agent': user_agent}
        self.exist_status_code: List[int] = [200, 403]
        self.not_exist_file_type: List[str] = ['/', '.config', '.sql', '.inc', '.bak', '.jsp', '.asp', '.aspx', '.php', '.html']

    def enqueue_dir(self):
        with open(user_path+'/dict/dir.txt', 'r') as file:
            for eachline in file:
                for target in self.domains:
                    self.queue.put_nowait(target+eachline.strip())

    def enqueue_error_page(self):
        for target in self.domains:
            url = target + '/.this_directory_will_never_exists_lalala'
            self.queue.put_nowait(url)

    def error_page(self):
        """
        判断有无错误界面，有则把该网站删除列表
        :return:
        """
        while not self.queue.empty():
            url = self.queue.get()
            # sys.stdout.write('\r错误页面剩余数: ' + str(self.queue.qsize()))
            # sys.stdout.flush()

            print(url)
            try:
                r = requests.get('http://{}'.format(url), timeout=self.timeout)
            except requests.exceptions.ConnectTimeout:
                continue
            except requests.exceptions.ReadTimeout:
                continue
            except requests.exceptions.ConnectionError:
                continue

            if r.status_code in self.exist_status_code:
                self.domains.remove(url.split('/')[0])
                continue

            # TODO 以下功能有待商榷
            # for not_exist in self.not_exist_file_type:
            #     url_with_ext = '{url}/{ext}'.format(url=url, ext=not_exist)
            #     try:
            #         print(url_with_ext)
            #         r = requests.get('http://{}'.format(url_with_ext), timeout=self.timeout)
            #     except requests.exceptions.ConnectTimeout:
            #         continue
            #     except requests.exceptions.ReadTimeout:
            #         continue
            #     if r.status_code in self.exist_status_code:
            #         self.domains.remove(url.split('/')[0])
            #         break

    def directory_brute(self):
        """
        对网站进行敏感目录检测
        :return:
        """
        while not self.queue.empty():
            url = self.queue.get()
            sys.stdout.write('\r目录扫描剩余数: ' + str(self.queue.qsize()))
            sys.stdout.flush()
            try:
                r = requests.get('http://' + url, timeout=self.timeout)
            except requests.exceptions.ConnectTimeout:
                continue
            except requests.exceptions.ReadTimeout:
                continue
            if r.status_code in [200, 403]:
                if url.split('/')[0] not in self.sensitive.keys():
                    self.sensitive[url.split('/')[0]] = [url + '\t' + str(r.status_code)]
                else:
                    self.sensitive[url.split('/')[0]].append(url + '\t' + str(r.status_code))

    def run(self):
        print('移除错误页面...')
        self.enqueue_error_page()
        self.error_page()

        print('\n检测敏感目录...')
        self.enqueue_dir()
        threads = [gevent.spawn(self.directory_brute) for _ in range(sendir_thread_num)]
        gevent.joinall(threads)
        # self.directory_brute()

        # Database().insert_sendir(self.sensitive, self.id)
        return self.sensitive


if __name__ == '__main__':
    print(SenDir(['green.jit.edu.cn', 'art.jit.edu.cn']).run())
