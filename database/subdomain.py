#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('/home/jasonsheh/Tools/python/SiteScan/db/subdomain.db')
        self.cursor = self.conn.cursor()

    def create_database(self):
        self.cursor.execute('create table result('
                            'id int,'
                            'ip varchar(16), '
                            'url varchar(255) '
                            ')')

        print("create database successfully")

    def insert(self, domains):
        for ip, urls in domains.items():
            for url in urls:
                sql = "insert into result (id, ip, url) " \
                      "values ('%s', '%s', '%s')"\
                      % (1, ip, url)
                self.cursor.execute(sql)
        self.conn.commit()

        self.clean()

    def select(self):
        sql = 'select * from result limit 0,30'
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['ip'] = result[1]
            _result['url'] = result[2]
            _results.append(_result)

        self.clean()

        return _results

    def count(self):
        sql = 'select count(*) from result'
        self.cursor.execute(sql)
        max_page = self.cursor.fetchone()
        return (max_page[0] // 15) + 1

    def clean(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    d = Database()
    # d.select_page(page=1)
    # d.select_detail(_id=10)
    d.create_database()
