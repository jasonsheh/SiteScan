#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('/home/jasonsheh/Tools/python/SiteScan/db/SiteScan.db')
        self.cursor = self.conn.cursor()

    def create_database(self):
        self.create_subdomain()
        self.create_port()

    def create_subdomain(self):
        self.cursor.execute('create table subdomain('
                            'id integer primary key,'
                            'ip varchar(16), '
                            'url varchar(255) '
                            ')')

        print("create subdomain successfully")

    def insert_subdomain(self, domains):
        for ip, urls in domains.items():
            for url in urls:
                sql = "insert into subdomain (ip, url) " \
                      "values ('%s', '%s')"\
                      % (ip, url)
                self.cursor.execute(sql)
        self.conn.commit()
        self.clean()

    def select_subdomain(self, page):
        sql = 'select * from subdomain limit %s,15' % ((page-1)*15)
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

    def create_port(self):
        self.cursor.execute('create table port('
                            'id integer primary key, '
                            'url varchar(255), '
                            'port varchar(6), '
                            'service varchar(30), '
                            'version varchar(50)'
                            ')')

        print("create port successfully")

    def insert_port(self, host):
        ip = host.hostname()
        porto = host['porto']
        ports = list(porto.keys())
        ports.sort()
        for port in ports:
            state = porto[port]['state']
            name = porto[port]['name']
            service = porto[port]['product']
            version = porto[port]['version']

            sql = "insert into port (ip, state, name, service, port, version ) " \
                  "values ('%s', '%s', '%s', '%s', '%s', '%s' )"\
                  % (ip, state, name, service, port, version)
            self.cursor.execute(sql)
        self.conn.commit()

    def delete(self, _id, mode):
        self.cursor.execute('delete * from %s where id = %s' % (mode, _id))
        self.conn.commit()
        self.clean()

    def count(self, mode):
        self.cursor.execute('select count(*) from %s' % mode)
        total = self.cursor.fetchone()
        return total[0]

    def clean(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    d = Database()
    # d.select_page(page=1)
    # d.select_detail(_id=10)
    d.create_database()
