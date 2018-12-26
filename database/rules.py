#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3
from setting import user_path, item_size


class Rules:
    def __init__(self):
        self.conn = sqlite3.connect(user_path + '/db/Rules.db')
        self.cursor = self.conn.cursor()

    def insert_fingerprint(self, name, rule):
        sql = "insert into fingerprint (name, rule) " \
              "values ('%s', '%s')"\
              % (name, rule)
        self.cursor.execute(sql)
        self.conn.commit()

    def update_fingerprint(self, name, rule):
        sql = "update fingerprint set rule = ? where name = ? "
        self.cursor.execute(sql, (rule, name))
        self.conn.commit()

    def select_fingerprint(self, page):
        sql = "select * from fingerprint order by id desc limit ?, ?"
        self.cursor.execute(sql, ((page-1)*item_size, item_size))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'name': result[1],
                    'rule': result[2]
                }
            )

        return results_list

    def delete(self, id):
        sql = "delete from where id = ? "
        self.cursor.execute(sql, (id, ))
        self.conn.commit()

    def count(self, mode):
        self.cursor.execute('select count(*) from %s' % mode)
        total = self.cursor.fetchone()
        return total[0]

    def clean(self):
        self.cursor.close()
        self.conn.close()
