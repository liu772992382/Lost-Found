# -*-coding:utf8 -*-

import smtplib
from flask import current_app
from email.mime.text import MIMEText


def send_email(username, content):
    msg = MIMEText(content,_subtype="html",_charset="utf-8")
    msg["Subject"] = "用户反馈"
    msg["From"] = username + "<" + current_app.config.get('MAIL_SENDER') + ">"
    msg["To"] = ";".join(current_app.config.get('MAIL_RECEIVER_LIST'))

    try:
        server = smtplib.SMTP()
        server.connect(current_app.config.get('MAIL_HOST'))
        server.starttls()
        server.login(current_app.config.get('MAIL_SENDER'), current_app.config.get('MAIL_PASSWORD'))
        server.sendmail(current_app.config.get('MAIL_SENDER'),current_app.config.get('MAIL_RECEIVER_LIST'),msg.as_string())
        server.close()
    except Exception as e:
        return False
    return True
