#!/usr/bin/env python
#coding=utf-8
import sys
sys.path.append('..')
from model.model import *
from flask import Flask, request, render_template,redirect,make_response,flash,session,g,url_for
import os
from flask.ext.sqlalchemy import SQLAlchemy
from os import urandom
import requests
import json
from time import *
import hashlib

UPLOAD_FLODER = 'static/img'

def hashpw(a):
	ha=hashlib.md5()
	ha.update(a)
	return str(ha.hexdigest())

@app.route('/found/login',methods=['GET','POST'])
def login():
	if request.method=='POST':
		form=request.form
		p=db.session.query(User).filter(User.EMail==form['EMail'])[0]
		if p.PassWord==hashpw(form['PassWord']):
			session['userid']=p.UserId
			return redirect('/found')
		else:
			return redirect('/found/login')
	return render_template('login_web.html')

@app.route('/found/register',methods=['GET','POST'])
def register():
	if request.method=='POST':
		form = request.form
		t=localtime()
		g.userdata=User()
		g.userdata.TrueName=form['TrueName']
		g.userdata.EMail=form['EMail']
		g.userdata.PassWord=hashpw(form['PassWord'])
		g.userdata.StuNumber=form['StuNumber']
		g.userdata.RegTime=str(t[0])+'.'+str(t[1])+'.'+str(t[2])
		userid=''
		for i in range(6):
			userid=userid+str(t[i])
		g.userdata.UserId=userid
		print g.userdata
		db.session.add(g.userdata)
		db.session.commit()
		db.session.close()
		return redirect('/found/login')

	return render_template('register_web.html')

@app.route('/found/form', methods=['GET', 'POST'])
def form():
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
		g.userdata.Reward=int(form["Reward"])
		g.userdata.LostStatus=True
		g.userdata.SubTime=str(t[0])+'.'+str(t[1])+'.'+str(t[2])
		g.userdata.ImgPath=things[int(form['ThingsType'])]
		print g.userdata.ImgPath
		db.session.add(g.userdata)
		db.session.commit()
		db.session.close()
		return redirect('/found/')
	#return render_template('form00_web.html',form =form)
	return render_template('form_web.html',title='发布启事')


@app.route('/found/',methods=['GET'])
@app.route('/found/<int:page>',methods=['GET'])
def index(page = 1):
	if 'ver'in request.query_string:
		paginate = UserData.query.filter(UserData.Verify==True,UserData.LostStatus==True).order_by(UserData.Id.desc()).paginate(page, 5, False)
		return render_template('index.html',users=paginate,page=page)
	if 'verify_request' in request.query_string:
		x=request.query_string.split('&')
		x=x[0].split('=')
		info=decrypt(x[1])
		session['userid']=info['visit_user']['userid']
		session['time']=info['visit_time']
		return redirect('/found')
	else:
			paginate = UserData.query.filter(UserData.Verify==True,UserData.LostStatus==True).order_by(UserData.Id.desc()).paginate(page, 5, False)
			# for i in paginate.items:
			# 	print i.Header
			return render_template('index_web.html',users=paginate,page=page)



@app.route('/found/usercenter',methods=['GET','POST'])
def usercenter():
	return render_template('usercenter_web.html')


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
		return render_template('verified_web.html',users=admins,page=int(x['page']))
	else:
		admins=UserData.query.filter(UserData.Verify==True).order_by(UserData.Id.desc()).paginate(page,8,False) #test
		return render_template('verified_web.html',users=admins,page=page)


@app.route('/found/manage',methods=['GET','POST'])
@app.route('/found/manage/<int:page>',methods=['GET','POST'])
def manage(page=1):
	if request.query_string:
		x=request.args
		if x['type']=='0':
			db.session.query(UserData).filter_by(Id=x['id']).delete()
		elif x['type']=='1':
			db.session.query(UserData).filter_by(Id=x['id']).update({'LostStatus':False})
		db.session.commit()
		db.session.close()
		admins=UserData.query.paginate(int(x['page']),5,False)
		return render_template('manage_web.html',users=admins,page=int(x['page']))
	else:
		admins=UserData.query.paginate(page,5,False)
		return render_template('manage_web.html',users=admins,page=page)


@app.route("/found/admin/login", methods=["GET", "POST"])
def adminLogin():
	if request.method == 'POST':
		UserId = request.form.get("UserId", None)
		PassWord = request.form.get("PassWord", None)
		user = db.session.query(User).filter(User.UserId==UserId)[0]
		if user.PassWord == hashpw(PassWord):
			session['adminid'] = user.UserId
			return redirect("/found/admin")
		else:
			return redirect("/found/admin/login")
	return render_template("admin_login.html")


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
		return render_template('admin_web.html',users=admins,page=int(x['page']))
	else:
		admins=UserData.query.filter(UserData.Verify==False).order_by(UserData.Id.desc()).paginate(page,8,False) #test
		return render_template('admin_web.html',users=admins,page=page)

@app.route('/found/logout',methods=['GET'])
def logout():
	session['userid']=''



if __name__=='__main__':
	app.run(host='0.0.0.0',port=8011,debug=True)
