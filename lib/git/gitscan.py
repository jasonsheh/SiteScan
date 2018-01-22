#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import time
import socket
from github import Github, GithubException


reg_mail = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
reg_ip = re.compile(r"^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))$")


class GitScan:
    def __init__(self, keyword):
        self.g = Github("a2601cbe06369ba6f81c4d0a16375a3761b24e79")
        self.keyword = keyword
        self.search_page = 5
        self.hash_list = []
        self.useless_ext = ['css', 'htm', 'html', 'pac', 'csv', 'txt', 'csv.dat', 'rules', 'md']
        self.useful_ext = ['properties']
        self.keywords = ['pwd', 'smtp password', 'admin password']
        self.fuzz_list = ['fuzz', 'dict', 'hack', 'whitelist']
        self.email = ['@163.com']

    # 移除无用的文件类型
    def filter(self, url):
        # 是否应该被过滤
        for ext in self.useless_ext:
            if url.endswith(ext):
                return True
        return False

    # 移除Github上fuzz，字典相关repo
    def remove_dict_from_repo(self, name):
        for fuzz_keyword in self.fuzz_list:
            if re.search(fuzz_keyword, name, re.IGNORECASE):
                return True
        return False

    def get_keyword_code(self, full_code):
        codes = full_code.splitlines()
        key_code = []
        for keyword in self.keywords:
            for code in codes:
                for kw in keyword.split(' '):
                    if re.search(kw, code, re.IGNORECASE) and len(code) < 300:
                        key_code.append(code.strip())
        if len(key_code) > 40:
            return []
        return list(set(key_code))

    def test(self):
        for kw in self.keywords:
            resource = self.g.search_code(self.keyword+' '+kw, sort="indexed", order="desc")
            for page in range(1, self.search_page):
                # You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.
                try:
                    for index, content in enumerate(resource.get_page(page)):
                        if content.sha not in self.hash_list:
                            url = content.html_url
                            full_name = content.repository.full_name

                            self.hash_list.append(content.sha)
                            if self.remove_dict_from_repo(url):
                                continue
                            if self.filter(url):
                                continue

                            try:
                                full_code = content.decoded_content.decode('utf-8')
                            except socket.timeout:
                                print('error', url)
                                continue
                            except GithubException.UnknownObjectException:
                                print('error', url)
                                continue
                            codes = self.get_keyword_code(full_code)
                            mail = re.findall(reg_mail, full_code)
                            ip = re.findall(reg_ip, full_code)
                            print(index, content.html_url)
                            for code in codes:
                                print('\t', code)
                except GithubException.GithubException:
                    time.sleep(5)
                time.sleep(3)


if __name__ == '__main__':
    GitScan('weibo').test()
