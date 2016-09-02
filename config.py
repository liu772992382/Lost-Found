#!/usr/bin/env python
#coding=utf-8
from os import urandom
class Config(object):
	SQLALCHEMY_DATABASE_URI='mysql://root:<password>@localhost:3306/findthing?charset=utf8'
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	SQLALCHEMY_TRACK_MODIFICATIONS=True
	SECRET_KEY = "hard to guess"
	UPLOAD_FLODER = 'static/img'
	WHOOSH_BASE = 'mysql://root:g@localhost:3306/findthing?charset=utf8'
