#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import requests
import gevent
from gevent.queue import Queue
from gevent import monkey
monkey.patch_all()


class GetTitle:
    def __init__(self, domains):
        self.domains = domains
        self.thread_num = 100
        self.queue = Queue()
        self.title = {}

    def run(self):
        print('\n网站标题扫描')
        self.enqueue_title()
        threads = [gevent.spawn(self.get_title) for _ in range(self.thread_num)]
        gevent.joinall(threads)

        return self.title

    def enqueue_title(self):
        for url in self.domains:
            self.queue.put_nowait(url)

    def get_title(self):
        while not self.queue.empty():
            url = self.queue.get()
            try:
                r = requests.get('http://' + url, timeout=3)
                if not r.text:
                    self.title[url] = ''
                    continue
                if not r.encoding:
                    if re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S):
                        r.encoding = re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    elif re.findall('encoding=[\'|\"]?(.*?)[\'|\"]?', r.text, re.I | re.S):
                        r.encoding = re.findall('encoding=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    else:
                        self.title[url] = ''
                        continue
                if r.encoding == 'ISO-8859-1' and re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S):
                    if re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S):
                        encoding = re.findall('charset=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    elif re.findall('encoding=[\'|\"]?(.*?)[\'|\"]?', r.text, re.I | re.S):
                        encoding = re.findall('encoding=[\'|\"]?(.*?)[\'|\"]', r.text, re.I | re.S)[0]
                    else:
                        encoding = 'utf-8'
                    self.title[url] = re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S)[0].encode(
                        "iso-8859-1").decode(encoding).encode('utf-8').decode('utf-8')
                elif re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S) and r.encoding in [
                    'utf-8', 'gb2312', 'GB2312', 'GBK', 'gbk2312', 'gbk']:
                    self.title[url] = re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S)[0].strip()
                elif re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S):
                    self.title[url] = re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S)[0].encode(
                        r.encoding).decode('utf-8').strip()
                else:
                    self.title[url] = ''
                    # print(url, self.title[url])
            except AttributeError:
                print(url)
                continue
            except LookupError:
                self.title[url] = ''
                continue
            except UnicodeDecodeError:
                self.title[url] = ''
                continue
            except requests.exceptions.ReadTimeout:
                self.title[url] = ''
                continue
            except requests.exceptions.ConnectionError:
                self.title[url] = ''
                continue
            except requests.exceptions.TooManyRedirects:
                self.title[url] = ''
                continue
            except requests.exceptions.ChunkedEncodingError:
                self.title[url] = ''
                continue
            except Exception as e:
                self.title[url] = ''
                print(url + '\t' + e)


if __name__ == '__main__':
    title = GetTitle(['octfive.cn']).run()
    print(title)
