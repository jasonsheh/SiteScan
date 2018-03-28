#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

from setting import user_path


class SaveToFile:
    def __init__(self, target, domains, title, fingerprint, dirs):
        self.target = target
        self.domains = domains
        self.title = title
        self.fingerprint = fingerprint
        self.dirs = dirs

    def save(self):
        with open(user_path+'./result/'+self.target+'.txt', 'w', encoding='utf-8') as file:
            for url, ips in sorted(self.domains.items()):
                file.writelines('\n{}\t{}\n'.format(url, ips))
                if self.fingerprint[url]:
                    file.writelines('\t' + self.fingerprint[url] + '\n')
                if self.title[url]:
                    file.writelines('\t'+self.title[url]+'\n')

                if url in self.dirs.keys():
                    for _dir in self.dirs[url]:
                        file.writelines('\t' + _dir+'\n')
