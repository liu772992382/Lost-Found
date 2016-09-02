#coding=utf8

from flask import session, redirect, g, request
from functools import wraps
from model import *
import requests
import json


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'userid' not in session or session['userid']=='':
            return redirect('/found/login')
        return func(*args, **kwargs)
    return wrapper


def wrapper_user_info(**kwargs0):
    def handle(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            g.user_info = {}
            # 如果登录
            if 'userid' in session and session['userid']:
            	if not session.get('thirdLogin', False):
            		user = User.query.filter(User.UserId==session.get('userid', None)).first()
            		g.user_info["username"] = user.TrueName
            		g.user_info["type"] = "local"
                        # 用于在移动端
                        if not g.posfix:
                            g.user_info["stunumber"] = user.StuNumber
                            g.user_info["headimg"] = "/static/img/headimg/yiban.jpg"
            	else:
                    user_temp = ThirdLoginUser.query.filter_by(Type="yiban", UserId=session.get('userid', None)).first()
                    g.user_info["type"] = "yiban"
                    g.user_info["username"] = user_temp.UserName
                    # 用户在移动端且需要详细信息
                    if not g.posfix and kwargs0.get("mobile", False):
                    	user = requests.get("https://openapi.yiban.cn/user/real_me?access_token="+user_temp.AccessToken, verify=False).text
                    	user_j = json.loads(user)
                    	if user_j['status'] == "success":
                    		g.user_info["headimg"] = user_j["info"]["yb_userhead"]
                    		g.user_info["stunumber"] = user_j["info"]["yb_studentid"]
                    		g.user_info["money"] = user_j["info"]["yb_money"]
            return func(*args, **kwargs)
    	return wrapper
    return handle
