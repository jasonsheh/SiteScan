#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
"""
对数据库进行的一系列操作


"""
import sqlite3
from setting import user_path


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(user_path + '/db/SiteScan.db')
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
        self.cursor.execute(sql, (name,))
        self.conn.commit()

        sql = "select id from task where name = ?"
        self.cursor.execute(sql, (name,))
        task_id = self.cursor.fetchall()
        self.clean()

        return task_id[0][0]

    def select_task(self, page):
        sql = "select * from task order by id desc limit ?,15"
        self.cursor.execute(sql, ((page - 1) * 15,))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'name': result[1]
                }
            )

        self.clean()
        return results_list

    def select_task_name(self, task_id):
        if task_id == -1:
            sql = "select * from task order by id limit 0,1"
            self.cursor.execute(sql)
        else:
            sql = "select * from task where id = ?"
            self.cursor.execute(sql, (task_id,))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'name': result[1]
                }
            )

        self.clean()
        return results_list[0].values()

    def select_task_subdomain(self, page, task_id):
        sql = "select * from subdomain where taskid = ? order by id desc limit ?,15"
        self.cursor.execute(sql, (task_id, (page - 1) * 15))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'ip': result[1],
                    'url': result[2],
                    'title': result[3],
                    'appname': result[4],
                    'taskid': result[5],
                }
            )

        self.clean()
        return results_list

    def select_task_port(self, page, task_id):
        sql = "select * from port where taskid = ? order by id desc limit ?,15"
        self.cursor.execute(sql, (task_id, (page - 1) * 15))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'ip': result[1],
                    'port': result[2],
                    'state': result[3],
                    'name': result[4],
                    'service': result[5],
                    'version': result[6],
                    'taskid': result[7],
                }
            )

        self.clean()
        return results_list

    def select_task_sendir(self, page, task_id):
        sql = "select * from sendir where taskid = ? order by id desc limit ?,15"
        self.cursor.execute(sql, (task_id, (page - 1) * 15))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'url': result[1],
                    'status_code': result[2],
                    'taskid': result[3],
                }
            )

        self.clean()
        return results_list

    def select_task_vul(self, page, task_id):
        sql = "select * from vul where taskid = ? order by id desc limit ?,15"
        self.cursor.execute(sql, (task_id, (page - 1) * 15))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'url': result[1],
                    'name': result[2],
                    'taskid': result[3],
                }
            )

        self.clean()
        return results_list

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

    def insert_subdomain(self, domains, title, appname, task_id=''):
        for url, ips in sorted(domains.items()):
            ips = ' '.join(ips)
            sql = "insert into subdomain (url, ip, title, appname, taskid) values (?, ?, ?, ?, ?)"
            self.cursor.execute(sql, (url, ips, title[url], appname[url], task_id))
        self.conn.commit()
        self.clean()

    def select_subdomain(self, page):
        sql = "select * from subdomain order by id desc limit ?,15"
        self.cursor.execute(sql, ((page - 1) * 15,))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'ip': result[1],
                    'url': result[2],
                    'title': result[3],
                    'appname': result[4],
                    'taskid': result[5],
                }
            )

        self.clean()
        return results_list

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

    def insert_port(self, host, url, porto, task_id=''):
        ports = list(porto.keys())
        ports.sort()
        for port in ports:
            state = porto[port]['state']
            name = porto[port]['name']
            service = porto[port]['product']
            version = porto[port]['version']

            sql = "insert into port (ip, url, port, state, name, service, version, taskid )" \
                  " values (?, ?, ?, ?, ?, ?, ?, ? )"
            self.cursor.execute(sql, (host, url, port, state, name, service, version, task_id))
        self.conn.commit()

    def select_port(self, page):
        sql = "select * from port order by id desc limit ?,15"
        self.cursor.execute(sql, ((page - 1) * 15,))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'ip': result[1],
                    'url': result[2],
                    'port': result[3],
                    'state': result[4],
                    'name': result[5],
                    'service': result[6],
                    'version': result[7],
                    'taskid': result[8],
                }
            )

        self.clean()
        return results_list

    def create_sendir(self):
        self.cursor.execute('create table sendir('
                            'id integer primary key, '
                            'url varchar(255), '
                            'status_code varchar(4), '
                            'taskid integer '
                            ')')

        print("create sendir successfully")

    def insert_sendir(self, sensitive, task_id=''):
        for url in sensitive:
            sql = "insert into sendir (url, status_code, taskid ) values (?, ?, ?)"
            self.cursor.execute(sql, (url, sensitive[url], task_id))
        self.conn.commit()

    def select_sendir(self, page):
        sql = "select * from sendir order by id desc limit ?,15"
        self.cursor.execute(sql, ((page - 1) * 15,))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'url': result[1],
                    'status_code': result[2],
                    'taskid': result[3],
                }
            )

        self.clean()
        return results_list

    def create_vul(self):
        self.cursor.execute('create table vul('
                            'id integer primary key, '
                            'url varchar(255), '
                            'name varchar(64), '
                            'taskid integer '
                            ')')

        print("create vul successfully")

    def insert_vul(self, urls, name, task_id=''):
        for url in urls:
            sql = "insert into vul (url, name, taskid ) values (?, ?, ?)"
            self.cursor.execute(sql, (url, name, task_id))
        self.conn.commit()

    def select_vul(self, page):
        sql = "select * from vul order by id desc limit ?,15"
        self.cursor.execute(sql, ((page - 1) * 15,))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'url': result[1],
                    'name': result[2],
                    'taskid': result[3],
                }
            )

        self.clean()
        return results_list

    def create_finger(self):
        self.cursor.execute('create table finger('
                            'id integer primary key, '
                            'url varchar(255), '
                            'appname varchar(255), '
                            'taskid integer '
                            ')')

        print("create finger successfully")

    def insert_finger(self, url, app_names, task_id=''):
        sql = "insert into finger (url, appname, taskid ) values (?, ?, ?)"
        self.cursor.execute(sql, (url, app_names, task_id))
        self.conn.commit()

    def select_finger(self, page):
        sql = "select * from finger order by id desc limit ?,15"
        self.cursor.execute(sql, ((page - 1) * 15,))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'url': result[1],
                    'appname': result[2],
                    'taskid': result[3],
                }
            )

        self.clean()
        return results_list

    def delete(self, task_id, mode):
        self.cursor.execute('delete from {} where id = ?'.format(mode), (task_id,))
        self.conn.commit()

        if mode == 'task':
            self.cursor.execute('delete from sendir where taskid = ?', (task_id,))
            self.cursor.execute('delete from subdomain where taskid = ?', (task_id,))
            self.cursor.execute('delete from port where taskid = ?', (task_id,))
            self.cursor.execute('delete from finger where taskid = ?', (task_id,))
            self.cursor.execute('delete from vul where taskid = ?', (task_id,))
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

    def count_task(self, mode, task_id):
        self.cursor.execute('select count(*) from {} where taskid = ?'.format(mode), (task_id,))
        total = self.cursor.fetchone()
        return total[0]

    def clean(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    Database().create_database()
