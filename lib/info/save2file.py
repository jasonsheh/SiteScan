#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import os
from typing import List, Dict
from setting import user_path


class SaveToFile:
    def __init__(self, domain, domains, info, dirs):
        self.domain: str = domain
        self.domains: Dict = domains
        self.info: List = info
        self.dirs = dirs

    def save(self):
        if not os.path.exists(user_path+'/result'):
            os.mkdir(user_path+'/result')

        with open(user_path+'/result/'+self.domain+'.txt', 'w', encoding='utf-8') as file:
            for info in self.info:
                file.writelines('\n{}\t{}\n'.format(info['domain'], self.domains[info['domain']]))
                file.writelines('\t' + info['title'] + '\n')
                file.writelines('\t'+info['app']+'\n')
