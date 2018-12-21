#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
"""
对数据库进行的一系列操作


"""
import sqlite3
from setting import user_path, item_size


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(user_path + '/db/SiteScan.db')
        self.cursor = self.conn.cursor()

    def create_database(self):
        self.create_subdomain()
        self.create_port()
        self.create_sendir()
        self.create_vul()

    def organize_subdomain_data(self, results):
        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'ip': result[1],
                    'url': result[2],
                    'title': result[3],
                    'appname': result[4],
                    'text': result[5],
                    'domain_id': result[6],
                    'src_id': result[7],
                    'is_new': result[8],
                }
            )
        self.clean()
        return results_list

    def select_subdomain_by_domain_id(self, domain_id, page=-1):
        if page == -1:
            sql = "select * from subdomain order by id_new desc where domain_id = ?"
            self.cursor.execute(sql, (domain_id,))
        else:
            sql = "select * from subdomain where domain_id = ? order by id desc limit ?,?"
            self.cursor.execute(sql, (domain_id, (page - 1) * item_size, item_size))

        return self.organize_subdomain_data(self.cursor.fetchall())

    def select_port_by_page(self, page, domain_id):
        sql = "select * from port where domain_id = ? order by id desc limit ?,?"
        self.cursor.execute(sql, (domain_id, (page - 1) * item_size, item_size))
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
                    'domain_id': result[8],
                }
            )

        self.clean()
        return results_list

    def select_sendir_by_page(self, page, domain_id):
        sql = "select * from sendir where domain_id = ? order by id desc limit ?,?"
        self.cursor.execute(sql, (domain_id, (page - 1) * item_size, item_size))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'url': result[1],
                    'status_code': result[2],
                    'domain_id': result[3],
                }
            )

        self.clean()
        return results_list

    def select_vul_by_page(self, page, domain_id):
        sql = "select * from vul where domain_id = ? order by id desc limit ?,?"
        self.cursor.execute(sql, (domain_id, (page - 1) * item_size, item_size))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'url': result[1],
                    'name': result[2],
                    'domain_id': result[3],
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
                            'text TEXT, '
                            'domain_id integer, '
                            'src_id integer, '
                            'is_new char(1)'
                            ')')
        print("create subdomain successfully")

    def insert_subdomain(self, domains, infos, domain_id, src_id):
        subdomains = self.select_subdomain_by_domain_id(domain_id)
        subdomain_list = [x['url'] for x in subdomains]

        self.conn = sqlite3.connect(user_path + '/db/SiteScan.db')
        self.cursor = self.conn.cursor()

        for info in infos:
            ips = ' '.join(domains[info['domain']])
            app = ' '.join(info['app'])
            if info['domain'] in subdomain_list:
                sql = "update subdomain set ip = ?, title = ?, appname = ?, text = ?, is_new = 0"
                self.cursor.execute(sql,
                                    (ips, info['title'], app, info['text']))

            else:
                sql = "insert into subdomain (url, ip, title, appname, text, domain_id, src_id, is_new) values (?, ?, ?, ?, ?, ?, ?, 1)"
                self.cursor.execute(sql,
                                    (info['domain'], ips, info['title'], app, info['text'], domain_id, src_id))
        self.conn.commit()
        self.clean()

    def select_subdomain(self, page):
        sql = "select * from subdomain order by is_new desc, id desc limit ?,?"
        self.cursor.execute(sql, ((page - 1) * item_size, item_size))
        return self.organize_subdomain_data(self.cursor.fetchall())

    def select_subdomain_detail(self, domain_id):
        sql = "select * from subdomain where id = ?"
        self.cursor.execute(sql, (domain_id, ))
        return self.organize_subdomain_data(self.cursor.fetchall())

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
                            'domain_id integer '
                            ')')

        print("create port successfully")

    def insert_port(self, host, url, porto, domain_id=''):
        ports = list(porto.keys())
        ports.sort()
        for port in ports:
            state = porto[port]['state']
            name = porto[port]['name']
            service = porto[port]['product']
            version = porto[port]['version']

            sql = "insert into port (ip, url, port, state, name, service, version, domain_id )" \
                  " values (?, ?, ?, ?, ?, ?, ?, ? )"
            self.cursor.execute(sql, (host, url, port, state, name, service, version, domain_id))
        self.conn.commit()

    def select_port(self, page):
        sql = "select * from port order by id desc limit ?,?"
        self.cursor.execute(sql, ((page - 1) * item_size, item_size))
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
                    'domain_id': result[8],
                }
            )

        self.clean()
        return results_list

    def create_sendir(self):
        self.cursor.execute('create table sendir('
                            'id integer primary key, '
                            'url varchar(255), '
                            'status_code varchar(4), '
                            'domain_id integer '
                            ')')

        print("create sendir successfully")

    def insert_sendir(self, sensitive, domain_id=''):
        for url in sensitive:
            sql = "insert into sendir (url, status_code, domain_id ) values (?, ?, ?)"
            self.cursor.execute(sql, (url, sensitive[url], domain_id))
        self.conn.commit()

    def select_sendir(self, page):
        sql = "select * from sendir order by id desc limit ?,?"
        self.cursor.execute(sql, ((page - 1) * item_size, item_size))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'url': result[1],
                    'status_code': result[2],
                    'domain_id': result[3],
                }
            )

        self.clean()
        return results_list

    def create_vul(self):
        self.cursor.execute('create table vul('
                            'id integer primary key, '
                            'url varchar(255), '
                            'name varchar(64), '
                            'domain_id integer '
                            ')')

        print("create vul successfully")

    def insert_vul(self, urls, name, domain_id=''):
        for url in urls:
            sql = "insert into vul (url, name, domain_id ) values (?, ?, ?)"
            self.cursor.execute(sql, (url, name, domain_id))
        self.conn.commit()

    def select_vul(self, page):
        sql = "select * from vul order by id desc limit ?,?"
        self.cursor.execute(sql, ((page - 1) * item_size, item_size))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'url': result[1],
                    'name': result[2],
                    'domain_id': result[3],
                }
            )

        self.clean()
        return results_list

    def delete(self, domain_id, mode):
        self.cursor.execute('delete from {} where id = ?'.format(mode), (domain_id,))
        self.conn.commit()

        if mode == 'task':
            self.cursor.execute('delete from sendir where domain_id = ?', (domain_id,))
            self.cursor.execute('delete from subdomain where domain_id = ?', (domain_id,))
            self.cursor.execute('delete from port where domain_id = ?', (domain_id,))
            self.cursor.execute('delete from vul where domain_id = ?', (domain_id,))
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

    def count_detail(self, mode, domain_id):
        self.cursor.execute('select count(*) from {} where domain_id = ?'.format(mode), (domain_id,))
        total = self.cursor.fetchone()
        return total[0]

    def clean(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    Database().create_database()
