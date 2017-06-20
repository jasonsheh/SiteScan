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
        # self.create_port()
        # self.create_sendir()
        # self.create_finger()

    def create_task(self):
        self.cursor.execute('create table task('
                            'id integer primary key,'
                            'name varchar(64)'
                            ')')

        print("create task successfully")

    def insert_task(self, name):
        sql = "insert into task (name) " \
              "values ('%s')"\
              % (name)
        self.cursor.execute(sql)
        self.conn.commit()
        self.clean()

    def select_task(self, page):
        sql = 'select * from task order by id desc limit %s,15' % ((page-1)*15)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['name'] = result[1]
            _results.append(_result)

        self.clean()
        return _results

    def create_subdomain(self):
        self.cursor.execute('create table subdomain('
                            'id integer primary key,'
                            'taskid integer, '
                            'ip varchar(16), '
                            'url varchar(255), '
                            'title varchar(255), '
                            'appname varchar(255)'
                            ')')

        print("create subdomain successfully")

    def insert_subdomain(self, domains, title, appname):
        for ip, urls in sorted(domains.items()):
            if urls:
                for url in urls:
                    sql = "insert into subdomain (ip, url, title, appname) " \
                          "values ('%s', '%s', '%s', '%s')"\
                          % (ip, url, title[url], appname[url])
                    self.cursor.execute(sql)
        self.conn.commit()
        self.clean()

    def select_subdomain(self, page):
        sql = 'select * from subdomain order by id desc limit %s,15' % ((page-1)*15)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['ip'] = result[1]
            _result['url'] = result[2]
            _result['title'] = result[3]
            _result['appname'] = result[4]
            _results.append(_result)

        self.clean()
        return _results

    def create_port(self):
        self.cursor.execute('create table port('
                            'id integer primary key, '
                            'taskid integer, '
                            'ip varchar(255), '
                            'port varchar(6), '
                            'state varchar(10), '
                            'name varchar(10), '
                            'service varchar(40), '
                            'version varchar(40)'
                            ')')

        print("create port successfully")

    def insert_port(self, host, porto):
        ports = list(porto.keys())
        ports.sort()
        for port in ports:
            state = porto[port]['state']
            name = porto[port]['name']
            service = porto[port]['product']
            version = porto[port]['version']

            sql = "insert into port (ip, port, state, name, service, version ) " \
                  "values ('%s', '%s', '%s', '%s', '%s', '%s' )"\
                  % (host, port, state, name, service, version)
            self.cursor.execute(sql)
        self.conn.commit()

    def select_ports(self, page):
        sql = 'select * from port order by id desc limit %s,15' % ((page-1)*15)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['ip'] = result[1]
            _result['port'] = result[2]
            _result['state'] = result[3]
            _result['name'] = result[4]
            _result['service'] = result[5]
            _result['version'] = result[6]
            _results.append(_result)

        self.clean()
        return _results

    def create_sendir(self):
        self.cursor.execute('create table sendir('
                            'id integer primary key, '
                            'taskid integer, '
                            'url varchar(255) '
                            ')')

        print("create port successfully")

    def insert_sendir(self, urls):
        for url in urls:
            sql = "insert into sendir (url ) " \
                  "values ('%s')" \
                  % (url)
            self.cursor.execute(sql)
        self.conn.commit()

    def select_sendir(self, page):
        sql = 'select * from sendir order by id desc limit %s,15' % ((page-1)*15)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['url'] = result[1]
            _results.append(_result)

        self.clean()
        return _results

    def create_finger(self):
        self.cursor.execute('create table finger('
                            'id integer primary key, '
                            'taskid integer, '
                            'url varchar(255), '
                            'appname varchar(255)'
                            ')')

        print("create finger successfully")

    def insert_finger(self, url, appnames):
        sql = "insert into finger (url, appname ) " \
              "values ('%s', '%s')" \
              % (url, appnames)
        self.cursor.execute(sql)
        self.conn.commit()

    def select_finger(self, page):
        sql = 'select * from finger order by id desc limit %s,15' % ((page-1)*15)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['url'] = result[1]
            _result['appname'] = result[1]
            _results.append(_result)

        self.clean()
        return _results

    def delete(self, id, mode):
        self.cursor.execute('delete from %s where id = %s' % (mode, id))
        self.conn.commit()
        self.clean()

    def delete_all(self, mode):
        self.cursor.execute('delete from %s' % mode)
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
    # d.delete_all('subdomain')
