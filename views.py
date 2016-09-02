#!/usr/bin/env python
#coding=utf8

import os
import json
import requests
from flask import (Flask, request, render_template, redirect,
					make_response, flash, session , g ,url_for, jsonify)
from datetime import datetime
from mail import send_email
from decorators import *
from utils import *
from model import *
from time import *


@app.before_request
def before_request():
	g.posfix = '_web' if not IsMobile(request.headers.get('User-Agent')) else ''


@app.route('/found/login',methods=['GET','POST'])
def login(Warnings=''):
	LoginVer = True if session.get('userid', '') else False

	if request.method=='POST':
		form=request.form
		p=db.session.query(User).filter(User.EMail==form['EMail']).first()
		if  p!=None and p.PassWord==hashpw(form['PassWord']):
			session['userid']=p.UserId
			session['thirdLogin'] = False
			return redirect('/found')
		else:
			return render_template('login{posfix}.html'.format(posfix=g.posfix), Warnings=u'帐号或密码错误！', Login=LoginVer, title=u'登录')
	else:
		return render_template('login{posfix}.html'.format(posfix=g.posfix),Login=LoginVer,title=u'登录')


@app.route('/found/register',methods=['GET','POST'])
def register():
	LoginVer = True if session.get('userid', '') else False

	if request.method=='POST':
		form = request.form
		t=localtime()
		userdata=User()
		userdata.TrueName=form['TrueName']
		userdata.EMail=form['EMail']
		userdata.PassWord=hashpw(form['PassWord'])
		userdata.StuNumber=form['StuNumber']
		# g.userdata.RegTime=str(t[0])+'.'+str(t[1])+'.'+str(t[2])
		userdata.RegTime = '.'.join([str(t[i]) for i in range(3)])
		userid = ''.join([str(t[i]) for i in range(6)])

		if db.session.query(User).filter(User.EMail==form['EMail']).first()==None:
			userdata.UserId=userid
			db.session.add(userdata)
			db.session.commit()
			return redirect('/found/login')
		else:
			return render_template('register{posfix}.html'.format(posfix=g.posfix),title=u'注册',Login=LoginVer,Warnings=u'用户名已存在！')

	return render_template('register{posfix}.html'.format(posfix=g.posfix),title=u'注册',Login=LoginVer)


@app.route('/found/form', methods=['GET', 'POST'])
@login_required
@wrapper_user_info(mobile=False)
def form():
	if request.method=='POST':
		form = request.form
		t=localtime()
		fname = Thumbnail(request.files.get('form_file'),
						form['ThingsType'])
		userdata=UserData()
		userdata.Header = form["Header"]
		userdata.Time=form['Time']
		userdata.Place=form['Place']
		userdata.ThingsType=form['ThingsType']
		userdata.Type=form['Type']
		userdata.Content=form['Content']
		userdata.ContactWay=form['ContactWay']
		if g.user_info["type"] == "local":
			userdata.Reward = 0
		else:
			userdata.Reward=form['Reward'] if form["Reward"] else 0
		userdata.LostStatus=True
		userdata.SubTime=str(t[0])+'.'+str(t[1])+'.'+str(t[2])
		userdata.ImgPath=fname
		userdata.UserId=session['userid']
		db.session.add(userdata)
		db.session.commit()
		return redirect('/found/manage')
	#return render_template('form00.html',form =form)

	return render_template('form{posfix}.html'.format(posfix=g.posfix),title=u'发布启事',Login=True, user_info=g.user_info)


@app.route('/found/',defaults={"page": 1},methods=['GET'])
@login_required
# @app.route('/found/<int:page>',methods=['GET'])
@wrapper_user_info(mobile=False)
def index(page):
	LoginVer = True if session.get('userid', '') else False
	_type = request.args.get("type", "寻物")

	paginate = UserData.query.filter(UserData.Verify==True, UserData.LostStatus==True, UserData.Type==_type).order_by(UserData.Id.desc()).paginate(page, 18, False)

	return render_template('index{posfix}.html'.format(posfix=g.posfix),users=paginate,page=page,title=u'寻物招领',Login=LoginVer, Type=_type, user_info=g.user_info)


@app.route("/found/detail/<int:Id>", methods=["GET"])
@wrapper_user_info(mobile=False)
def detail(Id):
	LoginVer = True if session.get('userid', '') else False
	user = UserData.query.filter(UserData.Id==Id).first()
	u = User.query.filter_by(UserId=user.UserId).first()
	if u:
		username = u.TrueName
	else:
		u2 = ThirdLoginUser.query.filter_by(Type="yiban", UserId=user.UserId).first()
		username = u2.UserName

	return render_template('found_detail{posfix}.html'.format(posfix=g.posfix),user=user, Login=LoginVer, user_info=g.user_info, username=username)


@app.route("/found/search", defaults={"page": 1}, methods=["GET"])
@wrapper_user_info(mobile=False)
def search(page):
	LoginVer = True if session.get('userid', '') else False
	keyword = request.args.get("keyword", None)

	paginate = UserData.query.filter(UserData.Header.ilike("%"+keyword+"%"), UserData.LostStatus==True, UserData.Verify==True).order_by(UserData.Id.desc()).paginate(page, 18, False)

	return render_template('index{posfix}.html'.format(posfix=g.posfix),users=paginate,page=1,title=u'寻物招领',Login=LoginVer, user_info=g.user_info)


@app.route("/found/user", methods=["GET"])
@login_required
@wrapper_user_info(mobile=True)
def user():
	return render_template('user.html', title=u'我的主页', user_info=g.user_info)


@app.route("/found/money", methods=["GET", "POST"])
def money():
	if 'userid' not in session or session['userid']=='':
		return redirect('/found/login')

	if session.get("thirdLogin", None):
		user = ThirdLoginUser.query.filter_by(Type="yiban", UserId=session.get('userid', None)).first()
		access_token = user.AccessToken
	else:
		access_token = None

	return render_template("money.html", access_token=access_token)


@app.route("/found/feedback", methods=["GET", "POST"])
@login_required
@wrapper_user_info(mobile=False)
def feedback():
	if request.method == "POST":
		content = request.form.get("Content", None)
		if send_email(g.user_info["username"], content):
			return jsonify({"status": "success"})
		else:
			return jsonify({"status": "failed"})
	else:
		return render_template("feedback.html")


@app.route("/found/yibanfriend", methods=["GET", "POST"])
@login_required
@wrapper_user_info(mobile=True)
def yibanfriend():
	return render_template("yibanfriend.html", user_info=g.user_info)


@app.route('/found/verified',methods=['GET'])
@app.route('/found/verified/<int:page>',methods=['GET'])
def verified(page=1):
	if 'adminid' not in session or session['adminid']=='':
		return redirect('/found/admin/login')

	_type = request.args.get('type', '')
	_id = request.args.get('id', '')
	if _type and _id:
		if _type=='0':
			db.session.query(UserData).filter_by(Id=_id).delete()
		elif _type=='1':
			db.session.query(UserData).filter_by(Id=_id).update({'LostStatus':False})
		elif _type=='2':
			db.session.query(UserData).filter_by(Id=_id).update({'Verify':True})
		db.session.commit()

	admins=UserData.query.filter(UserData.Verify==True).order_by(UserData.Id.desc()).paginate(page,18,False)
	return render_template('verified.html',users=admins,page=page)


@app.route('/found/manage',methods=['GET','POST'])
@app.route('/found/manage/<int:page>',methods=['GET','POST'])
@login_required
@wrapper_user_info(mobile=False)
def manage(page=1):
	_type = request.args.get('type', '')
	_id = request.args.get('id', '')
	if _type:
		if _type=='0':
			db.session.query(UserData).filter_by(Id=_id).delete()
		elif _type=='1':
			db.session.query(UserData).filter_by(Id=_id).update({'LostStatus':False})
		db.session.commit()

	things_type = request.args.get('ttype', None)
	if things_type:
		admins=UserData.query.filter_by(UserId=session['userid'], Type=things_type).order_by(UserData.Id.desc()).paginate(page, 18, False)
	else:
		admins=UserData.query.filter_by(UserId=session['userid']).order_by(UserData.Id.desc()).paginate(page, 18, False)
	return render_template('manage{posfix}.html'.format(posfix=g.posfix),users=admins,title=u'管理启事',page=page, user_info=g.user_info)


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

	_type = request.args.get('type', '')
	_id = request.args.get('id', '')
	if _type and _id:
		if _type=='0':
			db.session.query(UserData).filter_by(Id=_id).delete()
		elif _type=='1':
			db.session.query(UserData).filter_by(Id=_id).update({'LostStatus':False})
		elif _type=='2':
			db.session.query(UserData).filter_by(Id=_id).update({'Verify':True})
		db.session.commit()
	admins=UserData.query.filter(UserData.Verify==False).order_by(UserData.Id.desc()).paginate(page, 18, False)
	return render_template('admin_web.html',users=admins,page=page)


@app.route('/found/logout',methods=['GET'])
def logout():
	session['userid']=''
	session["thirdLogin"] = False
	return redirect('/found')


@app.route('/found/yiban',methods=['GET'])
def yiban():
	x=request.query_string.split('&')
	x=x[0].split('=')
	info=decrypt(x[1])
	session['userid']=info['visit_user']['userid']
	session['thirdLogin'] = True
	user = ThirdLoginUser.query.filter(ThirdLoginUser.Type=="yiban",
				ThirdLoginUser.UserId==info['visit_user']['userid']).first()
	if not user:
		yibanuser = ThirdLoginUser(
				Type="yiban",
				UserId=info['visit_user']['userid'],
				UserName=info['visit_user']['username'],
				AccessToken=info['visit_oauth']['access_token'],
				TokenExpires=info['visit_oauth']['token_expires']
		)
		db.session.add(yibanuser)
		db.session.commit()
	else:
		if user.AccessToken != info['visit_oauth']['access_token']:
			user.AccessToken = info['visit_oauth']['access_token']
			user.TokenExpires = info['visit_oauth']['token_expires']
			db.session.add(user)
			db.session.commit()

	return redirect('/found')

#-----------------------------------------api--------------------------------
@app.route("/found/school/award_wx", methods=["GET"])
def award():
	s = requests.get("https://openapi.yiban.cn/school/award_wx", params=dict(request.args)).text
	return jsonify(json.loads(s))


@app.route("/found/friend/me_list", methods=["GET"])
def me_list():
	if session['thirdLogin']:
		user_temp = ThirdLoginUser.query.filter_by(UserId=session.get("userid", None)).first()
		s = requests.get("https://openapi.yiban.cn/friend/me_list?access_token={access_token}&count=8".format(access_token=user_temp.AccessToken)).text
		return jsonify(json.loads(s))
	else:
		return jsonify({"status": "failed"})


if __name__=='__main__':
	app.run(host='0.0.0.0',port=8888, debug=True)
