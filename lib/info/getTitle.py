#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import asyncio
from asyncio import Queue
import aiohttp


class GetTitle:
    def __init__(self, domains):
        self.domains = domains
        self.loop = asyncio.get_event_loop()
        self.queue = Queue(loop=self.loop)
        self.thread_num = 100
        self.title = {}

    def run(self):
        print('\n网站标题扫描')
        self.enqueue_title()
        tasks = [self.async_get_title() for _ in range(self.thread_num)]
        self.loop.run_until_complete(asyncio.wait(tasks))
        self.loop.close()

        return self.title

    def enqueue_title(self):
        for url in self.domains:
            self.queue.put_nowait(url)

    async def async_get_title(self):
        while not self.queue.empty():
            url = await self.queue.get()
            if not await self._get_title(url):
                continue

    async def _get_title(self, url):
        try:
            async with aiohttp.request('GET', 'http://' + url) as r:
                text = await r.text()
                encoding = r.get_encoding()
            if not text:
                self.title[url] = ''
                return False
            if not encoding:
                if re.findall('charset=[\'|\"]?(.*?)[\'|\"]', text, re.I | re.S):
                    encoding = re.findall('charset=[\'|\"]?(.*?)[\'|\"]', text, re.I | re.S)[0]
                elif re.findall('encoding=[\'|\"]?(.*?)[\'|\"]?', text, re.I | re.S):
                    encoding = re.findall('encoding=[\'|\"]?(.*?)[\'|\"]', text, re.I | re.S)[0]
                else:
                    self.title[url] = ''
                    return False
            if encoding == 'ISO-8859-1' and re.findall('<title.*?>(.*?)</title.*?>', text, re.I | re.S):
                if re.findall('charset=[\'|\"]?(.*?)[\'|\"]', text, re.I | re.S):
                    encoding = re.findall('charset=[\'|\"]?(.*?)[\'|\"]', text, re.I | re.S)[0]
                elif re.findall('encoding=[\'|\"]?(.*?)[\'|\"]?', text, re.I | re.S):
                    encoding = re.findall('encoding=[\'|\"]?(.*?)[\'|\"]', text, re.I | re.S)[0]
                else:
                    encoding = 'utf-8'
                self.title[url] = re.findall('<title.*?>(.*?)</title.*?>', text, re.I | re.S)[0].encode(
                    "iso-8859-1").decode(encoding).encode('utf-8').decode('utf-8')
                return True
            elif re.findall('<title.*?>(.*?)</title.*?>', text, re.I | re.S) and encoding in [
                'utf-8', 'gb2312', 'GB2312', 'GBK', 'gbk2312', 'gbk']:
                self.title[url] = re.findall('<title.*?>(.*?)</title.*?>', text, re.I | re.S)[0].strip()
                return True
            elif re.findall('<title.*?>(.*?)</title.*?>', r.text, re.I | re.S):
                self.title[url] = re.findall('<title.*?>(.*?)</title.*?>', text, re.I | re.S)[0].encode(
                    r.encoding).decode('utf-8').strip()
                return True
            else:
                self.title[url] = ''
                return True
                # print(url, self.title[url])
        except AttributeError:
            print(url)
            return False
        except LookupError:
            self.title[url] = ''
            return False
        except UnicodeDecodeError:
            self.title[url] = ''
            return False
        except Exception as e:
            self.title[url] = ''
            print(url + '\t' + e)


if __name__ == '__main__':
    title = GetTitle(['octfive.cn']).run()
    print(title)
