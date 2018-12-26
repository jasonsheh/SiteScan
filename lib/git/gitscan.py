#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import time
import datetime
import socket
from github import Github, GithubException
from setting import github_api_key
from typing import Dict
from database.gitLeak import GitLeak


# reg_mail = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
# reg_ip = re.compile(r"^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))$")


class GitScan:
    # TODO 也许会增加机器学习来判断是否为真正的信息泄露
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

        # TODO More Rules
        self.keywords: Dict = {
            'jdbc:': 'jdbc:/.*/',
            'smtp password': "[(smtp)]?.*?password.*[ a-zA-Z0-9_\"']*=[^<]",
            'password=': "password.*[ a-zA-Z0-9_\"':]+[=][^<]"
        }
        self.false_positive = ['localhost', '127.0.0.1']
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
                is_false_positive = False
                for false_positive in self.false_positive:
                    if re.search(false_positive, code, re.I):
                        is_false_positive = True
                        break
                if re.search(rule, code, re.I) and not is_false_positive:
                    possible_codes.append(code.strip())
        return list(set(possible_codes))

    def confidence(self):
        """
        对匹配到的代码进行置信度计算
        :return:
        """
        # TODO confidence
        pass

    def switch_api_key(self):
        self.key_num = (self.key_num + 1) % len(github_api_key)
        self.g = Github(github_api_key[self.key_num])

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
        update_time = content.repository.updated_at
        update_time = datetime.datetime.strptime(update_time, '%a %d %b %Y %H:%M:%S GMT')
        update_time = update_time.strftime("%Y-%m-%d")
        # TODO 数据库增加最后更新日期字段
        result = {'domain': self.target, 'repository_name': full_name, 'repository_url': url, "update_time": update_time}
        full_code = content.decoded_content.decode('utf-8')

        codes = self.get_keyword_code(full_code)
        if codes:
            result['code'] = "\n".join(codes)
            self.result.append(result)

    def run(self):
        print("scan {}".format(self.target))
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
                        except AssertionError:
                            # github library encoding error
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

    @staticmethod
    def clean():
        """
        删除 type == 0 冗余数据
        一周执行一次
        :return:
        """
        GitLeak().delete_leak()


if __name__ == '__main__':
    GitScan("bilibili.com").run()
