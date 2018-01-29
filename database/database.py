#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
"""
对数据库进行的一系列操作


"""
import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('./db/SiteScan.db')
        self.cursor = self.conn.cursor()

    def create_database(self):
        self.create_task()
        self.create_subdomain()
        self.create_port()
        self.create_sendir()
        self.create_finger()
        self.create_vul()

    # 创建任务数据库
    def create_task(self):
        self.cursor.execute('create table task('
                            'id integer primary key,'
                            'name varchar(64) '
                            ')')
        print("create task successfully")

    # 插入任务
    def insert_task(self, name):
        sql = "insert into task (name) values (?)"
        self.cursor.execute(sql, (name, ))
        self.conn.commit()

        sql = "select id from task where name = ?"
        self.cursor.execute(sql, (name, ))
        id = self.cursor.fetchall()
        self.clean()

        return id[0][0]

    def select_task(self, page):
        sql = "select * from task order by id desc limit ?,15"
        self.cursor.execute(sql, ((page-1)*15, ))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['name'] = result[1]
            _results.append(_result)

        self.clean()
        return _results

    def select_task_name(self, id):
        sql = "select * from task where id = ?"
        self.cursor.execute(sql, (id, ))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['name'] = result[1]
            _results.append(_result)

        self.clean()
        return _results[0]['name']

    def select_task_subdomain(self, page, id):
        sql = "select * from subdomain where taskid = ? order by id desc limit ?,15"
        self.cursor.execute(sql, (id, (page-1)*15))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['ip'] = result[1]
            _result['url'] = result[2]
            _result['title'] = result[3]
            _result['appname'] = result[4]
            _result['taskid'] = result[5]
            _results.append(_result)

        self.clean()
        return _results

    def select_task_port(self, page, id):
        sql = "select * from port where taskid = ? order by id desc limit ?,15"
        self.cursor.execute(sql, (id, (page-1)*15))
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
            _result['taskid'] = result[7]
            _results.append(_result)

        self.clean()
        return _results

    def select_task_sendir(self, page, id):
        sql = "select * from sendir where taskid = ? order by id desc limit ?,15"
        self.cursor.execute(sql, (id, (page-1)*15))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['url'] = result[1]
            _result['status_code'] = result[2]
            _result['taskid'] = result[3]
            _results.append(_result)

        self.clean()
        return _results

    def select_task_vul(self, page, id):
        sql = "select * from vul where taskid = ? order by id desc limit ?,15"
        self.cursor.execute(sql, (id, (page-1)*15))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['url'] = result[1]
            _result['name'] = result[2]
            _result['taskid'] = result[3]
            _results.append(_result)

        self.clean()
        return _results

    def create_subdomain(self):
        self.cursor.execute('create table subdomain ('
                            'id integer primary key,'
                            'ip varchar(255), '
                            'url varchar(255), '
                            'title varchar(255), '
                            'appname varchar(255), '
                            'taskid integer '
                            ')')

        print("create subdomain successfully")

    def insert_subdomain(self, domains, title, appname, taskid=''):
        for url, ips in sorted(domains.items()):
            ips = ' '.join(ips)
            sql = "insert into subdomain (url, ip, title, appname, taskid) values (?, ?, ?, ?, ?)"
            self.cursor.execute(sql, (url, ips, title[url], appname[url], taskid))
        self.conn.commit()
        self.clean()

    def select_subdomain(self, page):
        sql = "select * from subdomain order by id desc limit ?,15"
        self.cursor.execute(sql, ((page-1)*15, ))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['ip'] = result[1]
            _result['url'] = result[2]
            _result['title'] = result[3]
            _result['appname'] = result[4]
            _result['taskid'] = result[5]
            _results.append(_result)

        self.clean()
        return _results

    def create_port(self):
        self.cursor.execute('create table port('
                            'id integer primary key, '
                            'ip varchar(255), '
                            'url varchar(255), '
                            'port varchar(6), '
                            'state varchar(10), '
                            'name varchar(10), '
                            'service varchar(40), '
                            'version varchar(40), '
                            'taskid integer '
                            ')')

        print("create port successfully")

    def insert_port(self, host, url, porto, taskid=''):
        ports = list(porto.keys())
        ports.sort()
        for port in ports:
            state = porto[port]['state']
            name = porto[port]['name']
            service = porto[port]['product']
            version = porto[port]['version']

            sql = "insert into port (ip, url, port, state, name, service, version, taskid ) values (?, ?, ?, ?, ?, ?, ?, ? )"
            self.cursor.execute(sql, (host, url, port, state, name, service, version, taskid))
        self.conn.commit()

    def select_port(self, page):
        sql = "select * from port order by id desc limit ?,15"
        self.cursor.execute(sql, ((page-1)*15, ))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['ip'] = result[1]
            _result['url'] = result[2]
            _result['port'] = result[3]
            _result['state'] = result[4]
            _result['name'] = result[5]
            _result['service'] = result[6]
            _result['version'] = result[7]
            _result['taskid'] = result[8]
            _results.append(_result)

        self.clean()
        return _results

    def create_sendir(self):
        self.cursor.execute('create table sendir('
                            'id integer primary key, '
                            'url varchar(255), '
                            'status_code varchar(4), '
                            'taskid integer '
                            ')')

        print("create sendir successfully")

    def insert_sendir(self, sensitive, taskid=''):
        for url in sensitive:
            sql = "insert into sendir (url, status_code, taskid ) values (?, ?, ?)"
            self.cursor.execute(sql, (url, sensitive[url], taskid))
        self.conn.commit()

    def select_sendir(self, page):
        sql = "select * from sendir order by id desc limit ?,15"
        self.cursor.execute(sql, ((page-1)*15, ))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['url'] = result[1]
            _result['status_code'] = result[2]
            _result['taskid'] = result[3]
            _results.append(_result)

        self.clean()
        return _results

    def create_vul(self):
        self.cursor.execute('create table vul('
                            'id integer primary key, '
                            'url varchar(255), '
                            'name varchar(64), '
                            'taskid integer '
                            ')')

        print("create vul successfully")

    def insert_vul(self, urls, name, taskid=''):
        for url in urls:
            sql = "insert into vul (url, name, taskid ) values (?, ?, ?)"
            self.cursor.execute(sql, (url, name, taskid))
        self.conn.commit()

    def select_vul(self, page):
        sql = "select * from vul order by id desc limit ?,15"
        self.cursor.execute(sql, ((page-1)*15, ))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['url'] = result[1]
            _result['name'] = result[2]
            _result['taskid'] = result[3]
            _results.append(_result)

        self.clean()
        return _results

    def create_finger(self):
        self.cursor.execute('create table finger('
                            'id integer primary key, '
                            'url varchar(255), '
                            'appname varchar(255), '
                            'taskid integer '
                            ')')

        print("create finger successfully")

    def insert_finger(self, url, appnames, taskid=''):
        sql = "insert into finger (url, appname, taskid ) values (?, ?, ?)"
        self.cursor.execute(sql, (url, appnames, taskid))
        self.conn.commit()

    def select_finger(self, page):
        sql = "select * from finger order by id desc limit ?,15"
        self.cursor.execute(sql, ((page-1)*15, ))
        results = self.cursor.fetchall()

        _results = []
        for result in results:
            _result = {}
            _result['id'] = result[0]
            _result['url'] = result[1]
            _result['appname'] = result[2]
            _result['taskid'] = result[3]
            _results.append(_result)

        self.clean()
        return _results

    def delete(self, id, mode):
        self.cursor.execute('delete from {} where id = ?'.format(mode), (id, ))
        self.conn.commit()

        if mode == 'task':
            self.cursor.execute('delete from sendir where taskid = ?', (id,))
            self.cursor.execute('delete from subdomain where taskid = ?', (id,))
            self.cursor.execute('delete from port where taskid = ?', (id,))
            self.cursor.execute('delete from finger where taskid = ?', (id,))
            self.cursor.execute('delete from vul where taskid = ?', (id,))
            self.conn.commit()

        self.clean()

    def delete_all(self, mode):
        self.cursor.execute('delete from {}'.format(mode))
        self.conn.commit()
        self.clean()

    def count(self, mode):
        self.cursor.execute('select count(*) from {}'.format(mode))
        total = self.cursor.fetchone()
        return total[0]

    def count_task(self, mode, id):
        self.cursor.execute('select count(*) from {} where taskid = ?'.format(mode), (id, ))
        total = self.cursor.fetchone()
        return total[0]

    def clean(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    Database().create_database()
    # d.insert_subdomain({"te'st.com": '127.0.0.1'}, {"te'st.com": 'test'}, {"te'st.com": 'test'})
