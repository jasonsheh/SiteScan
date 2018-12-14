#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import requests
from typing import List


class Redirect:
    def __init__(self, url):
        self.target: str = url
        self.redirect_keyword_list: List[str] = ["url", "redirect", "goto"]
        self.compare_url: str = "https://www.baidu.com"
        self.redirect_url: str = "http://www.qq.com_521_qq_diao_yu_wangzhan_789.com"

    def scan(self):
        for evil_url in self.insert_payload():
            redirect_resp = requests.get(evil_url)
            if self.compare_url == redirect_resp.url:
                print("存在重定向漏洞: ", evil_url)

    def insert_payload(self):
        evil_url_list = []

        params = self.target.split('?')[-1].split('&')
        for param in params:
            for redirect_keyword in self.redirect_keyword_list:
                if re.search(re.compile(redirect_keyword, re.I), param):
                    evil_param = param.split('=')[0]+'='+self.compare_url
                    evil_url_list.append(self.target.replace(param, evil_param))
                    break
        return evil_url_list


if __name__ == '__main__':
    # Redirect("http://www.iikx.com/e/extend/jump/?url=http://prism.osapublishing.org/Account/").scan()
    Redirect("https://m.ly.com//passport/logout.html?returnUrl=https://www.baidu.com").scan()
