#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
import asyncio
from asyncio import Queue
import aiohttp

aiohttp
'''
from database.database import Database
from setting import user_path
'''
sys.path.append('C:\Code\SiteScan')
from setting import user_path
from typing import List, Dict


class SenDir:
    def __init__(self, domains, id=0):
        self.domains: List = domains
        self.id: int = id
        self.thread_num: int = 200
        self.timeout: int = 3
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.queue = Queue(loop=self.loop)
        self.sensitive: Dict = {}
        self.headers: Dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        self.exist_status_code: List[int] = [200, 403]
        self.not_exist_file_type: List[str] = ['', '/', '.config', '.sql', '.inc', '.bak', '.jsp', '.asp', '.aspx', '.php', '.html']

    def enqueue_dir(self):
        with open(user_path+'/dict/dir.txt', 'r') as file:
            for eachline in file:
                for target in self.domains:
                    self.queue.put_nowait(target+eachline.strip())

    def enqueue_error_page(self):
        for target in self.domains:
            url = target + '/.this_page_will_never_exists_lalala'
            self.queue.put_nowait(url)

    async def directory_brute(self):
        '''
        对网站进行敏感目录检测
        :return:
        '''
        while not self.queue.empty():
            url = await self.queue.get()
            sys.stdout.write('\r目录扫描剩余数: ' + str(self.queue.qsize()))
            sys.stdout.flush()
            try:
                async with self.session.get('http://' + url, timeout=3) as r:
                    status_code = r.status
            except aiohttp.client_exceptions.ClientOSError:
                continue
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
            except asyncio.TimeoutError:
                continue
            except AttributeError:
                continue
            if status_code in [200, 403]:
                if url.split('/')[0] not in self.sensitive.keys():
                    self.sensitive[url.split('/')[0]] = [url + '\t' + str(status_code)]
                else:
                    self.sensitive[url.split('/')[0]].append(url + '\t' + str(status_code))

    async def error_page(self):
        '''
        判断有无错误界面，有则把该网站删除列表
        :return:
        '''
        while not self.queue.empty():
            url = await self.queue.get()
            sys.stdout.write('\r错误页面剩余数: ' + str(self.queue.qsize()))
            sys.stdout.flush()
            try:
                async with self.session.get('http://{}'.format(url), timeout=self.timeout) as r:
                    status_code = r.status
            except aiohttp.client_exceptions.ClientOSError:
                self.domains.remove(url.split('/')[0])
                continue
            except aiohttp.client_exceptions.ServerDisconnectedError:
                self.domains.remove(url.split('/')[0])
                continue
            except asyncio.TimeoutError:
                continue

            if status_code in self.exist_status_code:
                self.domains.remove(url.split('/')[0])
                continue

            for not_exist in self.not_exist_file_type:
                url = '{url}/this_page_will_never_exists{ext}'.format(url=url, ext=not_exist)
                try:
                    async with self.session.get('http://{}'.format(url), timeout=self.timeout) as r:
                        status_code = r.status
                except aiohttp.client_exceptions.ClientOSError:
                    self.domains.remove(url.split('/')[0])
                    break
                except aiohttp.client_exceptions.ServerDisconnectedError:
                    self.domains.remove(url.split('/')[0])
                    break
                except asyncio.TimeoutError:
                    self.domains.remove(url.split('/')[0])
                    break
                if status_code in self.exist_status_code:
                    self.domains.remove(url.split('/')[0])
                    break

    async def close(self):
        await self.session.close()

    def run(self):
        print('移除错误页面...')
        self.enqueue_error_page()
        tasks = [self.error_page() for _ in range(self.thread_num)]
        self.loop.run_until_complete(asyncio.wait(tasks))

        print('\n检测敏感目录...')
        self.enqueue_dir()
        tasks = [self.directory_brute() for _ in range(self.thread_num)]
        self.loop.run_until_complete(asyncio.wait(tasks))

        self.loop.run_until_complete(asyncio.wait([self.close()]))
        self.loop.close()

        # Database().insert_sendir(self.sensitive, self.id)
        return self.sensitive


if __name__ == '__main__':
    SenDir(['green.jit.edu.cn', 'www.jit.edu.cn']).run()
