#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-
"""
对数据库进行的一系列操作


"""
from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from setting import user_path, item_size

Base = declarative_base()


class SubDomain(Base):
    __tablename__ = "subdomain"

    id = Column(Integer, primary_key=True)
    ip = Column(String(255))
    domain = Column(String(255))
    title = Column(String(255))
    appname = Column(String(255))
    text = Column(Text)
    domain_id = Column(Integer)
    src_id = Column(Integer)
    is_new = Column(String(1))

    def format(self):
        return {
            "id": self.id,
            "ip": self.ip,
            "domain": self.domain,
            "title": self.title,
            "appname": self.appname,
            "text": self.text,
            "domain_id": self.domain_id,
            "src_id": self.src_id,
            "is_new": self.is_new
        }


class Port(Base):
    __tablename__ = "port"

    id = Column(Integer, primary_key=True)
    ip = Column(String(255))
    url = Column(String(255))
    port = Column(String(7))
    state = Column(String(15))
    name = Column(String(15))
    service = Column(String(64))
    version = Column(String(64))
    domain_id = Column(Integer)

    def format(self):
        return {
            "id": self.id,
            "ip": self.ip,
            "url": self.url,
            "port": self.port,
            "state": self.state,
            "name": self.name,
            "service": self.service,
            "version": self.version,
            "domain_id": self.domain_id
        }


class SenDir(Base):
    __tablename__ = "sendir"

    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    status_code = Column(String(4))
    domain_id = Column(Integer)

    def format(self):
        return {
            "id": self.id,
            "url": self.url,
            "status_code": self.status_code,
            "domain_id": self.domain_id
        }


class Vul(Base):
    __tablename__ = "vul"

    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    name = Column(String(64))
    domain_id = Column(Integer)

    def format(self):
        return {
            "id": self.id,
            "url": self.url,
            "name": self.name,
            "domain_id": self.domain_id
        }


class Database:
    def __init__(self):
        # TODO 增加setting文件中，数据库类型的选择
        self.engine = create_engine(
            "sqlite:///{user_path}/db/SiteScan.db?check_same_thread=False".format(user_path=user_path))
        self.session = sessionmaker(bind=self.engine)()

    def create_database(self):
        Base.metadata.create_all(self.engine)

    def select_mode_by_domain_id(self, mode, page, domain_id):

        mode_dict = {
            "subdomain": SubDomain,
            "port": Port,
            "sendir": SenDir,
            "vul": Vul,
        }

        results = self.session.query(mode_dict[mode]).filter_by(domain_id=domain_id).order_by(
            mode_dict[mode].id.desc()).limit(item_size).offset((page - 1) * item_size).all()

        results_list = []
        for result in results:
            results_list.append(result.format())
        return results_list

    def insert_subdomain(self, domains, infos, domain_id, src_id):
        subdomains = self.session.query(SubDomain).filter_by(domain_id=domain_id).all()
        subdomain_list = [x.domain for x in subdomains]

        for info in infos:
            ips = ' '.join(domains[info['domain']])
            app = ' '.join(info['app'])
            if info['domain'] in subdomain_list:
                subdomain = self.session.query(SubDomain).filter_by(domain=info['domain'])
                subdomain.ip = ips
                subdomain.title = info['title']
                subdomain.appname = app
                subdomain.text = info['text']
                subdomain.is_new = 0
                self.session.commit()
            else:
                subdomain = SubDomain(url=info['domain'], ip=ips, title=info['title'], appname=app, text=info['text'],
                                      domain_id=domain_id, src_id=src_id, is_new=1)
                self.session.add(subdomain)
                self.session.commit()

    def select_subdomain_detail(self, domain_id):
        results = self.session.query(SubDomain).filter_by(id=domain_id).all()
        results_list = []
        for result in results:
            results_list.append(result.format())
        return results_list

    def insert_port(self, host, url, porto, domain_id=''):
        ports = list(porto.keys())
        ports.sort()
        for port in ports:
            state = porto[port]['state']
            name = porto[port]['name']
            service = porto[port]['product']
            version = porto[port]['version']

            port = Port(ip=host, url=url, port=port, state=state, name=name, service=service, version=version,
                        domain_id=domain_id)
            self.session.add(port)
        self.session.commit()

    def select_mode(self, mode, page):
        mode_dict = {
            "subdomain": SubDomain,
            "port": Port,
            "sendir": SenDir,
            "vul": Vul,
        }
        if mode == "subdomain":
            results = self.session.query(mode_dict[mode]).order_by(SubDomain.is_new.desc()).order_by(
                mode_dict[mode].id.desc()).limit(item_size).offset((page - 1) * item_size).all()
        else:
            results = self.session.query(mode_dict[mode]).order_by(mode_dict[mode].id.desc()).limit(item_size).offset(
                (page - 1) * item_size).all()

        results_list = []
        for result in results:
            results_list.append(result.format())
        return results_list

    def insert_sendir(self, sensitive, domain_id=''):
        for url in sensitive:
            sendir = SenDir(url=url, status_code=sensitive[url], domain_id=domain_id)
            self.session.add(sendir)
        self.session.commit()

    def insert_vul(self, urls, name, domain_id=''):
        for url in urls:
            vul = Vul(url=url, name=name, domain_id=domain_id)
            self.session.add(vul)
        self.session.commit()

    # def delete(self, domain_id, mode):
    #     self.cursor.execute('delete from {} where id = ?'.format(mode), (domain_id,))
    #     self.conn.commit()
    #
    #     if mode == 'task':
    #         self.cursor.execute('delete from sendir where domain_id = ?', (domain_id,))
    #         self.cursor.execute('delete from subdomain where domain_id = ?', (domain_id,))
    #         self.cursor.execute('delete from port where domain_id = ?', (domain_id,))
    #         self.cursor.execute('delete from vul where domain_id = ?', (domain_id,))
    #         self.conn.commit()

    def count(self, mode, domain_id=None):
        mode_dict = {
            "subdomain": SubDomain,
            "port": Port,
            "sendir": SenDir,
            "vul": Vul,
        }
        if domain_id:
            total = self.session.query(func.count(mode_dict[mode].id)).filter(
                mode_dict[mode].domain_id == domain_id).scalar()
        else:
            total = self.session.query(func.count(mode_dict[mode].id)).scalar()
        return total

    def clean(self):
        self.session.close()


if __name__ == '__main__':
    Database().create_database()
