#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-


from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from setting import user_path, item_size

Base = declarative_base()


class FingerPrint(Base):
    __tablename__ = "fingerprint"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    rule = Column(Text)

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "rule": self.rule,
        }


class Rules:
    def __init__(self):
        self.engine = create_engine(
            "sqlite:///{user_path}/db/Rules.db?check_same_thread=False".format(user_path=user_path))
        # self.conn = sqlite3.connect(user_path + '/db/Rules.db', check_same_thread=False)
        self.session = sessionmaker(bind=self.engine)()

    def insert_fingerprint(self, name, rule):
        fingerprint = FingerPrint(name=name, rule=rule)
        self.session.add(fingerprint)
        self.session.commit()

    def update_fingerprint(self, name, rule):
        fingerprint = self.session.query(FingerPrint).filter_by(name=name)
        fingerprint.rule = rule
        self.session.commit()

    def select_fingerprint(self, page):
        results = self.session.query(FingerPrint).order_by(FingerPrint.id.desc()).limit(item_size).offset(
            (page - 1) * item_size).all()

        results_list = []
        for result in results:
            results_list.append(result.format())

        return results_list

    def delete(self, id):
        result = self.session.query(FingerPrint).filter_by(id=id)
        self.session.delete(result)
        self.session.commit()

    def count(self):
        return self.session.query(func.count(FingerPrint.id)).scalar()

    def clean(self):
        self.session.close()
