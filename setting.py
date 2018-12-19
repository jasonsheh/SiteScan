#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

# 安装设置
user_path = 'C:/Code/SiteScan'

# 常用变量设置

# 页面显示条目数
item_size: int = 15

# 每日子域名获取数量
sudomain_scan_size: int = 2

# vps 1c1m 50线程数 用时 4min完成 cpu 40% 带宽 40%
# 根据服务器配置自行调整
subdomain_thread_num: int = 150
sendir_thread_num: int = 50
siteinfo_thread_num: int = 20

user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"

vt_api_key = ""

github_api_key = ""

qq_email_username = ""
qq_email_password = ""
