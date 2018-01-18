#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import time
from github import Github


reg_mail = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
reg_ip = re.compile(r"^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))$")


class GitScan:
    def __init__(self, keyword):
        self.g = Github("your key")
        self.keyword = keyword
        self.hash_list = []
        self.useless_ext = ['css', 'htm', 'html']
        self.keywords = ['password', '@163.com']
        self.email = ['@163.com']

    def filter(self, url):
        # 是否应该被过滤
        for ext in self.useless_ext:
            if url.endswith(ext):
                return True
        return False

    def get_keyword_code(self, full_code):
        codes = full_code.splitlines()
        key_code = []
        for keyword in self.keywords:
            for code in codes:
                if re.search(keyword, code, re.IGNORECASE) or re.search(self.keyword, code, re.IGNORECASE):
                    key_code.append(code.strip())
        return key_code

    def test(self):
        for kw in self.keywords:
            resource = self.g.search_code(self.keyword+' '+kw, sort="indexed", order="desc")
            for index, content in enumerate(resource.get_page(1)):
                if content.sha not in self.hash_list:
                    url = content.html_url
                    self.hash_list.append(content.sha)
                    if self.filter(url):
                        continue
                    # full_name = content.repository.full_name
                    full_code = content.decoded_content.decode('utf-8')
                    code = self.get_keyword_code(full_code)
                    mail = re.findall(reg_mail, full_code)
                    ip = re.findall(reg_ip, full_code)
                    print(index, content.html_url)
                    print(index, code)
                    if mail:
                        print(mail)
                    if ip:
                        print(ip)
            time.sleep(3)


if __name__ == '__main__':
    GitScan('tuniu').test()
