#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-


from flask import Flask, render_template, request, redirect
from database.database import Database
from lib.cel import port_scan, domain_scan

app = Flask(__name__)

max_domain = Database().count('subdomain')
max_port = Database().count('port')
max_sendir = Database().count('sendir')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/domain')
@app.route('/domain/<int:page>')
def subdomain(page=1):
    domains = Database().select_subdomain(page)
    return render_template('domain.html', page=page, max_page=max_domain//15+1, domains=domains)


@app.route('/port')
@app.route('/port/<int:page>')
def port(page=1):
    ports = Database().select_ports(page)
    return render_template('port.html', page=page, max_page=max_port//15+1, ports=ports)


@app.route('/sendir')
@app.route('/sendir/<int:page>')
def sendir(page=1):
    ports = Database().select_sendir(page)
    return render_template('port.html', page=page, max_page=max_sendir//15+1, ports=ports)


@app.route('/del/<int:_id>/<string:mode>')
def delete():
    Database().delete(_id, mode)


@app.route('/add', methods=['POST'])
def add_task():
    if request.method == 'POST':
        if request.form['port']:
            port_scan.delay(request.form['port'])
            return redirect('/port/1')
        if request.form['domain']:
            domain_scan.delay(request.form['domain'])
            return redirect('/domain/1')


if __name__ == '__main__':
    try:
        app.run()
    except KeyboardInterrupt:
        sys.exit()
