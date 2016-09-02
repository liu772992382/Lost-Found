#!/usr/bin/env python
#coding=utf-8
import sys
sys.path.append('..')
from model import *
from flask import Flask, request, render_template,redirect,make_response,flash,session,g,url_for,jsonify
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from werkzeug.utils import secure_filename
from flask.ext.sqlalchemy import SQLAlchemy
import requests
import json
from time import localtime
import hashlib
from M2Crypto import util
from Crypto.Cipher import AES
from PIL import Image

IMG_FLODER = 'static/img/'
admin_list=['201632220424','5297459','20164994118']

Users = db.session.query(User).all()

username_table = {u.EMail:u for u in Users}
userid_table = {u.id:u for u in Users}
print username_table
print userid_table


def decrypt(data):
	iv = '9b738aa2ee18145a' # app id
	KEY = '298fe57f669647ffe92ee1deba8b944e' # app secret
	mode = AES.MODE_CBC
	data = util.h2b(data)
	decryptor = AES.new(KEY, mode, IV=iv)
	plain = decryptor.decrypt(data)
	plain = "".join([ plain.strip().rsplit("}" , 1)[0] ,  "}"] )
	oauth_state = json.loads(plain)
	return oauth_state


def hashpw(a):
	ha=hashlib.md5()
	ha.update(a)
	print str(ha.hexdigest()),a
	return str(ha.hexdigest())


def IsMobile(a):
	a=a.lower()
	MobileAgent=["iphone", "ipod", "ipad", "android", "mobile", "blackberry", "webos", "incognito", "webmate", "bada", "nokia", "lg", "ucweb", "skyfire"]
	for i in MobileAgent:
		if i in a:
			return True
	else:
		return False


def Thumbnail(fname):
	size=160,160
	im=Image.open(IMG_FLODER+fname)
	im.thumbnail(size,Image.ANTIALIAS)
	im.save(IMG_FLODER+fname+'.thumbnail','png')


def authenticate(username, password):
    user = username_table.get(username,None)
    if user and safe_str_cmp(user.PassWord, hashpw(password)):
        return user

def identity(payload):
	user_id = payload['identity']
	return userid_table.get(user_id,None)

jwt = JWT(app,authenticate,identity)


@app.route('/protected')
@jwt_required()
def protected():
	return '%s' %current_identity


class Index():
	def get(self):
		paginate = UserData.query.filter(UserData.Verify==True).order_by(UserData.Id.desc()).paginate(page, 5, False)
		infoes = []
		for i  in paginate.items:
			infoes.append(i.dict())
		return jsonify({'users':infoes,'page':page,'title':u'寻物招领'})


@app.route('/found',methods=['GET','POST'])

def get(self):
	if 'userid' in session and session['userid']!='':
		LoginVer = False
	else:
		LoginVer = True
	return {'LoginVer':LoginVer,'IsMobile':IsMobile(request.headers.get('User-Agent'))}

def post(self):
		if 'userid' in session and session['userid']!='':
			LoginVer = False
		else:
			LoginVer = True
		form=request.form
		p=db.session.query(User).filter(User.EMail==form['EMail']).first()
		LoginStatus = False
		if  p!=None and p.PassWord==hashpw(form['PassWord']):
			session['userid'] = p.UserId
			LoginStatus = True
		return jsonify({'status':LoginStatus,'LoginVer':LoginVer,'IsMobile':IsMobile(request.headers.get('User-Agent'))})



if __name__=='__main__':
	app.run(host='0.0.0.0',port=8888, debug=True)
