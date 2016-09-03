#!/usr/bin/env python
#coding=utf8

import flask_whooshalchemy as whooshalchemy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask
from config import Config
import sys, os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# class User(db.Model):
#     __tablename__ = 'Users'
#     uid = db.Column(db.Integer, primary_key=True)
#     UserId = db.Column(db.String(50))
#     UserNick = db.Column(db.String(50))
#     UserImg = db.Column(db.String(200))
#     UserSex = db.Column(db.Boolean)
#
#     def __str__ (self):
#         return "User(Id='%s')" % self.id
#
#     def dict(self):
#         return {'Id':self.uid,
#                 'UserId':self.UserId,
#                 'TrueName':self.TrueName,
#                 'StuNumber':self.StuNumber,
#                 'RegTime':self.RegTime}

class UserData(db.Model):
    __tablename__ = 'NoticeData'

    did = db.Column(db.Integer, primary_key=True)
    Time = db.Column(db.String(50))
    # Header = db.Column(db.String(50))
    UserId = db.Column(db.String(20))
    UserNick = db.Column(db.String(50))
    UserImg = db.Column(db.String(200))
    Place = db.Column(db.String(100))
    # ThingsType = db.Column(db.String(20))
    Type = db.Column(db.Integer,default = 0)
    Content = db.Column(db.String(400))
    ImgPath = db.Column(db.String(150))
    Report = db.Column(db.Integer, default = 0)
    ReportUsers = db.Column(db.String(500), default = '')
    # Reward = db.Column(db.Integer)
    #ThumbnailPath = db.Column(db.String(150))
    LostStatus = db.Column(db.Boolean, default = True)
    ContactWay = db.Column(db.String(100))
    # Verify = db.Column(db.Boolean,default=False)
    SubTime=db.Column(db.String(30))


class Star(db.Model):
    __tablename__ = 'Star'

    sid = db.Column(db.Integer, primary_key = True)
    UserId = db.Column(db.String(20))
    did = db.Column(db.Integer,db.ForeignKey('NoticeData.did',ondelete='CASCADE', onupdate='CASCADE'))
    StarTime = db.Column(db.String(30))

#
# class ThirdLoginUser(db.Model):
#     __tablename__ = 'ThirdLoginUser'
#
#     Id = db.Column(db.Integer,primary_key=True)
#     Type = db.Column(db.String(20))   # 第三方登录类型
#     UserId = db.Column(db.String(20)) # 第三方登录唯一ID
#     UserName = db.Column(db.String(20)) # 第三方登录用户名
#     AccessToken = db.Column(db.String(80))  # 第三方登录唯一凭证
#     TokenExpires = db.Column(db.String(40))  # 凭证过期时间

#
# class AdminUser(db.Model):
#     __tablename__ = "AdminUsers"
#     Id = db.Column(db.Integer, primary_key=True)
#     UserId = db.Column(db.String(50))
#     PassWord = db.Column(db.String(50))
#     RegTime = db.Column(db.String(50))
#
# whooshalchemy.whoosh_index(app, UserData)

# if __name__ == '__main__':
#     db.create_all()
#
#     admin = AdminUser()
#     admin.UserId = "20144483"
#     admin.PassWord = "7ff5ae861e302ac269518883ce0a2dea"
#     db.session.add(admin)
#     db.session.commit()
#     db.session.close()
