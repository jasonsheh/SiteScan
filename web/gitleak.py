#!/usr/bin/python
# __author__ = 'JasonSheh'
# __email__ = 'qq3039344@gmail.com'
# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, request, redirect
from database.gitLeak import GitLeak

gitleak = Blueprint('gitleak', __name__)


@gitleak.route('/gitleak')
def gitleak_index():
    return render_template('gitleak/gitleak.html')


@gitleak.route('/gitleak/rules')
@gitleak.route('/gitleak/rules/<int:page>')
def gitleak_rules(page=1):
    rules = GitLeak().select_rules_by_page(page=page)
    return render_template('gitleak/gitrules.html', rules=rules, mode='/gitleak/rules', page=page)
