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
                '''sys.stdout.write('# 剩余目录个数' + str(self.q.qsize()) + '\r')
                sys.stdout.flush()'''
                _dir = self.q.get()
                url = self.target + _dir
                r = requests.get(url, timeout=1, allow_redirects=False)

                if r.status_code == 200:
                    # with open('res.txt', 'w+') as file:
                        # file.write(url + '\n')
                    self.sensitive.append(url)

                time.sleep(0.1)
            except:
                continue

    def run(self):
        print('\n检测敏感目录...')
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        # with open('res.txt', 'w+') as file:
            # file.write('sensitive direction:\n\n')

        with open('D:/tools/python/SiteScan/dict/dir.txt', 'r') as file:
            for eachline in file:
                self.q.put(eachline.strip())

        try:
            threads = []
            for i in range(int(self.thread_num)):
                t = threading.Thread(target=self.dirt)
                threads.append(t)
            for item in threads:
                item.start()

            for item in threads:
                item.join()
            print('\n')
        except Exception as e:
            print(e)

        if len(self.sensitive) <20:
            for url in self.sensitive:
                print(url)

        return self.sensitive


def main():
    s = Sendir(target='http://'+'m2.wxfenxiao.com')
    s.run()

if __name__ == '__main__':
    main()
