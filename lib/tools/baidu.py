#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import re
from urllib.parse import urlparse
import time


class Baidu:
    def __init__(self, keyword):
        self.keyword: str = keyword
        self.start_page: int = 6
        self.end_page: int = 35
        self.res = []
        self.url = []
        self.big_company = ['zhidao.baidu.com']

    def run(self) -> list:
        pattern = re.compile(r'<a target="_blank" href="(.*?)" class="c-showurl" style="text-decoration:none;">')
        for i in range(self.start_page, self.end_page):
            url = 'http://www.baidu.com/s?wd={}&pn={}'.format(self.keyword, str(i*10))
            r = requests.get(url).text
            self.res += re.findall(pattern, r)
            if i % 9 == 0:
                time.sleep(1)
        self.turn2url()
        self.clean()
        return self.url

    def turn2url(self):
        pattern = re.compile(r"'Location': '(.*?)',")
        for raw_url in self.res:
            r = requests.get(raw_url, allow_redirects=False)
            r = str(r.headers)
            self.url += re.findall(pattern, r)

    def clean(self):
        res = {}
        for url in self.url:
            url_hostname = urlparse(url).netloc
            if url_hostname in self.big_company:
                continue
            if url_hostname not in res.keys():
                res[url_hostname] = url
        self.url = list(res.values())

    def output(self):
        for url in self.url:
            print(url)


if __name__ == '__main__':
    b = Baidu(keyword='新闻 inurl:.asp?id=')
    b.run()
    b.output()
