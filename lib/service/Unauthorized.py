#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import redis
import pymongo
import kazoo.client
import memcache


def redis_unauthorized(ip):
    try:
        conn = redis.Redis(host=ip, port=6379, decode_responses=True)
        conn.set('test', 'test', ex=3, nx=True)
        if conn['test'] == 'test':
            return True
    except Exception as e:
        print(e)
        return False


def mongodb_unauthorized(ip):
    try:
        conn = pymongo.MongoClient(ip, 27017)
        dbname = conn.database_names()
        return True
    except Exception as e:
        print(e)
        return False


def zookeeper_unauthorized(ip):
    try:
        conn = kazoo.client.KazooClient(hosts=str(ip)+':2181')
        conn.start()
        conn.stop()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def elastic_search_unauthorized(ip):
    try:
        resp = requests.get('http://'+str(ip)+':9200')
        if 'You Know, for Search' in resp.text:
            return True
        return False
    except Exception as e:
        print(e)
        return False


def memcached_unauthorized(ip):
    try:
        conn = memcache.Client([str(ip)+':11211'])
        return True
    except Exception as e:
        print(e)
        return False


def hadoop_unauthorized(ip):
    try:
        resp = requests.get('http://'+str(ip)+':50070')
        if 'hadoop' in resp.text.lower():
            return True
        return False
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    # redis_unauthorized('192.155.86.88')
    # mongodb_unauthorized('218.95.177.150')
    # zookeeper_unauthorized('207.244.79.99')
    # elastic_search_unauthorized('101.132.42.189')
    # print(memcached_unauthorized('45.32.116.229'))
    print(hadoop_unauthorized('185.93.31.44'))
