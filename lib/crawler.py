#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import re
from urllib.parse import urlparse
import threading
import queue
import time
from selenium import webdriver

import sys
sys.path.append('C:\Code\SiteScan')


class Crawler:
    def __init__(self, target):
        self.target = target
        self.url_set = []  # 存放所有链接
        self.urls = []  # 存放不重复规则链接
        self.sitemap = []
        self.q = queue.Queue(0)
        self.url_rule = []
        self.thread_num = 4
        self.header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        # 禁用图片
        chrome_prefs = {}
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_options.experimental_options["prefs"] = chrome_prefs

        self.driver = webdriver.Chrome(chrome_options=chrome_options)

        # self.cap = webdriver.DesiredCapabilities.PHANTOMJS
        # self.cap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片

    def init(self):
        if not self.target.startswith('http://') and not self.target.startswith('https://'):
            self.target = 'http://' + self.target
        if not self.target.endswith('/'):
            self.target += '/'

    def dynamic_conn(self, url):
        """
        动态连接,返回所有链接
        :param url:
        :return:
        """
        res = []
        self.driver.get(url)
        time.sleep(4)
        try:
            buttons = self.driver.find_elements_by_xpath("//*[@type='button'@onclick]")
            for button in buttons:
                button.click()
        except:
            pass

        try:
            forms = self.driver.find_elements_by_xpath("//form[@method='post']")
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
            frames = self.driver.find_elements_by_xpath("//iframe[@src]")
            for frame in frames:
                res.append(frame.get_attribute("src"))
        except:
            pass

        a = self.driver.find_elements_by_tag_name('a')
        for _a in a:
            res.append(_a.get_attribute("href"))

        self.driver.quit()
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
        提取结果链接中可爬取的链接
        :param res:
        :return:
        """
        res = list(set(res))
        new_url = []
        if res:
            for url in res:  # 添加url处理规则
                if not url:
                    continue
                url = url.strip('/').strip('.')
                if url.startswith(' '):
                    url = url[1:]

                if (url.startswith('http://') or url.startswith('https://')) and not url.startswith(self.target):
                    # 其他网站的链接
                    continue
                if url.startswith('ftp://') or url.startswith('mailto:'):
                    # 非web服务
                    continue
                if re.search('\.(css|jpg|JPG|png|pdf|js|gif|xls|doc|docx|rar|ico|ppt)$', url) or re.search('javascript:', url):
                    # 无用文件类型
                    continue
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

        for url in self.url_set:
            print(self.url)
        return self.urls

    def test(self):
        self.init()
        t1 = time.time()
        self.driver.get(self.target)
        t2 = time.time()
        print(t2-t1)
        self.driver.get_screenshot_as_file(r'C:\Code\SiteScan\result\test.png')
        self.driver.close()


if __name__ == '__main__':
    Crawler(target='http://www.jit.edu.cn').scan()
