#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('/home/jasonsheh/Tools/python/SiteScan/db/port.db')
        self.cursor = self.conn.cursor()

    def create_database(self):
        self.cursor.execute('create table result('
                            'id integer primary key, '
                            'url varchar(255), '
                            'port varchar(6), '
                            'service varchar(30), '
                            'version varchar(50)'
                            ')')

        print("create database successfully")

    def insert(self, host):
        ip = host.hostname()
        porto = host['porto']
        ports = list(porto.keys())
        ports.sort()
        for port in ports:
            state = porto[port]['state']
            name = porto[port]['name']
            service = porto[port]['product']
            version = porto[port]['version']

            sql = "insert into result (ip, state, name, service, port, version ) " \
                  "values ('%s', '%s', '%s', '%s', '%s', '%s' )"\
                  % (ip, state, name, service, port, version)
            self.cursor.execute(sql)
        self.conn.commit()

        self.clean()

    def select_page(self, page):
        sql = 'select * from result order by id desc limit %s, 15' % str((page-1) * 15)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['url'] = result[1]
            _result['scheme'] = result[2]
            _result['host'] = result[3]
            _result['path'] = result[4]
            _result['port'] = result[5]
            _result['status_code'] = result[6]
            _result['sqli'] = result[7]
            _result['request_header'] = result[8]
            _result['request_body'] = result[9]
            _result['response_header'] = result[10]
            _result['response_body'] = result[11]
            _results.append(_result)

        self.clean()

        return _results

    def select_detail(self, _id):
        sql = 'select * from result where id = %s' % _id
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        _result = {}
        _result['id'] = result[0]
        _result['url'] = result[1]
        _result['scheme'] = result[2]
        _result['host'] = result[3]
        _result['path'] = result[4]
        _result['port'] = result[5]
        _result['status_code'] = result[6]
        _result['sqli'] = result[7]
        _result['request_header'] = result[8]
        _result['request_body'] = result[9]
        _result['response_header'] = result[10]
        _result['response_body'] = result[11]

        self.clean()

        return _result

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
