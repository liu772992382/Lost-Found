#!/usr/bin/env python
#coding=utf8

import os
import json
import requests
from flask import (Flask, request, render_template, redirect,
					make_response, flash, session , g ,url_for, jsonify)
from datetime import datetime
from model import *
import time
from config import *
from functools import wraps
from werkzeug.utils import secure_filename
from PIL import Image
import hashlib
from M2Crypto import util
from Crypto.Cipher import AES

# @app.before_request
# def before_request():
# 	g.posfix = '_web' if not IsMobile(request.headers.get('User-Agent')) else ''
def Thumbnail(f, _type):
    things = [
        'kapian_icon.png',
        'qianbao_icon.png',
        'yaoshi_icon.png',
        'shouji_icon.png',
        'qita_icon.png'
    ]
    if f.filename=='':
        fname=things[int(_type)]
    else:
        fname = hashpw(f.filename.encode('utf-8'))
	im=Image.open(f)
	im.thumbnail((160,160),Image.ANTIALIAS)
	im.save(Config.IMG_FLODER + fname)
    return fname

def hashimage(upfile):
	fname = upfile.filename
	a = fname[:fname.rfind('.')].encode('utf8') + session['userid'].encode('utf8')
	ha=hashlib.md5()
	ha.update(a)
	c = str(ha.hexdigest()) + fname[fname.rfind('.'):]
	upfile.save(os.path.join(Config.IMG_FLODER, c))
	im = Image.open(Config.IMG_FLODER + c)
	im.thumbnail((160,160),Image.ANTIALIAS)
	tname = str(ha.hexdigest()) + '_thumbnail' + fname[fname.rfind('.'):]
	im.save(os.path.join(Config.IMG_FLODER, tname))
	return c


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'userid' not in session:
            return redirect('https://openapi.yiban.cn/oauth/authorize?client_id=b2b5b1d373b4433c&redirect_uri=http://f.yiban.cn/iapp57189')
        return func(*args, **kwargs)
    return wrapper

def get_time():
	return time.strftime("%Y-%m-%d %X", time.localtime())


def decrypt(data):
	iv = 'b2b5b1d373b4433c' # app id
	KEY = '61e1e18779d444ed4ee6b36946f0d898' # app secret
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




# @app.route('/found/login',methods=['GET','POST'])
# def login(Warnings=''):
# 	LoginVer = True if session.get('userid', '') else False
#
# 	if request.method=='POST':
# 		form=request.form
# 		p=db.session.query(User).filter(User.EMail==form['EMail']).first()
# 		if  p!=None and p.PassWord==hashpw(form['PassWord']):
# 			session['userid'] = p.UserId
# 			session['thirdLogin'] = False
# 			return redirect('/found')
# 		else:
# 			return render_template('login{posfix}.html'.format(posfix=g.posfix), Warnings=u'帐号或密码错误！', Login=LoginVer, title=u'登录')
# 	else:
# 		return render_template('login{posfix}.html'.format(posfix=g.posfix),Login=LoginVer,title=u'登录')


# @app.route('/found/register',methods=['GET','POST'])
# def register():
# 	# LoginVer = True if session.get('userid', '') else False
#
# 	if request.method=='POST':
# 		form = request.form
# 		t=localtime()
# 		userdata=User()
# 		userdata.TrueName=form['TrueName']
# 		userdata.EMail=form['EMail']
# 		userdata.PassWord=hashpw(form['PassWord'])
# 		userdata.StuNumber=form['StuNumber']
# 		# g.userdata.RegTime=str(t[0])+'.'+str(t[1])+'.'+str(t[2])
# 		userdata.RegTime = '.'.join([str(t[i]) for i in range(3)])
# 		userid = ''.join([str(t[i]) for i in range(6)])
#
# 		if db.session.query(User).filter(User.EMail==form['EMail']).first()==None:
# 			userdata.UserId=userid
# 			db.session.add(userdata)
# 			db.session.commit()
# 			return redirect('/found/login')
# 		else:
# 			return render_template('register{posfix}.html'.format(posfix=g.posfix),title=u'注册',Login=LoginVer,Warnings=u'用户名已存在！')
#
# 	return render_template('register{posfix}.html'.format(posfix=g.posfix),title=u'注册',Login=LoginVer)


@app.route('/found/form', methods=['GET', 'POST'])
@login_required
# @wrapper_user_info(mobile=False)
def form():
	if request.method=='POST':
		form = request.form
		fname = hashimage(request.files.get('form_file'))
		userdata=UserData()
		# userdata.Header = form["Header"]
		userdata.UserId = session['userid']
		userdata.UserNick = session['user_info']['info']['yb_usernick']
		userdata.UserImg = session['user_info']['info']['yb_userhead']
		userdata.Time = form['Time']
		userdata.Place = form['Place']
		userdata.Type = form['Type']
		userdata.Content = form['Content']
		userdata.ContactWay = form['ContactWay']
		# if g.user_info["type"] == "local":
		# 	userdata.Reward = 0
		# else:
		# 	userdata.Reward=form['Reward'] if form["Reward"] else 0
		userdata.LostStatus = True
		userdata.SubTime = get_time()
		userdata.ImgPath = fname
		# userdata.DataId = session['userid']
		db.session.add(userdata)
		db.session.commit()
		return redirect('/found/')
	#return render_template('form00.html',form =form)

	return render_template('form.html', title=u'发布启事', form = True)


@app.route('/found/',defaults={"page": 1},methods=['GET'])
@login_required
# @app.route('/found/<int:page>',methods=['GET'])
# @wrapper_user_info(mobile=False)
def index(page):
	# LoginVer = True if session.get('userid', '') else False
	# _type = request.args.get("type", "寻物")

	paginate = UserData.query.order_by(UserData.SubTime.desc()).all()
	for i in paginate:
		try:
			rpos = i.ImgPath.rfind('.')
			i.thumbnail = i.ImgPath[:rpos] + '_thumbnail' + i.ImgPath[rpos:]
		except:
			continue
	return render_template('index.html', users = paginate, page = page, title = u'寻物招领', index = True)




# @app.route("/found/detail/<int:Id>", methods=["GET"])
# # @wrapper_user_info(mobile=False)
# def detail(Id):
# 	LoginVer = True if session.get('userid', '') else False
# 	user = UserData.query.filter(UserData.Id==Id).first()
# 	u = User.query.filter_by(UserId=user.UserId).first()
# 	if u:
# 		username = u.TrueName
# 	else:
# 		u2 = ThirdLoginUser.query.filter_by(Type="yiban", UserId=user.UserId).first()
# 		username = u2.UserName
#
# 	return render_template('found_detail{posfix}.html'.format(posfix=g.posfix),user=user, Login=LoginVer, user_info=g.user_info, username=username)
#
#
# @app.route("/found/search", defaults={"page": 1}, methods=["GET"])
# # @wrapper_user_info(mobile=False)
# def search(page):
# 	LoginVer = True if session.get('userid', '') else False
# 	keyword = request.args.get("keyword", None)
#
# 	paginate = UserData.query.filter(UserData.Header.ilike("%"+keyword+"%"), UserData.LostStatus==True, UserData.Verify==True).order_by(UserData.Id.desc()).paginate(page, 18, False)
#
# 	return render_template('index{posfix}.html'.format(posfix=g.posfix),users=paginate,page=1,title=u'寻物招领',Login=LoginVer, user_info=g.user_info)


@app.route("/found/me", methods=["GET"])
@login_required
# @wrapper_user_info(mobile=True)
def user():
	if session['user_info']['status']:
		user_info = session['user_info']['info']
		error = False
	else:
		error = True
		user_info = User()
	infos = db.session.query(UserData).all()
	return render_template('Me.html', title=u'我的主页', user_info = user_info, me = True, error = error, infos = infos)


@app.route('/found/myinfo',methods = ['GET'])
@login_required
def myinfo():
	if request.method == 'GET':
		infos = db.session.query(UserData).filter_by(UserId = session['userid']).order_by(UserData.SubTime.desc()).all()
		for i in infos:
			try:
				rpos = i.ImgPath.rfind('.')
				i.thumbnail = i.ImgPath[:rpos] + '_thumbnail' + i.ImgPath[rpos:]
			except:
				continue
		return render_template('MyInfo.html', me = True, infos = infos, title = u'我发布的信息')


@app.route('/found/mystar',methods = ['GET'])
@login_required
def mystar():
	if request.method == 'GET':
		stars = db.session.query(Star).filter_by(UserId = session['userid']).order_by(Star.StarTime.desc()).all()
		infos = []
		for i in stars:
			infos.append(db.session.query(UserData).filter_by(did = i.did).first())
		for i in infos:
			try:
				rpos = i.ImgPath.rfind('.')
				i.thumbnail = i.ImgPath[:rpos] + '_thumbnail' + i.ImgPath[rpos:]
			except:
				continue
		return render_template('MyStar.html', me = True, infos = infos, title = u'我发布的信息')


@app.route('/found/info_delete',methods = ['POST'])
def info_delete():
	try:
		delete_id = request.form['delete_id']
		delete_info = db.session.query(UserData).filter_by(did = delete_id).first()
		db.session.delete(delete_info)
		db.session.commit()
		return 'success'
	except:
		return 'error'


@app.route('/found/unstar',methods = ['POST'])
def unstar():
	try:
		delete_id = request.form['unstar_id']
		delete_info = db.session.query(Star).filter_by(did = delete_id,UserId = session['userid']).first()
		db.session.delete(delete_info)
		db.session.commit()
		return 'success'
	except:
		return 'error'


@app.route('/found/report', methods = ['POST'])
def report():
	try:
		report_id = request.form['did']
		report_data = db.session.query(UserData).filter_by(did = report_id).first()
		ru = report_data.ReportUsers.split(',')
		if session['userid'] not in ru:
			report_data.Report += 1
			report_data.ReportUsers += ',' + session['userid']
			return 'success'
		else:
			return 'error'
	except:
		return 'error'


@app.route('/found/star', methods = ['POST'])
def star():
	# try:
	star_id = request.form['star_id']
	star_data = db.session.query(Star).filter_by(did = star_id,UserId = session['userid']).first()
	if star_data == None:
		new_star = Star()
		new_star.did = star_id
		new_star.UserId = session['userid']
		new_star.StarTime = get_time()
		db.session.add(new_star)
		db.session.commit()
		return 'success'
	else:
		return 'error'
	# except:
	# 	return 'error'


# @app.route("/found/money", methods=["GET", "POST"])
# def money():
# 	if 'userid' not in session or session['userid']=='':
# 		return redirect('/found/login')
#
# 	if session.get("thirdLogin", None):
# 		user = ThirdLoginUser.query.filter_by(Type="yiban", UserId=session.get('userid', None)).first()
# 		access_token = user.AccessToken
# 	else:
# 		access_token = None
#
# 	return render_template("money.html", access_token=access_token)
#
#
# @app.route("/found/feedback", methods=["GET", "POST"])
# @login_required
# # @wrapper_user_info(mobile=False)
# def feedback():
# 	if request.method == "POST":
# 		content = request.form.get("Content", None)
# 		if send_email(g.user_info["username"], content):
# 			return jsonify({"status": "success"})
# 		else:
# 			return jsonify({"status": "failed"})
# 	else:
# 		return render_template("feedback.html")


# @app.route("/found/yibanfriend", methods=["GET", "POST"])
# @login_required
# # @wrapper_user_info(mobile=True)
# def yibanfriend():
# 	return render_template("yibanfriend.html", user_info=g.user_info)


# @app.route('/found/verified',methods=['GET'])
# @app.route('/found/verified/<int:page>',methods=['GET'])
# def verified(page=1):
# 	if 'adminid' not in session or session['adminid']=='':
# 		return redirect('/found/admin/login')
#
# 	_type = request.args.get('type', '')
# 	_id = request.args.get('id', '')
# 	if _type and _id:
# 		if _type=='0':
# 			db.session.query(UserData).filter_by(Id=_id).delete()
# 		elif _type=='1':
# 			db.session.query(UserData).filter_by(Id=_id).update({'LostStatus':False})
# 		elif _type=='2':
# 			db.session.query(UserData).filter_by(Id=_id).update({'Verify':True})
# 		db.session.commit()
#
# 	admins=UserData.query.filter(UserData.Verify==True).order_by(UserData.Id.desc()).paginate(page,18,False)
# 	return render_template('verified.html',users=admins,page=page)


# @app.route('/found/manage',methods=['GET','POST'])
# @app.route('/found/manage/<int:page>',methods=['GET','POST'])
# @login_required
# # @wrapper_user_info(mobile=False)
# def manage(page=1):
# 	_type = request.args.get('type', '')
# 	_id = request.args.get('id', '')
# 	if _type:
# 		if _type=='0':
# 			db.session.query(UserData).filter_by(Id=_id).delete()
# 		elif _type=='1':
# 			db.session.query(UserData).filter_by(Id=_id).update({'LostStatus':False})
# 		db.session.commit()
#
# 	things_type = request.args.get('ttype', None)
# 	if things_type:
# 		admins=UserData.query.filter_by(UserId=session['userid'], Type=things_type).order_by(UserData.Id.desc()).paginate(page, 18, False)
# 	else:
# 		admins=UserData.query.filter_by(UserId=session['userid']).order_by(UserData.Id.desc()).paginate(page, 18, False)
# 	return render_template('manage{posfix}.html'.format(posfix=g.posfix),users=admins,title=u'管理启事',page=page, user_info=g.user_info)


# @app.route("/found/admin/login", methods=["GET", "POST"])
# def adminLogin():
# 	if request.method == 'POST':
# 		UserId = request.form.get("UserId", None)
# 		PassWord = request.form.get("PassWord", None)
# 		user = db.session.query(AdminUser).filter(AdminUser.
# 		UserId = request.form.get("UserId", None)
# 		PassWord = request.form.get("PassWord", None)
# 		user = db.session.query(AdminUser).filter(AdminUser.UserId==UserId)[0]
# 		if user.PassWord == hashpw(PassWord):
# 			session['adminid'] = user.UserId
# 			return redirect("/found/admin")
# 		else:
# 			return redirect("/found/admin/login")
# 	return render_template("admin_login.html")


# @app.route('/found/admin',methods=['GET','POST'])
# @app.route('/found/admin/<int:page>',methods=['GET','POST'])
# def admin(page=1):
# 	if 'adminid' not in session or session['adminid']=='':
# 		return redirect('/found/admin/login')
#
# 	_type = request.args.get('type', '')
# 	_id = request.args.get('id', '')
# 	if _type and _id:
# 		if _type=='0':
# 			db.session.query(UserData).filter_by(Id=_id).delete()
# 		elif _type=='1':
# 			db.session.query(UserData).filter_by(Id=_id).update({'LostStatus':False})
# 		elif _type=='2':
# 			db.session.query(UserData).filter_by(Id=_id).update({'Verify':True})
# 		db.session.commit()
# 	admins=UserData.query.filter(UserData.Verify==False).order_by(UserData.Id.desc()).paginate(page, 18, False)
# 	return render_template('admin_web.html',users=admins,page=page)


# @app.route('/found/logout',methods=['GET'])
# def logout():
# 	session['userid']=''
# 	session["thirdLogin"] = False
# 	return redirect('/found')

@app.route('/found/admin',methods = ['GET'])
def admin():
	try:
		if hashpw(request.args.get('key')) == '13562d307759d1275a92ac4b185f0ac5':
			infos = db.session.query(UserData).all()
			for i in infos:
				try:
					rpos = i.ImgPath.rfind('.')
					i.thumbnail = i.ImgPath[:rpos] + '_thumbnail' + i.ImgPath[rpos:]
				except:
					continue
			return render_template('Admin.html', infos = infos)
		else:
			return '#-_-'
	except:
		return '#-_-'	

@app.route('/found/yiban',methods=['GET'])
def yiban():
	try:
		x=request.args.get('verify_request')
		print x
		info=decrypt(x)
		print info
		session['access_token'] = info['visit_oauth']['access_token']
		r1 = requests.get('https://openapi.yiban.cn/user/me?access_token=' + info['visit_oauth']['access_token'])
		session['user_info'] = r1.json()
		session['userid'] = session['user_info']['info']['yb_userid']
		return redirect('/found/me')
	except:
		'认证失败'
	# session['userid']=info['visit_user']['userid']
	# session['thirdLogin'] = True
	# user = ThirdLoginUser.query.filter(ThirdLoginUser.Type=="yiban",
	# 			ThirdLoginUser.UserId==info['visit_user']['userid']).first()
	# if not user:
	# 	yibanuser = ThirdLoginUser(
	# 			Type="yiban",
	# 			UserId=info['visit_user']['userid'],
	# 			UserName=info['visit_user']['username'],
	# 			AccessToken=info['visit_oauth']['access_token'],
	# 			TokenExpires=info['visit_oauth']['token_expires']
	# 	)
	# 	db.session.add(yibanuser)
	# 	db.session.commit()
	# else:
	# 	if user.AccessToken != info['visit_oauth']['access_token']:
	# 		user.AccessToken = info['visit_oauth']['access_token']
	# 		user.TokenExpires = info['visit_oauth']['token_expires']
	# 		db.session.add(user)
	# 		db.session.commit()


#-----------------------------------------api--------------------------------
# @app.route("/found/school/award_wx", methods=["GET"])
# def award():
# 	s = requests.get("https://openapi.yiban.cn/school/award_wx", params=dict(request.args)).text
# 	return jsonify(json.loads(s))
#
#
# @app.route("/found/friend/me_list", methods=["GET"])
# def me_list():
# 	if session['thirdLogin']:
# 		user_temp = ThirdLoginUser.query.filter_by(UserId=session.get("userid", None)).first()
# 		s = requests.get("https://openapi.yiban.cn/friend/me_list?access_token={access_token}&count=8".format(access_token=user_temp.AccessToken)).text
# 		return jsonify(json.loads(s))
# 	else:
# 		return jsonify({"status": "failed"})


if __name__=='__main__':
	app.run( debug=True, host='0.0.0.0', port=7777)
