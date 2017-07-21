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
# from selenium import webdriver


class Crawler:
    def __init__(self, target):
        self.target = target
        self.url_set = []
        self.urls = []
        self.sitemap = []
        self.q = queue.Queue(0)
        self.url_rule = []
        self.thread_num = 4
        self.header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        # self.cap = webdriver.DesiredCapabilities.PHANTOMJS
        # self.cap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片

    def init(self):
        if not self.target.startswith('http://') and not self.target.startswith('https://'):
            self.target = 'http://' + self.target
        if not self.target.endswith('/'):
            self.target += '/'

    def dynamic_conn(self, url):
        """
        动态
        连接,返回所有链接
        :param url:
        :return:
        """
        res = []
        driver = webdriver.PhantomJS(desired_capabilities=self.cap)
        driver.get(url)
        time.sleep(4)
        try:
            buttons = driver.find_elements_by_xpath("//*[@type='button'@onclick]")
            for button in buttons:
                button.click()
        except:
            pass

        try:
            forms = driver.find_elements_by_xpath("//form[@method='post']")
            for form in forms:
                action = form.get_attribute('action')
                texts = form.find_elements_by_xpath("//input[@type='text']")
                if '?' not in action:
                    _url = action + '?'
                else:
                    _url = action
                for text in texts:
                    _url += text.get_attribute("name")+'='+text.get_attribute("value")+'&'

                res.append(_url[:-1])
        except:
            pass

        try:
            frames = driver.find_elements_by_xpath("//iframe[@src]")
            for frame in frames:
                res.append(frame.get_attribute("src"))
        except:
            pass

        a = driver.find_elements_by_tag_name('a')
        for _a in a:
            res.append(_a.get_attribute("href"))

        driver.quit()
        return res

    def static_conn(self, url):
        try:
            r = requests.get(url, headers=self.header)
        except requests.exceptions.ChunkedEncodingError:
            return []
        pattern = re.compile(r'href="(.*?)"')
        return re.findall(pattern, r.text)

    def get_url(self, res):
        """
        提取页面中可爬取的链接
        :param res:
        :return:
        """

        res = list(set(res))
        new_url = []
        if res:
            for url in res:  # 添加url处理规则
                if not url:
                    continue
                if url.startswith(' '):
                    url = url[1:]
                if url.startswith('..'):
                    url = url[2:]
                if url.startswith('.'):
                    url = url[1:]

                if (url.startswith('http://') or url.startswith('https://')) and not url.startswith(self.target):
                    continue
                if url.startswith('ftp://'):
                    continue
                if url.startswith('mailto:'):
                    continue
                if re.search('\.(css|jpg|JPG|png|pdf|js|gif|xls|doc|docx|rar|ico|ppt)$', url) or re.search('javascript:', url):
                    continue
                if url.startswith('/'):
                    url = url[1:]
                if not url.startswith('http:') and not url.startswith('https:'):
                    url = self.target + url
                if url.startswith(self.target):
                    new_url.append(url)
                # print(url)
            new_url = list(set(new_url))
            return new_url
        else:
            return []

    def filter(self, res):
        """
        相似网址去重
        :param res:
        :return:
        """
        for i in res:
            if i not in self.url_set:
                self.url_set.append(i)
                # self.q.put(i)

            # print(urlparse(i).path)
            if urlparse(i).path in ['/', '']:
                rule = ''
            elif len(urlparse(i).path.split('/')) == 2 and '?' in i:
                rule = urlparse(i).path.split('/')[1][:3]
            else:
                rule = urlparse(i).path.split('/')[1][:3]

            for path in urlparse(i).path.split('/')[1:]:
                rule += str(len(path))  # 判断网址相似规则

            if '?' in i:
                for query in urlparse(i).query.split('&'):
                    rule += query.split('=')[0][:1]
                    rule += query.split('=')[0][-1:]  # 判断网址相似规则

            if rule in self.url_rule:
                continue
            else:
                # print(rule + i)
                self.q.put(i)
                self.urls.append(i)
                self.url_rule.append(rule)
                self.sitemap.append(urlparse(i).path)

        list(set(self.sitemap))
        list(set(self.urls))

    def crawler(self):
        while not self.q.empty():
            url = self.q.get()

            new_res = self.static_conn(url)
            res = self.get_url(new_res)
            if not res:
                continue
            self.filter(res)

    # almost done need improved
    def scan(self):
        self.init()
        try:
            r = requests.get(self.target, headers=self.header)
            pattern = re.compile(r'href="(.*?)"')
            res = re.findall(pattern, r.text)
            self.target = r.url
        except requests.exceptions.ConnectionError:
            return self.url_set
        except requests.exceptions.ReadTimeout:
            return self.url_set
        except requests.exceptions.ChunkedEncodingError:
            return self.url_set

        res = self.get_url(res)
        if not res:
            res = self.static_conn(self.target + '/index.html')
            res = self.get_url(res)

        self.filter(res)

        threads = []
        for i in range(int(self.thread_num)):
            t = threading.Thread(target=self.crawler)
            threads.append(t)
        for item in threads:
            item.start()

        for item in threads:
            item.join()

        if self.url_set:
            print('\n# 扫描链接总数:' + str(len(self.url_set)))

        '''
            self.urls.sort()
            for url in self.urls:
                print(url)
        '''

        # print(len(self.urls))

        return self.urls


def main():
    Crawler(target='http://it.jit.edu.cn/').scan()

if __name__ == '__main__':
    main()
