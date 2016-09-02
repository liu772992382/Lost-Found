# -*- coding: utf-8 -*-

from werkzeug.utils import secure_filename
from flask import current_app
from M2Crypto import util
from Crypto.Cipher import AES
from PIL import Image
from os import urandom
import requests
import hashlib
import json

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
	MobileAgent=["iphone", "ipod", "ipad", "android", "mobile",
                "blackberry", "webos", "incognito", "webmate",
                "bada", "nokia", "lg", "ucweb", "skyfire"]
	for i in MobileAgent:
		if i in a:
			return True
	else:
		return False

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
        fname=secure_filename(f.filename)
    	im=Image.open(f)
    	im.thumbnail((160,160),Image.ANTIALIAS)
    	im.save(current_app.config.get('IMG_FLODER') + fname)
    return fname
