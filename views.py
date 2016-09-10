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

#---------------------------------------函数-------------------------------------

#-------------------------------------------------------------------------------
#压缩图片并返回md5文件名
def hashimage(upfile):
	fname = upfile.filename
	a = fname[:fname.rfind('.')].encode('utf8')# + session['userid'].encode('utf8')
	ha=hashlib.md5()
	ha.update(a)
	c = str(ha.hexdigest()) + fname[fname.rfind('.'):]
	upfile.save(os.path.join(Config.IMG_FLODER, c))
	im = Image.open(Config.IMG_FLODER + c)
	im.thumbnail((160,160),Image.ANTIALIAS)
	tname = str(ha.hexdigest()) + '_thumbnail' + fname[fname.rfind('.'):]
	im.save(os.path.join(Config.IMG_FLODER, tname))
	return c

#-------------------------------------------------------------------------------
#登陆状态验证
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'userid' not in session:
            return redirect('https://openapi.yiban.cn/oauth/authorize?client_id=b2b5b1d373b4433c&redirect_uri=http://f.yiban.cn/iapp57189')
        return func(*args, **kwargs)
    return wrapper

#-------------------------------------------------------------------------------
#获取规定格式时间
def get_time():
	return time.strftime("%Y-%m-%d %X", time.localtime())

#-------------------------------------------------------------------------------
#解码易班登陆参数
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

#-------------------------------------------------------------------------------
#md5加密，返回加密后的字符串
def hashpw(a):
	ha=hashlib.md5()
	ha.update(a)
	return str(ha.hexdigest())

#--------------------------------------路由--------------------------------------

#-------------------------------------------------------------------------------
#首页
@app.route('/found/',defaults={"page": 1},methods=['GET'])
@login_required
def index(page):

	paginate = UserData.query.order_by(UserData.SubTime.desc()).all()
	for i in paginate:
		try:
			rpos = i.ImgPath.rfind('.')
			i.thumbnail = i.ImgPath[:rpos] + '_thumbnail' + i.ImgPath[rpos:]
		except:
			continue
	return render_template('index.html', users = paginate, page = page, title = u'寻物招领', index = True)

#-------------------------------------------------------------------------------
#表单的提交
@app.route('/found/form', methods=['GET', 'POST'])
@login_required
def form():
	if request.method=='POST':
		try:
			form = request.form
			fname = hashimage(request.files.get('form_file'))
			userdata=UserData()
			userdata.UserId = session['userid']
			userdata.UserNick = session['user_info']['info']['yb_usernick']
			userdata.UserImg = session['user_info']['info']['yb_userhead']
			userdata.Time = form.get('Time')
			userdata.Place = form.get('Place')
			userdata.Type = form.get('Type')
			userdata.Content = form.get('Content')
			userdata.ContactWay = form.get('ContactWay')
			userdata.LostStatus = True
			userdata.SubTime = get_time()
			userdata.ImgPath = fname
			db.session.add(userdata)
			db.session.commit()
			return redirect('/found/')
		except:
			return render_template('form.html', title=u'发布启事', form = True, error = True)

	return render_template('form.html', title=u'发布启事', form = True)



#-------------------------------------------------------------------------------
#我的主页
@app.route("/found/me", methods=["GET"])
@login_required
def user():
	if session['user_info']['status']:
		user_info = session['user_info']['info']
		error = False
	else:
		error = True
		user_info = User()
	infos = db.session.query(UserData).all()
	return render_template('Me.html', title=u'我的主页', user_info = user_info, me = True, error = error, infos = infos)

#-------------------------------------------------------------------------------
#我发布的信息
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

#-------------------------------------------------------------------------------
#我收藏的信息
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

#-------------------------------------------------------------------------------
#举报信息
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

#-------------------------------------------------------------------------------
#收藏信息
@app.route('/found/star', methods = ['POST'])
def star():
	try:
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
	except:
		return 'error'

#-------------------------------------------------------------------------------
#删除信息
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

#-------------------------------------------------------------------------------
#取消收藏
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

#-------------------------------------------------------------------------------
#管理信息
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

#-------------------------------------------------------------------------------
#获得易班授权
@app.route('/found/yiban',methods=['GET'])
def yiban():
	try:
		x=request.args.get('verify_request')
		info=decrypt(x)
		session['access_token'] = info['visit_oauth']['access_token']
		r1 = requests.get('https://openapi.yiban.cn/user/me?access_token=' + info['visit_oauth']['access_token'])
		session['user_info'] = r1.json()
		session['userid'] = session['user_info']['info']['yb_userid']
		return redirect('/found/me')
	except:
		'认证失败'


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
