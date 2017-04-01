#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import socket
import requests
from urllib.parse import urlparse


class Info:
    def __init__(self, target):
        self.target = target
        self.ip = ''
        self.server = ''

    def get_ip(self):
        try:
            ip = socket.gethostbyname(urlparse(self.target).netloc)  # get ip address
            self.ip = ip
            print('获取ip: ' + self.ip)
        except Exception as e:
            print(e)
            # print(target)

    def get_server(self):
        try:
            r = requests.get(self.target)

            if 'Server' in r.headers:
                self.server = (r.headers['Server'])
            else:
                self.server = 'unknown'

            print('获取服务器信息 ' + self.server)

        except requests.exceptions.ConnectionError:
            print('连接错误')
        except Exception as e:
            print(e)
            # print(target)

    def run(self):
        self.get_ip()
        self.get_server()
        return self.ip, self.server
<<<<<<< HEAD

if __name__ == '__main__':
    s = Info('http://znyywlw.jit.edu.cn')
    s.run()
=======
>>>>>>> b48090a64e299874ab424d042b7633900f626713
