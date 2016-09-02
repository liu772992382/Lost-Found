#!/usr/bin/env python
#coding=utf8
from model import * 
a=db.session.query(UserData).filter(or_(UserData.Header.like("%s%"),UserData.Place.like('%s%')))
print a
