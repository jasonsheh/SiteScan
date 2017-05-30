#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys

from flask import Flask, render_template
from database.database import Database
app = Flask(__name__)

max_page = Database().count('subdomain')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/domain/<int:page>')
def SubDomain(page=1):
    domains = Database().select_subdomain(page)
    return render_template('domain.html', page=page, max_page=max_page//15+1, domains=domains)


@app.route('/del/<int:_id>/<string:mode>')
def delete():
    Database().delete(_id, mode)


if __name__ == '__main__':
    try:
        app.run()
    except KeyboardInterrupt:
        sys.exit()
