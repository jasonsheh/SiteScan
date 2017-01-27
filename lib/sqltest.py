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
        self.payload = ' and 1=2'

    def _conn(self):
        try:
            conn = requests.get(self.target + self.payload, timeout=1, allow_redirects=False)
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

    def _scan(self):
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
            conn1 = requests.get(self.target + 'and 1=1', timeout=1, allow_redirects=False)
            if not(15 > len(conn1.content)-len(conn.content) > -15) and self.waf == '':
                return self.target
            else:
                print('不存在注入 防火墙疑似:' + self.waf)
                return False
        except Exception as e:
            print('不存在注入'+str(e))
            return False

    def get_sql_in(self):
        sql_in = []
        res = []
        pattern = re.compile('.*\?.*=\d+')
        pattern2 = re.compile('.*/\d+')
        for target in self.targets:
            res += re.findall(pattern, target)  # 获取所有可能的注入点
            res += re.findall(pattern2, target)
            if res != []:
                flag = 0
                if sql_in == []:
                    sql_in += res
                for _url in sql_in:
                    if urlparse(_url).path == urlparse(res[0]).path:
                        flag = 1
                        break
                if flag == 0:
                    sql_in += res
        self.targets = sql_in

    def run(self):
        print("\n检测SQL注入:")
        results = []
        self.get_sql_in()
        for target in self.targets:
            self.target = target
            result = self._scan()
            if result:
                print('可能存在注入:' + result)
                results += result
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
