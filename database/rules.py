#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3


class Rules:
    def __init__(self):
        self.conn = sqlite3.connect('/home/jasonsheh/Tools/python/SiteScan/db/Rules.db')
        self.cursor = self.conn.cursor()

    def insert_application(self, app, rule):
        sql = "insert into application (app, rule) " \
              "values ('%s', '%s')"\
              % (app, rule)
        self.cursor.execute(sql)
        self.conn.commit()
        self.clean()

    def select_application(self, page):
        sql = 'select * from application order by id desc limit %s,15' % ((page-1)*15)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['app'] = result[1]
            _result['rule'] = result[2]
            _results.append(_result)

        self.clean()
        return _results

    def count(self, mode):
        self.cursor.execute('select count(*) from %s' % mode)
        total = self.cursor.fetchone()
        return total[0]

    def clean(self):
        self.cursor.close()
        self.conn.close()
