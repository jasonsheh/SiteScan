#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-


from flask import Flask, render_template, request, redirect
from database.database import Database
from database.rules import Rules
from database.srcList import SrcList
from setting import item_size

from web.gitleak import gitleak

app = Flask(__name__)
app.register_blueprint(gitleak)

max_domain = Database().count('subdomain')
max_port = Database().count('port')
max_sendir = Database().count('sendir')
max_fingerprint = Rules().count('fingerprint')
max_vul = Database().count('vul')
max_src = SrcList().count()


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    src_list = SrcList().select_recent_src_list(page)
    return render_template('index.html', mode="index", page=page, max_page=max_src // item_size + 1, src_list=src_list,
                           max_domain=max_domain, max_port=max_port,
                           max_sendir=max_sendir, max_fingerprint=max_fingerprint,
                           max_vul=max_vul)


@app.route('/setting')
@app.route('/setting/<int:page>')
def setting(page=1):
    src_list = SrcList().select_src_list(page)
    return render_template('setting.html', mode="setting", page=page, src_list=src_list,
                           max_page=max_src // item_size + 1)


@app.route('/fingerscan')
def finger_scan():
    return render_template('fingerscan.html', total_number=max_fingerprint)

# @app.route('/fingerscan/post', methods=['POST'])
# def add_task():
#     if request.method == 'POST':
#         if request.form.get('domain').find('.') != -1:
#             result = FingerPrint(request.form.get('finger'), request.form.get('protocol')).run()
#             flash(result.split(' ')[:-1])
#         return redirect('/index')


@app.route('/detail/<int:domain_id>')
def detail(domain_id):
    # 域名ID
    src_name = SrcList().select_src_by_id(domain_id)
    domain_number = Database().count_detail('subdomain', domain_id)
    port_number = Database().count_detail('port', domain_id)
    sendir_number = Database().count_detail('sendir', domain_id)
    vul_number = Database().count_detail('vul', domain_id)
    return render_template('detail.html', domain_id=domain_id, src_name=src_name[2:], domain_number=domain_number,
                           port_number=port_number, sendir_number=sendir_number, vul_number=vul_number)


@app.route('/detail/<string:mode>/<int:id>')
@app.route('/detail/<string:mode>/<int:id>/<int:page>')
def detail_domain(mode, id, page=1):
    if mode == 'domain':
        domain_number = Database().count_detail('subdomain', id)
        domains = Database().select_subdomain_by_domain_id(id, page)
        return render_template('detail.html', id=id, _mode=mode, mode="detail/{}/{}".format(mode, id), page=page,
                               max_page=domain_number // item_size + 1, domains=domains)
    if mode == 'port':
        port_number = Database().count_detail('port', id)
        ports = Database().select_port_by_page(page, id)
        return render_template('detail.html', id=id, _mode=mode, mode="detail/{}/{}".format(mode, id), page=page,
                               max_page=port_number // item_size + 1, ports=ports)
    if mode == 'sendir':
        sendir_number = Database().count_detail('sendir', id)
        sendir = Database().select_sendir_by_page(page, id)
        return render_template('detail.html', id=id, _mode=mode, mode="detail/{}/{}".format(mode, id), page=page,
                               max_page=sendir_number // item_size + 1, sendirs=sendir)
    if mode == 'vul':
        vul_number = Database().count_detail('vul', id)
        vuls = Database().select_vul_by_page(page, id)
        return render_template('detail.html', id=id, _mode=mode, mode="detail/{}/{}".format(mode, id), page=page,
                               max_page=vul_number // item_size + 1, sendirs=vuls)


@app.route('/domain')
@app.route('/domain/<int:page>')
def subdomain(page=1):
    domains = Database().select_subdomain(page)
    return render_template('domain.html', mode="domain", page=page, max_page=max_domain // item_size + 1,
                           domains=domains)


@app.route('/domain/detail/<int:domain_id>')
def subdomain_detail(domain_id):
    domain = Database().select_subdomain_detail(domain_id)[0]
    # TODO 完善子域名详细信息功能
    return render_template('domain_detail.html', domain=domain)


@app.route('/port')
@app.route('/port/<int:page>')
def port(page=1):
    ports = Database().select_port(page)
    return render_template('port.html', mode="port", page=page, max_page=max_port // item_size + 1, ports=ports)


@app.route('/sendir')
@app.route('/sendir/<int:page>')
def sendir(page=1):
    sendir = Database().select_sendir(page)
    return render_template('sendir.html', mode="sendir", page=page, max_page=max_sendir // item_size + 1,
                           sendirs=sendir)


@app.route('/vul')
@app.route('/vul/<int:page>')
def vul(page=1):
    vuls = Database().select_vul(page)
    return render_template('vul.html', mode="vul", page=page, max_page=max_vul // item_size + 1, sendirs=vuls)


@app.route('/fingerprint')
@app.route('/fingerprint/<int:page>')
def fingerprint(page=1):
    finger_print = Rules().select_fingerprint(page)
    return render_template('fingerprint.html', mode="fingerprint", page=page, max_page=max_fingerprint // item_size + 1,
                           fingerprints=finger_print)


@app.route('/add_rule', methods=['POST'])
def add_rule():
    if request.method == 'POST':
        if request.form.get('name') and request.form.get('rule'):
            Rules().insert_fingerprint(request.form['name'], request.form['rule'])
            return redirect('/fingerprint/1')


@app.route('/update/<string:mode>', methods=['POST'])
def update(mode):
    if request.method == 'POST':
        if mode == "fingerprint":
            if request.form.get('name') and request.form.get('rule'):
                Rules().update_fingerprint(request.form['name'], request.form['rule'])
                return redirect(request.referrer)


@app.route('/del/<string:mode>/<int:id>')
def delete(id, mode):
    if mode == 'src':
        SrcList().delete(id)
    if mode == 'fingerprint':
        Rules().delete(id)
    else:
        Database().delete(id, mode)
    return redirect(request.referrer)
