#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import socket
import requests


class Info:
    def __init__(self, target):
        self.target = target
        self.ip = ''
        self.server = ''
        self.language = ''

    def get_ip(self):
        try:
            target = self.target[7:]
            self.ip = socket.gethostbyname(target)  # get ip address
            print('\n Ip address: ' + self.ip)
        except Exception as e:
            print(e)

    def get_server(self):
        try:
            r = requests.get(self.target)
            self.server = r.headers['Server']
            print(' HostName:' + self.server)
            if 'X-Powered-By' in r.headers:
                self.language = r.headers['X-Powered-By']  # get language
                print(' ' + self.language)
        except Exception as e:
            print(e)

    def run(self):
        self.get_ip()
        self.get_server()
        return self.ip, self.language, self.server

