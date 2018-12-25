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


@gitleak.route('/gitleak/range')
@gitleak.route('/gitleak/range/<int:page>')
def gitleak_range(page=1):
    ranges = g.select_range(page=page)
    max_ranges = g.count("range")
    return render_template('gitleak/gitrange.html', ranges=ranges, mode='gitleak/range',
                           page=max_ranges // item_size + 1)


@gitleak.route('/gitleak/<string:mode>/<int:leak_id>')
def gitleak_mode(mode, leak_id):
    if mode == "ignore":
        GitLeak().update_type(leak_id, 0)
        return redirect(request.referrer)
    if mode == "confirm":
        GitLeak().update_type(leak_id, 1)
        return redirect(request.referrer)
    if mode == "irrelevant":
        GitLeak().update_type(leak_id, 2)
        return redirect(request.referrer)
