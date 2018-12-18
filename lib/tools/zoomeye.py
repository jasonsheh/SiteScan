#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import requests
import os
import json

access_token = ''
ip_list = []


def login():
    username = input('[-] input : username :')
    password = input('[-] input : password :')
    data = {
        'username': username,
        'password': password
    }
    data_encoded = json.dumps(data)
    try:
        r = requests.post(url='https://api.zoomeye.org/user/login', data=data_encoded)
        r_decoded = json.loads(r.text)
        global access_token
        access_token = r_decoded['access_token']
    except Exception as e:
        print('[-] info : username or password is wrong, please try again ')
        print(e)
        exit()


def save_str(file, my_str):
    with open(file, 'w') as output:
        output.write(my_str)


def save_list(file, my_list):
    s = '\n'.join(my_list)
    with open(file, 'w+') as output:
        output.write(s)


def apiTest():
    global access_token
    with open('access_token.txt', 'r') as token:
        access_token = token.read()
    headers = {
        'Authorization': 'JWT ' + access_token,
    }
    page = 1
    # print(headers)
    print('[-] Usage : port: country:')
    key = input('[-] Input : searching content :')
    pages = input('[-] Input : searching pages :')
    while int(pages) >= page:
        try:
            r = requests.get(url='https://api.zoomeye.org/host/search?query='+str(key) +
                                 '&facet=app,os&page='+str(page), headers=headers)
            r_decoded = json.loads(r.text)
            print(r.text)
            # print r_decoded
            # print r_decoded['total']
            for x in r_decoded['matches']:
                ip_list.append(x['ip'] + ':' + str(x['portinfo']['port']))
            print('[-] info : count ' + str(page * 10))
        except Exception as e:
            if e == 'matches':
                print('[-] info : account was break, excceeding the max limitations')
                break
            else:
                print('[-] info : ' + str(e))
        page += 1
    save_list('res_ip.txt', ip_list)


def main():
    if not os.path.isfile('access_token.txt'):
        print('[-] info : access_token file is not exist, please login')
        login()
        save_str('access_token.txt', access_token)

    apiTest()


if __name__ == '__main__':
    main()
