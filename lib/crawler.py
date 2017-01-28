#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import re
from urllib.parse import urlparse
import threading
import queue
import time
import sys


class Crawler:
    def __init__(self, target):
        self.target = target
        self.url_set = []
        self.sitemap = []
        self.site_file = []
        self.q = queue.Queue(0)

    @staticmethod
    def conn(target):  # get url in one page
        try:
            r = requests.get(target, timeout=1)
            pattern_1 = re.compile(r'href="(.*?)"')
            pattern_2 = re.compile(r'src="(.*?)"')
            res = re.findall(pattern_1, r.text)
            res += re.findall(pattern_2, r.text)
            return res
        except:
            return []

    def get_url(self, res):
        res = list(set(res))
        new_url = []
        for url in res:
            _quit = 0
            # print(url)
            if url.startswith('http') and not url.startswith(self.target):
                continue
            for i in ['javascript:', '(', '.css', '.jpg', '.png', '.pdf',
                      '.xls', '.doc', '.rar', '.ico', '.ppt', '.pptx']:
                if i in url:
                    if i == '.rar':
                        self.site_file.append(i)
                    _quit = 1
                    break
            if _quit:
                continue
            if url.startswith('..'):
                url = url[2:]
            if not url.startswith('/') and not url.startswith('http:') and not url.startswith('www'):
                url = '/' + url
            if '/' in url and not url.startswith('http:'):
                url = self.target + url
            if url.startswith(self.target):
                new_url.append(url)
            # print(url)
        new_url = list(set(new_url))
        return new_url

    def crawler(self):
        while not self.q.empty():
            if self.q.qsize() != 0:
                sys.stdout.write('# 剩余爬取链接个数' + str(self.q.qsize()) + '\r')
                sys.stdout.flush()
            url = self.q.get()
            try:
                new_res = self.conn(url)
                res = self.get_url(new_res)
            except Exception as e:
                print(e)
                continue
            for i in res:
                if i not in self.url_set:
                    self.url_set.append(i)
                    # self.q.put(i)

                if ('?' in i) and (urlparse(i).path.split('?')[0] not in self.sitemap):
                    self.sitemap.append(urlparse(i).path.split('?')[0])
                    self.q.put(i)
                    # print(i)
                elif urlparse(i).path.rsplit('/', 1)[0] == '' and urlparse(i).path not in self.sitemap:
                    self.sitemap.append(urlparse(i).path)
                    self.q.put(i)
                    # print(i)
                elif urlparse(i).path.rsplit('/', 1)[0] not in self.sitemap:  # 伪静态
                    self.sitemap.append(urlparse(i).path.rsplit('/', 1)[0])
                    self.q.put(i)
                    # print(i)

            time.sleep(0.1)

    # almost done need improved
    def run(self):
        res = self.conn(self.target)
        res = self.get_url(res)
        if not res:
            res = self.conn(self.target + '/index.php')
            res = self.get_url(res)
        for i in res:
            self.url_set.append(i)
            if ('?' in i) and (urlparse(i).path.split('?')[0] not in self.sitemap):
                self.sitemap.append(urlparse(i).path.split('?')[0])
                # print(i)
            elif urlparse(i).path.rsplit('/', 1)[0] == [] and urlparse(i).path not in self.sitemap:
                self.sitemap.append(urlparse(i).path)
                # print(i)
            elif urlparse(i).path.rsplit('/', 1)[0] not in self.sitemap:  # 伪静态
                self.sitemap.append(urlparse(i).path.rsplit('/', 1)[0])
            self.q.put(i)

        thread_num = 5
        threads = []
        for i in range(int(thread_num)):
            t = threading.Thread(target=self.crawler)
            threads.append(t)
        for item in threads:
            item.start()

        for item in threads:
            item.join()

        print('\n\n扫描链接总数:' + str(len(self.url_set)))

        self.sitemap.sort()

        print("\n目录结构")
        for url in self.sitemap:
            print(url)

        return self.url_set, self.sitemap
