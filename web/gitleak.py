#!/usr/bin/python
# __author__ = 'JasonSheh'
# __email__ = 'qq3039344@gmail.com'
# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, request, redirect
from database.gitLeak import GitLeak
from setting import item_size

gitleak = Blueprint('gitleak', __name__)

g = GitLeak()


@gitleak.route('/gitleak')
@gitleak.route('/gitleak/<int:page>')
def gitleak_index(page=1):
    leaks = g.select_leak(page=page)
    max_leaks = g.count("leak", not_type="0")
    return render_template('gitleak/gitleak.html', leaks=leaks, mode='gitleak', page=page,
                           max_page=max_leaks // item_size + 1)


@gitleak.route('/gitleak/rules')
@gitleak.route('/gitleak/rules/<int:page>')
def gitleak_rules(page=1):
    rules = g.select_rules(page=page)
    max_leaks = g.count("rule")
    return render_template('gitleak/gitrules.html', rules=rules, mode='gitleak/rules', page=page,
                           max_page=max_leaks // item_size + 1)


@gitleak.route('/gitleak/range')
@gitleak.route('/gitleak/range/<int:page>')
def gitleak_range(page=1):
    ranges = g.select_range(page=page)
    max_ranges = g.count("range")
    return render_template('gitleak/gitrange.html', ranges=ranges, mode='gitleak/range',
                           page=page, max_page=max_ranges // item_size + 1)


@gitleak.route('/gitleak/<string:mode>/<int:leak_id>')
def gitleak_mode(mode, leak_id):
    if mode == "ignore":
        g.update_type(leak_id, 0)
        return redirect(request.referrer)
    if mode == "confirm":
        g.update_type(leak_id, 1)
        return redirect(request.referrer)
    if mode == "irrelevant":
        g.update_type(leak_id, 2)
        return redirect(request.referrer)


@gitleak.route('/gitleak/del/<string:mode>/<int:id>')
def gitleak_delete(mode, id):
    """
    删除github 监控范围或搜索规则
    :param mode: range or rule
    :param id: id
    :return:
    """
    g.delete(mode, id)
    return redirect(request.referrer)


@gitleak.route('/gitleak/update/<string:mode>', methods=['POST'])
def gitleak_update(mode):
    if mode == "range":
        if request.form.get('id') and request.form.get('domain'):
            g.update_range(request.form['id'], request.form['domain'])
            return redirect(request.referrer)
    if mode == "rule":
        if request.form.get('id') and request.form.get('keyword') and request.form.get('pattern'):
            g.update_rule(request.form['id'], request.form['keyword'], request.form['pattern'])
            return redirect(request.referrer)
    return redirect('/gitleak')


@gitleak.route('/gitleak/add/<string:mode>', methods=['POST'])
def gitleak_add(mode):
    if mode == "range":
        if request.form.get('domain'):
            g.insert_range(request.form['id'], request.form['domain'])
            return redirect('/gitleak/range')
    if mode == "rule":
        if request.form.get('keyword') and request.form.get('pattern'):
            g.insert_rule(request.form['keyword'], request.form['pattern'])
            return redirect('/gitleak/rules')
    return redirect('/gitleak')
