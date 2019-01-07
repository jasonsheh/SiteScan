#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import time
import datetime
import requests
import socket
from github import Github, GithubException
from setting import github_api_key
from typing import Dict
from database.gitLeak import GitLeak


# reg_mail = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')


class GitScan:
    # TODO 也许会增加机器学习来判断是否为真正的信息泄露
    def __init__(self, target: str):
        self.key_num = 0
        self.g = Github(github_api_key[self.key_num])
        self.target: str = target
        self.search_page: int = 1
        self.timeout: int = 4
        self.hash_list = []
        self.result = []
        self.useless_ext = ['css', 'htm', 'html', 'pac', 'csv', 'txt', 'csv.dat', 'rules', 'svg']
        self.useful_ext = ['properties']

        # TODO More Rules
        # TODO single database
        self.keywords: Dict = {
            'jdbc:': 'jdbc:/.*/',
            'smtp password': "[(smtp)]?.*?password[^,./ ]?[a-zA-Z0-9_\"':]*[ ]*[=:][^<]*",
            'password': "password[^,/ ]?[a-zA-Z0-9_\"':]*[ ]*[=:][^<]*",
            'passwd': "passwd[^,/ ]?[a-zA-Z0-9_\"':]*[ ]*[=:][^<]*",
        }
        self.false_positive = [r"\(\)[;,]?$", r"\*{6}", "changeit", "type: ss, server:"]
        self.fuzz_repo_name = ['fuzz', 'hack', 'whitelist', 'blacklist', '.github.io']
        self.fuzz_file_name = ["Surge3.conf"]

        self.reg_domain = r"[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+"
        self.reg_ip = r"((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))"
        self.reg_private_ip = r"(127\.)|(192\.168\.)|(10\.)|(172\.1[6-9]\.)|(172\.2[0-9]\.)|(172\.3[0-1]\.)|(localhost)"

    # 移除无用的文件类型
    def filter(self, url):
        # 是否应该被过滤
        for ext in self.useless_ext:
            if url.endswith(ext):
                return True
        return False

    def remove_useless_from_repo(self, name):
        """
        移除Github上 fuzz，字典等相关repo
        :param name: repo url 类似名称
        :return: is_fuzz_or_dict_like bool
        """
        for fuzz_keyword in self.fuzz_repo_name:
            if re.search(fuzz_keyword, name, re.IGNORECASE):
                return True
        for fuzz_keyword in self.fuzz_file_name:
            if re.search(fuzz_keyword, name, re.IGNORECASE):
                return True
        return False

    def switch_api_key(self):
        self.key_num = (self.key_num + 1) % len(github_api_key)
        self.g = Github(github_api_key[self.key_num])

    def handle_content(self, content):
        if content.sha in self.hash_list:
            return
        self.hash_list.append(content.sha)

        url = content.html_url
        if self.remove_useless_from_repo(url):
            return
        if self.filter(url):
            return

        full_name = content.repository.full_name
        update_time = content.repository.updated_at
        update_time_str = update_time.strftime("%Y-%m-%d")
        result = {
            'domain': self.target,
            'repository_name': full_name,
            'repository_url': url,
            "update_time": update_time_str
        }

        # 更新时间不能超过1个月
        if (datetime.datetime.now() - update_time).days > 30:
            return
        try:
            full_code = content.decoded_content.decode('utf-8')
        except requests.exceptions.ConnectionError:
            return

        result["confidence"] = self.confidence(full_code)
        codes = self.get_keyword_code(full_code)
        if codes:
            result['code'] = codes
            self.result.append(result)

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
                if re.search(self.reg_private_ip, code, re.I):
                    is_false_positive = True
                if re.search(rule, code, re.I) and not is_false_positive:
                    possible_codes.append(code.strip())
        return list(set(possible_codes))

    def confidence(self, all_codes):
        """
        实验性的置信度计算函数

        对匹配到的代码进行置信度计算
        计算 出现总IP数量/私有地址
        计算 出现url数量/包含的目标域名
        :param all_codes: 全量代码
        :return: 置信度
        """
        confidence = 0

        all_code = all_codes.splitlines()
        ip_count = 0
        private_ip_count = 0

        url_count = 0
        target_url_count = 0
        for code in all_code:
            # 公有IP出现次数
            if re.search(self.reg_ip, code, re.I):
                ip_count += 1
                if re.search(self.reg_private_ip, code, re.I):
                    private_ip_count += 1

            # url出现次数
            if re.search(self.reg_domain, code, re.I):
                url_count += 1
                if self.target in code:
                    target_url_count += 1
        if ip_count != 0:
            confidence += ((ip_count - private_ip_count) / ip_count)
        if url_count != 0:
            confidence += (target_url_count / url_count)
        return int(round(confidence, 2) * 100)

    def run(self):
        print("scan {}".format(self.target))
        for kw in self.keywords:
            # 每个关键字搜索完成(默认30条)切换api_key
            self.switch_api_key()
            resource = self.g.search_code('"{}"+{}'.format(self.target, kw), sort="indexed", order="desc")
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
                        except requests.exceptions.ReadTimeout:
                            continue
                        except AssertionError:
                            # github library encoding error
                            continue

                except GithubException as e:
                    print(e)
                    time.sleep(self.timeout)
            time.sleep(self.timeout)

        return self.result

    def output(self):
        for result in self.result:
            print(result["repository_name"], result["repository_url"])
            for code in result["code"].split('\n'):
                print("\t" + code)

    @staticmethod
    def clean():
        """
        删除 type == 0 冗余数据
        一周执行一次
        :return:
        """
        GitLeak().delete_leak()


if __name__ == '__main__':
    GitScan("").run()
