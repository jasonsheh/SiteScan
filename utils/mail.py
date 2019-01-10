#!/usr/bin/python
# __author__ = 'JasonSheh'
# __email__ = 'qq3039344@gmail.com'
# -*- coding:utf-8 -*-

import traceback
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from setting import qq_email_username, qq_email_password


class MyMail:
    def __init__(self):
        self.smtp_server = 'smtp.qq.com'
        self.smtp_port = 587

    def send_mail(self, subject, title, sender="SiteScan Email Module"):
        receivers = ['3039344@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

        message = MIMEText(subject, 'plain', 'utf-8')
        message['From'] = Header(sender, 'utf-8')
        message['To'] = Header("you", 'utf-8')

        message['Subject'] = Header(title, 'utf-8')

        try:
            smtpObj = smtplib.SMTP(self.smtp_server, self.smtp_port)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(qq_email_username, qq_email_password)
            smtpObj.sendmail(qq_email_username, receivers, message.as_string())
            print("邮件发送成功")
            smtpObj.quit()
        except Exception as e:
            print("Error: ", e)

    @staticmethod
    def mail_test(username: str, password: str, server: str, port: int) -> bool:
        try:
            smtpObj = smtplib.SMTP(server, port)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(username, password)
            smtpObj.quit()
            return True
        except Exception as e:
            return False


def mail_alert(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            MyMail().send_mail(traceback.format_exc(), 'error', "SiteScan Email Module")
    return wrapper


if __name__ == '__main__':
    # MyMail().send_mail('这个是正文\nPython SMTP 邮件测试', "这个是标题", "SiteScan Email Module")
    MyMail.mail_test("15611700291@163.com", "chao5638321", "smtp.163.com", 25)
