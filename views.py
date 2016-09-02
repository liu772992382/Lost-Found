#!/usr/bin/env python
#coding=utf8
import sys
sys.path.append('..')
from model import *
from flask import Flask, request, render_template,redirect,make_response,flash,session,g,url_for
import os
from PIL import Image
from werkzeug.utils import secure_filename
from flask.ext.sqlalchemy import SQLAlchemy
from os import urandom
import requests
import json
from time import *
import hashlib
from M2Crypto import util
from Crypto.Cipher import AES
from PIL import Image


IMG_FLODER = 'static/img/'

admin_list=['201632220424','5297459','20164994118']

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

@app.route('/found/login',methods=['GET','POST'])
def login(Warnings=''):
	if 'userid' in session and session['userid']!='':
		LoginVer=False
	else:
		LoginVer=True
	if request.method=='POST':
		form=request.form
		p=db.session.query(User).filter(User.EMail==form['EMail']).first()
		if  p!=None and p.PassWord==hashpw(form['PassWord']):
			session['userid']=p.UserId
			return redirect('/found/manage')
		else:
			if not IsMobile(request.headers.get('User-Agent')):
				return render_template('login_web.html',Warnings=u'帐号或密码错误！',Login=LoginVer,title=u'登录')
			else:
				return render_template('login.html',Login=LoginVer,Warnings=u'帐号或密码错误！',title=u'登录')
	else:
		if not IsMobile(request.headers.get('User-Agent')):
			return render_template('login_web.html',Login=LoginVer,title=u'登录')
		else:
			return render_template('login.html',Login=LoginVer,title=u'登录')

@app.route('/found/register',methods=['GET','POST'])
def register():
	if 'userid' in session and session['userid']!='':
		LoginVer=False
	else:
		LoginVer=True
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
		if db.session.query(User).filter(User.EMail==form['EMail']).first()==None:
			g.userdata.UserId=userid
			db.session.add(g.userdata)
			db.session.commit()
			db.session.close()
			return redirect('/found/login')
		else:
			if not IsMobile(request.headers.get('User-Agent')):
				return render_template('register_web.html',title=u'注册',Login=LoginVer,Warnings=u'用户名已存在！')
			else:
				return render_template('register.html',title=u'注册',Login=LoginVer,Warnings=u'用户名已存在！')
	if not IsMobile(request.headers.get('User-Agent')):
		return render_template('register_web.html',title=u'注册',Login=LoginVer)
	else:
		return render_template('register.html',title=u'注册',Login=LoginVer)


@app.route('/found/form', methods=['GET', 'POST'])
def form():

	if 'userid' not in session or session['userid']=='':
		return redirect('/found/login')
	if 'userid' in session and session['userid']!='':
		LoginVer=False
	else:
		LoginVer=True
	if request.method=='POST':
		form = request.form
		t=localtime()
		things=['kapian_icon.png','qianbao_icon.png','yaoshi_icon.png','shouji_icon.png','qita_icon.png']
		f=request.files['form_file']
		if f.filename=='':
			fname=things[int(form['ThingsType'])]
		else:
			fname=secure_filename(f.filename)
			f.save(os.path.join(IMG_FLODER,fname))
			Thumbnail(fname)
		g.userdata=UserData()
		g.userdata.Header = form["Header"]
		g.userdata.Time=form['Time']
		g.userdata.Place=form['Place']
		g.userdata.ThingsType=form['ThingsType']
		g.userdata.Type=form['Type']
		g.userdata.Content=form['Content']
		g.userdata.ContactWay=form['ContactWay']
		g.userdata.Reward=form['Reward']
		g.userdata.LostStatus=True
		g.userdata.SubTime=str(t[0])+'.'+str(t[1])+'.'+str(t[2])
		g.userdata.ImgPath=fname
		g.userdata.UserId=session['userid']
		db.session.add(g.userdata)
		db.session.commit()
		db.session.close()
		return redirect('/found/manage')
	#return render_template('form00.html',form =form)

	if not IsMobile(request.headers.get('User-Agent')):
		return render_template('form_web.html',title=u'发布启事',Login=LoginVer)
	else:
		return render_template('form.html',title=u'发布启事',Login=LoginVer)


@app.route('/found/',methods=['GET'])
@app.route('/found/<int:page>',methods=['GET'])
def index(page = 1):
	if 'userid' in session and session['userid']!='':
		LoginVer=False
	else:
		LoginVer=True
	_type = request.args.get("type", "寻物")
	paginate = UserData.query.filter(UserData.Verify==True, UserData.Type==_type).order_by(UserData.Id.desc()).paginate(page, 8, False)
	# for i in paginate.items:
	if not IsMobile(request.headers.get('User-Agent')):
		return render_template('index_web.html',users=paginate,page=page,title=u'寻物招领',Login=LoginVer, Type=_type)
	else:
		return render_template('index.html',users=paginate,page=page,title=u'寻物招领',Login=LoginVer, Type=_type)


@app.route("/found/detail/<int:Id>", methods=["GET"])
def detail(Id):
	if 'userid' in session and session['userid']!='':
		LoginVer=False
	else:
		LoginVer=True
	user = UserData.query.filter(UserData.Id==Id).first()
	user_info = User.query.filter(User.UserId==user.UserId).first()
	if not IsMobile(request.headers.get('User-Agent')):
		return render_template('found_detail_web.html',user=user, Login=LoginVer, user_info=user_info)
	else:
		return render_template('found_detail.html',user=user ,Login=LoginVer, user_info=user_info)


@app.route("/found/search", defaults={"page": 1}, methods=["GET"])
def search(page):
	if 'userid' in session and session['userid']!='':
		LoginVer=False
	else:
		LoginVer=True
	keyword = request.args.get("keyword", None)

	paginate = UserData.query.filter(UserData.Header.ilike("%"+keyword+"%")).order_by(UserData.Id.desc()).paginate(page, 8, False)
	if not IsMobile(request.headers.get('User-Agent')):
		return render_template('index_web.html',users=paginate,page=1,title=u'寻物招领',Login=LoginVer)
	else:
		return render_template('index.html',users=paginate,page=1,title=u'寻物招领',Login=LoginVer)


@app.route('/found/verified',methods=['GET'])
@app.route('/found/verified/<int:page>',methods=['GET'])
def verified(page=1):
	if 'adminid' not in session or session['adminid']=='':
		return redirect('/found/admin/login')
	else:
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
			admins=UserData.query.filter(UserData.Verify==True).order_by(UserData.Id.desc()).paginate(page,8,False) #test
			return render_template('verified.html',users=admins,page=page)


@app.route('/found/manage',methods=['GET','POST'])
@app.route('/found/manage/<int:page>',methods=['GET','POST'])
def manage(page=1):
	if 'userid' not in session or session['userid']=='':
		return redirect('/found/login')
	if 'userid' in session and session['userid']!='':
		LoginVer=False
	else:
		LoginVer=True
	if request.query_string:
		x=request.args
		if x['type']=='0':
			db.session.query(UserData).filter_by(Id=x['id']).delete()
		elif x['type']=='1':
			db.session.query(UserData).filter_by(Id=x['id']).update({'LostStatus':False})
		db.session.commit()
		db.session.close()
		admins=UserData.query.filter_by(UserId=session['userid']).order_by(UserData.Id.desc()).paginate(int(x['page']),5,False)

		if not IsMobile(request.headers.get('User-Agent')):
			return render_template('manage_web.html',users=admins,title=u'管理启事',page=int(x['page']))
		else:
			return render_template('manage.html',users=admins,title=u'管理启事',page=int(x['page']))
	else:
		admins=UserData.query.filter_by(UserId=session['userid']).order_by(UserData.Id.desc()).paginate(page,5,False)

		if not IsMobile(request.headers.get('User-Agent')):
			return render_template('manage_web.html',users=admins,page=page,title=u'管理启事',Login=LoginVer)
		else:
			return render_template('manage.html',users=admins,page=page,title=u'管理启事',Login=LoginVer)


@app.route("/found/admin/login", methods=["GET", "POST"])
def adminLogin():
	if request.method == 'POST':
		UserId = request.form.get("UserId", None)
		PassWord = request.form.get("PassWord", None)
		user = db.session.query(AdminUser).filter(AdminUser.UserId==UserId)[0]
		if user.PassWord == hashpw(PassWord):
			session['adminid'] = user.UserId
			return redirect("/found/admin")
		else:
			return redirect("/found/admin/login")
	return render_template("admin_login.html")


@app.route('/found/admin',methods=['GET','POST'])
@app.route('/found/admin/<int:page>',methods=['GET','POST'])
def admin(page=1):
	if 'adminid' not in session or session['adminid']=='':
		return redirect('/found/admin/login')
	else:
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
	return redirect('/found')

@app.route('/found/yiban',methods=['GET'])
def yiban():
	x=request.query_string.split('&')
	x=x[0].split('=')
	info=decrypt(x[1])
	session['userid']=info['visit_user']['userid']
	return redirect('/found')


if __name__=='__main__':
	app.run(host='0.0.0.0',port=8888, debug=True)
