#!/usr/bin/env python
#coding=utf-8
from os import urandom
class Config(object):
	SQLALCHEMY_DATABASE_URI='mysql://root:g@localhost:3306/findthing?charset=utf8'
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	SQLALCHEMY_TRACK_MODIFICATIONS=True
	SECRET_KEY = "hard to guess"
	UPLOAD_FLODER = 'static/img/'
	WHOOSH_BASE = 'mysql://root:g@localhost:3306/findthing?charset=utf8'
	IMG_FLODER = 'static/img/'
	# email
	MAIL_HOST = "smtp.163.com"
	MAIL_SENDER = "gjw870402916@163.com"
	MAIL_PASSWORD = "08151997bc"
	MAIL_RECEIVER_LIST = ["870402916@qq.com",]
