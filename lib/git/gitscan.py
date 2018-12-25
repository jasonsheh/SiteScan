#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import time
import socket
from github import Github, GithubException
from setting import github_api_key
from typing import Dict


# reg_mail = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
# reg_ip = re.compile(r"^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))$")


class GitScan:
    def __init__(self, target: str):
        self.key_num = 0
        self.g = Github(github_api_key[self.key_num])
        self.target: str = target
        self.search_page: int = 1
        self.timeout: int = 5
        self.hash_list = []
        self.result = []
        self.useless_ext = ['css', 'htm', 'html', 'pac', 'csv', 'txt', 'csv.dat', 'rules', 'svg']
        self.useful_ext = ['properties']
        self.keywords: Dict = {
            'jdbc:': 'jdbc:',
            'smtp password': "[(smtp)]?.*?password.*[ a-zA-Z0-9_\"']=[^<]",
            'password=': "password[ a-zA-Z0-9_\"':]+[=][^<]"
        }
        self.false_positive = ['localhost', 'l27.0.0.1']
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

    def get_keyword_code(self, all_codes):
        """
        获取匹配到关键字的代码行
        :param all_codes: 全量代码
        :return: 关键代码
        """
        all_code = all_codes.splitlines()
        possible_codes = []
        for keyword, rule in self.keywords.items():
            for code in all_code:
                if len(code) > 350:
                    continue
                if re.search(rule, code, re.I):
                    possible_codes.append(code.strip())
        possible_codes = list(set(possible_codes))
        removed_code = []
        for possible_code in possible_codes:
            # TODO 127.0.0.1 bug
            for false_positive in self.false_positive:
                if re.search(false_positive, possible_code, re.I):
                    removed_code.append(possible_code)
                    break
        # 移除匹配到false positive的code
        for code in removed_code:
            possible_codes.remove(code)

        return possible_codes

    def switch_api_key(self):
        self.key_num = (self.key_num + 1) % len(github_api_key)
        self.g = Github(github_api_key[self.key_num])
        print(self.key_num)

    def handle_content(self, content):
        if content.sha in self.hash_list:
            return
        self.hash_list.append(content.sha)

        url = content.html_url
        if self.remove_dict_from_repo(url):
            return
        if self.filter(url):
            return

        full_name = content.repository.full_name
        result = {'domain': self.target, 'repository_name': full_name, 'repository_url': url}
        full_code = content.decoded_content.decode('utf-8')

        codes = self.get_keyword_code(full_code)
        if codes:
            result['code'] = "\n".join(codes)
            self.result.append(result)

    def run(self):
        for kw in self.keywords:
            # 每个关键字搜索完成(默认30条)切换api_key
            self.switch_api_key()
            resource = self.g.search_code('{}+{}'.format(self.target, kw), sort="indexed", order="desc")
            for page in range(0, self.search_page):
                try:
                    for index, content in enumerate(resource.get_page(page)):
                        # 处理数据
                        try:
                            # TODO add hash 去重

                            self.handle_content(content)
                        except socket.timeout:
                            time.sleep(self.timeout)
                            continue
                except GithubException as e:
                    print(e)
                    time.sleep(self.timeout)
                    continue
            time.sleep(self.timeout)

        return self.result

    def output(self):
        for result in self.result:
            print(result["repository_name"], result["repository_url"])
            for code in result["code"].split('\n'):
                print("\t"+code)


if __name__ == '__main__':
    g = GitScan('taobao.com')
    for i in range(10):
        g.switch_api_key()
