#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-


from flask import Flask, render_template, request, redirect
from database.database import Database
from database.rules import Rules
from lib.cel import port_scan, domain_scan, sendir_scan, site_scan

app = Flask(__name__)

max_domain = Database().count('subdomain')
max_port = Database().count('port')
max_sendir = Database().count('sendir')
max_fingerprint = Rules().count('application')
max_task = Database().count('task')
max_vul = Database().count('vul')


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    tasks = Database().select_task(page)
    return render_template('index.html', page=page, max_page=max_task, tasks=tasks,
                           max_domain=max_domain, max_port=max_port,
                           max_sendir=max_sendir, max_fingerprint=max_fingerprint,
                           max_vul=max_vul)


@app.route('/detail')
@app.route('/detail/<int:id>')
def detail(id=1):
    task_name = Database().select_task_name(id)
    domain_number = Database().count_task('subdomain', id)
    port_number = Database().count_task('port', id)
    sendir_number = Database().count_task('sendir', id)
    vul_number = Database().count_task('vul', id)
    return render_template('detail.html', id=id, task_name=task_name, domain_number=domain_number,
                           port_number=port_number, sendir_number=sendir_number, vul_number=vul_number)


@app.route('/detail/<string:mode>/<int:id>')
@app.route('/detail/<string:mode>/<int:id>/<int:page>')
def detail_domain(mode, id, page=1):
    if mode == 'domain':
        domain_number = Database().count_task('subdomain', id)
        domains = Database().select_task_subdomain(page, id)
        return render_template('detail.html', id=id, mode=mode, page=page, max_page=domain_number//15+1, domains=domains)
    if mode == 'port':
        port_number = Database().count_task('port', id)
        ports = Database().select_task_port(page, id)
        return render_template('detail.html', id=id, mode=mode, page=page, max_page=port_number//15+1, ports=ports)
    if mode == 'sendir':
        sendir_number = Database().count_task('sendir', id)
        sendir = Database().select_task_sendir(page, id)
        return render_template('detail.html', id=id, mode=mode, page=page, max_page=sendir_number//15+1, sendirs=sendir)
    if mode == 'vul':
        vul_number = Database().count_task('vul', id)
        vuls = Database().select_task_vul(page, id)
        return render_template('detail.html', id=id, mode=mode, page=page, max_page=vul_number//15+1, sendirs=vuls)



@app.route('/domain')
@app.route('/domain/<int:page>')
def subdomain(page=1):
    domains = Database().select_subdomain(page)
    return render_template('domain.html', page=page, max_page=max_domain//15+1, domains=domains)


@app.route('/port')
@app.route('/port/<int:page>')
def port(page=1):
    ports = Database().select_port(page)
    return render_template('port.html', page=page, max_page=max_port//15+1, ports=ports)


@app.route('/sendir')
@app.route('/sendir/<int:page>')
def sendir(page=1):
    sendir = Database().select_sendir(page)
    return render_template('sendir.html', page=page, max_page=max_sendir//15+1, sendirs=sendir)


@app.route('/vul')
@app.route('/vul/<int:page>')
def vul(page=1):
    vuls = Database().select_vul(page)
    return render_template('vul.html', page=page, max_page=max_vul//15+1, sendirs=vuls)


@app.route('/fingerprint')
@app.route('/fingerprint/<int:page>')
def fingerprint(page=1):
    finger_print = Rules().select_application(page)
    return render_template('fingerprint.html', page=page, max_page=max_fingerprint//15+1, fingerprints=finger_print)


@app.route('/add_rule', methods=['POST'])
def add_rule():
    if request.method == 'POST':
        if request.form.get('name') and request.form.get('rule'):
            # print(request.form['name'], request.form['rule'])
            Rules().insert_application(request.form['name'], request.form['rule'])
            return redirect('/fingerprint/1')


@app.route('/del/<int:id>/<string:mode>')
def delete(id, mode):
    Database().delete(id, mode)


@app.route('/add', methods=['POST'])
def add_task():
    if request.method == 'POST':
        if request.form.get('port'):
            port_scan.delay(request.form['port'])
            return redirect('/port/1')
        elif request.form.get('domain'):
            domain_scan.delay(request.form['domain'])
            return redirect('/domain/1')
        elif request.form.get('sendir'):
            sendir_scan.delay(request.form['sendir'])
            return redirect('/sendir/1')
        elif request.form.get('vul'):
            sendir_scan.delay(request.form['vul'])
            return redirect('/vul/1')
        elif request.form.get('sitescan'):
            site_scan.delay(request.form['sendir'])
            return redirect('/index')


if __name__ == '__main__':
    try:
        app.run()
    except KeyboardInterrupt:
        sys.exit()
