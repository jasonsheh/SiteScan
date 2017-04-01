#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import requests
import threading
import queue
import time


class Sendir:
    def __init__(self, target):
        self.target = target
        self.q = queue.Queue(0)
        self.thread_num = 3
        self.sensitive = []

    def dirt(self):
        while not self.q.empty():
            try:
                _dir = self.q.get()
                url = self.target + _dir
                r = requests.get(url, timeout=1, allow_redirects=False)

                if r.status_code == 200:
                    self.sensitive.append(url)

                time.sleep(0.1)
            except:
                continue

    def run(self):
        try:
            r = requests.get(self.target, timeout=1, allow_redirects=False)
            print('\n# 检测敏感目录...')
            # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
            # with open('res.txt', 'w+') as file:
                # file.write('sensitive direction:\n\n')

            with open('D:/tools/python/SiteScan/dict/dir.txt', 'r') as file:
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

            if len(self.sensitive) < 20:
                for url in self.sensitive:
                    print(url)
            return self.sensitive
        except:
            print('\n无法检测目录')
            return self.sensitive


def main():
<<<<<<< HEAD
    s = Sendir(target='http://'+'chinac.com/')
=======
    s = Sendir(target='http://'+'oa.meizu.com')
>>>>>>> b48090a64e299874ab424d042b7633900f626713
    s.run()

if __name__ == '__main__':
    main()
