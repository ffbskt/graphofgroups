# -*- coding: utf-8 -*-

from models import *
#from extra_library import *
#from google.appengine.ext.ndb import msgprop
#from add_funk import make_dict_from_stat
#import time
#import logging
#import sys
#from google.appengine.api import memcache
#import re
#from random import randint
from datetime import datetime


		

def out_put_rating(self):
    table = ObjectRating.query()
    #fix what do with General Parametrs&???!! down bug
    groups = Group.query()
    #max_five = []
    objs = []
    ind = {}			
    for group in groups:
	exist_table = []
	for obj in table: # Add split for Group and Base objts
	    if group.key.urlsafe() in obj.to_dict():
		exist_table.append(obj)
	#print '+++', exist_table
	top = sorted(exist_table, key=lambda x: getattr(x, group.key.urlsafe())[-1], reverse=True)
	if len(top) >= 3:
	    top = top[:3] 
	#print '--', top
	group.top_rate=[]
	place = 1
	for obj in top:
	    rate = getattr(obj, group.key.urlsafe())[-1]	
	    group.top_rate.append([obj.key.id(), obj.name, obj.avatar,
			   obj.is_group, str(rate)])
	    entity = ndb.Key(urlsafe=obj.key.id()).get()
	    hist = (str(place) + ' place ' + obj.name + ' in group ' + group.name + ' with group rate ' + 
		  str(group.rate[-1]) + ' and own result ' + str(getattr(obj, group.key.urlsafe())[-1]) + 
			' it was at ' + datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")) 
	    place += 1
	    entity.frame.append(hist)
	    entity.put()	
	    #fill_max_five(max_five, obj.key.id(), rate, other=[obj.name, obj.avatar,
			   #obj.is_group])
	    objs.append([obj.key.id(), obj.name, obj.avatar,
			   obj.is_group, str(rate)])				 	
	group.put()
	#print group
    gen_p = ndb.Key(Group, 'ffbskt@gmail.com', Group, 'General parametrs').get()
    for o in sorted(objs, key=lambda x: x[4], reverse=True):
	if o[0] not in ind and len(ind) < 5: 
  	    ind[o[0]] = [o[0], o[1], o[2], o[3], o[4]]	
    #for i in max_five:
	#i[4] = str(i[4]) 	
    gen_p.top_rate = sorted(ind.values(), key=lambda x: x[4], reverse=True)
    #max_five = sorted(max_five, key=lambda x: , reverse=True)	
    gen_p.put()				
    #print '$$$$$$$$$$', gen_p	
    return Answer()




