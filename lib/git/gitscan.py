#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import time
import socket
from github import Github, GithubException
from setting import github_api_key


# reg_mail = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
# reg_ip = re.compile(r"^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))$")


class GitScan:
    def __init__(self, target: str):
        self.key_num = 0
        self.g = Github(github_api_key[self.key_num])
        self.target: str = target
        self.search_page: int = 1
        self.timeout: int = 10
        self.hash_list = []
        self.useless_ext = ['css', 'htm', 'html', 'pac', 'csv', 'txt', 'csv.dat', 'rules', 'svg']
        self.useful_ext = ['properties']
        # self.keywords = ['jdbc:', 'smtp password', 'password=']
        self.keywords = {'jdbc:': 'jdbc:',
                         'smtp password': "[(smtp)]?.*?password.*[^>]=[^<]",
                         'password=': "password.*[=]"}
        # self.keywords = ['password =']

        self.fuzz_repo_keyword = ['fuzz', 'hack', 'whitelist', 'blacklist']

    # 移除无用的文件类型
    def filter(self, url):
        # 是否应该被过滤
        for ext in self.useless_ext:
            if url.endswith(ext):
                return True
        return False

    def remove_dict_from_repo(self, name):
        """
        移除Github上 fuzz，字典等相关repo
        :param name: repo url 类似名称
        :return: is_fuzz_or_dict_like bool
        """
        for fuzz_keyword in self.fuzz_repo_keyword:
            if re.search(fuzz_keyword, name, re.IGNORECASE):
                return True
        return False

    def get_keyword_code(self, full_code):
        """
        获取匹配到关键字的代码行
        :param full_code: 全量代码
        :return: 关键代码
        """
        codes = full_code.splitlines()
        key_code = []
        for keyword, rule in self.keywords.items():
            # for k in keyword.split(' '):
            #     if k == '':
            #         continue
            for code in codes:
                if re.search(rule, code, re.I) and len(code) < 300:
                    key_code.append(code.strip())
        return list(set(key_code))

    def switch_api_key(self):
        self.key_num = (self.key_num + 1) // len(github_api_key)
        self.g = Github(github_api_key[self.key_num])

    def test(self):
        for kw in self.keywords:
            resource = self.g.search_code('{}+{}'.format(self.target, kw), sort="indexed", order="desc")
            print(resource.totalCount)
            for page in range(0, self.search_page):
                try:
                    for index, content in enumerate(resource.get_page(page)):
                        if content.sha in self.hash_list:
                            continue
                        url = content.html_url
                        full_name = content.repository.full_name

                        self.hash_list.append(content.sha)
                        if self.remove_dict_from_repo(url):
                            continue
                        if self.filter(url):
                            continue

                        full_code = content.decoded_content.decode('utf-8')

                        codes = self.get_keyword_code(full_code)
                        if codes:
                            print(index, content.html_url, full_name)
                            for code in codes:
                                print('\t', code)
                except GithubException as e:
                    print(e)
                    time.sleep(5)
                    continue
                time.sleep(self.timeout)
            # 每个关键字搜索完成(默认30页)切换api_key
            self.switch_api_key()


if __name__ == '__main__':
    GitScan('youdao.com').test()
