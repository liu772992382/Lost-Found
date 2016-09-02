#!/usr/bin/env python
#coding=utf-8
from flask import Flask, request, render_template,redirect,make_response,flash,session,g,url_for
import os
from werkzeug.utils import secure_filename
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField,SelectField
from wtforms.validators import Required,Length
from os import urandom
from model import *
import requests
import json
from M2Crypto import util 
from Crypto.Cipher import AES
from time import *

app = Flask(__name__)

def decrypt(data):
	iv = '433acf3969f659d1' # app id
	KEY = '038fa8231348f42966b95ee52f56fbf7' # app secret
	mode = AES.MODE_CBC
	data = util.h2b(data)
	decryptor = AES.new(KEY, mode, IV=iv)
	plain = decryptor.decrypt(data)
	plain = "".join([ plain.strip().rsplit("}" , 1)[0] ,  "}"] )
	oauth_state = json.loads(plain)
	return oauth_state


@app.route('/found/form', methods=['GET', 'POST'])
def form():
	if 'userid' not in session:
		return redirect('/found')
	if request.method=='POST':
		form = request.form
		t=localtime()
		things=['card.png','wallet.jpg','keys.png','phone.png','others.png']
		g.userdata=UserData()
		g.userdata.Time=form['Time']
		g.userdata.Place=form['Place']
		g.userdata.Header=form['Header']
		g.userdata.ThingsType=form['ThingsType']
		g.userdata.Type=form['Type']
		g.userdata.Content=form['Content']
		g.userdata.ContactWay=form['ContactWay']
		#g.userdata.Stunum=session['userid']
		g.userdata.LostStatus=True
		g.userdata.SubTime=str(t[0])+'.'+str(t[1])+'.'+str(t[2])
		g.userdata.ImgPath=things[int(form['ThingsType'])]

		db.session.add(g.userdata)
		db.session.commit()
		db.session.close()
		return redirect('/found/manage')
	#return render_template('form00.html',form =form)
	return render_template('test_form.html',title='发布启事')


@app.route('/found/',methods=['GET'])
@app.route('/found/<int:page>',methods=['GET'])
@app.errorhandler(500)
def index(page = 1):
	#if 'verify_request' in request.query_string:
		x=request.query_string.split('&')
		x=x[0].split('=')
		info=decrypt(x[1])
		session['userid']=info['visit_user']['userid']
		session['time']=info['visit_time']
		return redirect('/found')
	#else:
		if 'userid' not in session:
			#r1=requests.get('https://openapi.yiban.cn/oauth/authorize?client_id=56ce8404ea66f546&redirect_uri=http://113.251.245.100&display=html')
			return '请登录易班客户端使用!'
		elif 'userid'  in session:
			paginate = UserData.query.filter(UserData.Verify==True,UserData.LostStatus==True).order_by(UserData.Id.desc()).paginate(page, 5, False)
			# for i in paginate.items:
			# 	print i.Header
			return render_template('test_index.html',users=paginate,page=page)
		else:
			return '请登录易班客户端使用!' 

@app.route('/found/finished',methods=['GET'])
@app.route('/found/finished/<int:page>',methods=['GET'])
def finished(page=1):
	if 'userid' not in session:
		return redirect('/found')
	paginate = UserData.query.filter(UserData.Verify==True,UserData.LostStatus==False).order_by(UserData.Id.desc()).paginate(page, 5, False)
	return render_template('finished.html',users=paginate,page=page)


@app.route('/found/verified',methods=['GET'])
@app.route('/found/verified/<int:page>',methods=['GET'])
def verified(page=1):
	if request.query_string:
		x=request.args
		if x['type']=='0':
			db.session.query(UserData).filter_by(Id=x['id']).delete()
		elif x['type']=='1':
			db.session.query(UserData).filter_by(Id=x['id']).update({'LostStatus':False})
		elif x['type']=='2':
			db.session.query(UserData).filter_by(Id=x['id']).update({'Verify':True})
		db.session.commit()
		db.session.close()
		admins=UserData.query.filter(UserData.Verify==True).order_by(UserData.Id.desc()).paginate(int(x['page']),8,False)
		return render_template('verified.html',users=admins,page=int(x['page']))
	else:
		#admins=admin.query.filter_by()
		admins=UserData.query.filter(UserData.Verify==True).order_by(UserData.Id.desc()).paginate(page,8,False) #test
		return render_template('verified.html',users=admins,page=page)


@app.route('/found/manage',methods=['GET','POST'])
@app.route('/found/manage/<int:page>',methods=['GET','POST'])
def manage(page=1):
	if 'userid' not in session:
		return redirect('/found')
	if request.query_string:
		x=request.args
		if x['type']=='0':
			db.session.query(UserData).filter_by(Id=x['id']).delete()
		elif x['type']=='1':
			db.session.query(UserData).filter_by(Id=x['id']).update({'LostStatus':False})
		db.session.commit()
		db.session.close()
		admins=UserData.query.filter_by(Stunum=session['userid']).order_by(UserData.Id.desc()).paginate(int(x['page']),5,False)
		return render_template('manage.html',users=admins,page=int(x['page']))
	else:
		admins=UserData.query.order_by(UserData.Id.desc()).paginate(page,5,False)
		return render_template('manage.html',users=admins,page=page)


@app.route('/found/admin',methods=['GET','POST'])
@app.route('/found/admin/<int:page>',methods=['GET','POST'])
def admin(page=1):
	admin=UserData()
	if request.query_string:
		x=request.args
		if x['type']=='0':
			db.session.query(UserData).filter_by(Id=x['id']).delete()
		elif x['type']=='1':
			db.session.query(UserData).filter_by(Id=x['id']).update({'LostStatus':False})
		elif x['type']=='2':
			db.session.query(UserData).filter_by(Id=x['id']).update({'Verify':True})
		db.session.commit()
		db.session.close()
		admins=UserData.query.filter(UserData.Verify==False).order_by(UserData.Id.desc()).paginate(int(x['page']),8,False)
		return render_template('admin.html',users=admins,page=int(x['page']))
	else:
		admins=UserData.query.filter(UserData.Verify==False).order_by(UserData.Id.desc()).paginate(page,8,False) #test
		return render_template('admin.html',users=admins,page=page)


if __name__=='__main__':
	app.run(host="0.0.0.0",port=8082,debug=True)
