#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import re


class Sql:
    def __init__(self, target):
        self.target = target
        self.waf = ''
        self.payload = ' and 1=5'

    def _conn(self):
        try:
            conn = requests.get(self.target + self.payload, timeout=1)
            if conn.status_code == 500:
                print("服务器错误!")
                return False
            if conn.status_code == 406:
                print("无法接受!")
                return False
            if conn.status_code == 302:
                print("重定向错误!")
                return False
            if conn.status_code != 200:
                print("连接错误，响应码为%s" % conn.status_code)
                return False
            else:
                return conn
        except Exception as e:
            print('无法连接 错误为:%s' % e)
            return False

    def waf_scan(self):
        try:
            conn = self._conn()
            if conn == False:
                return False
            else:
                if 'www.safedog.cn' in conn.text:
                    self.waf = '安全狗'
                elif 'safe.webscan.360.cn' in conn.text:
                    self.waf = '360'
                elif 'www.yunsuo.com.cn' in conn.text:
                    self.waf = '云锁'
                elif 'D盾' in conn.text:
                    self.waf = 'D盾'
                elif 'yundun' in conn.text:
                    self.waf = '云盾'
                elif '深空Web应用' in conn.text:
                    self.waf = '深空Web'
                elif '玄武盾' in conn.text:
                    self.waf = '玄武盾'
                elif len(conn.content) < 1000:
                    self.waf = '可能存在'
                else:
                    self.waf = ''
            conn1 = requests.get(self.target + 'and 1=1', timeout=1)
            if not(15 > len(conn1.content)-len(conn.content) > -15) and self.waf == '':
                return self.target
            else:
                print('不存在注入 防火墙疑似:' + self.waf)
                return False
        except Exception as e:
            print('不存在注入'+str(e))
            return False


def main():
        with open('baidu/2.txt', 'r') as file:
            with open('sql/1.txt', 'a+') as sql_file:
                for eachline in file:
                    target = eachline.strip()
                    try:
                        s = Sql(target)
                        target1 = s.waf_scan()
                        if target1:
                            print('可能存在注入')
                            sql_file.write(target1 + '\n')
                    except Exception as e:
                        print(e)


if __name__ == '__main__':
    main()
