# -*- coding: utf-8 -*-
#import endpoints
#from google.appengine.api import users
#from protorpc import messages
#from protorpc import message_types
#from protorpc import remote
#from google.appengine.ext import ndb
#from google.appengine.api import mail
#import json
from models import *
#from extra_library import *
#from google.appengine.ext.ndb import msgprop
#from add_funk import make_dict_from_stat
import time
#import logging
#import sys
#from google.appengine.api import memcache
#import re
#from random import randint

def compute_top_raiting(self, child, begin, parent=[], date=time.time()):
    #!! ?? add val with parrent to do't load parrent valeue each time	
    #self.show_picture(ShowPict())
    objects = ObjectToGroup.query(ancestor=ndb.Key(ObjectToGroup, child)).fetch(keys_only=True)
    #print "REFG__________2", objects	
    if objects != [] and objects[0]:	
        self.compute_rate(Show(group_url=child))
	#local_parent=parent[:]
	parent.append(child)
	#print 'child  ', ndb.Key(urlsafe=child).id()
	#for p in parent:
	    #print 'parent  ', ndb.Key(urlsafe=p).id()		
        for obj in objects:
	    compute_top_raiting(self, obj.id(), begin, parent[:])    
    else:
	parent.reverse()
	obj_rate = ndb.Key(ObjectRating, child).get()
#Debag mess
	print "\n______Start fill table________"
	
	obj_name = ndb.Key(urlsafe=child).id()
	print obj_name
#finish Debag
	for i in xrange(len(parent) - 1):
   	    current, next = parent[i], parent[i + 1]
    	    print '++', current, next, #ndb.Key(urlsafe=child).id(), ndb.Key(urlsafe=current).id(), ndb.Key(urlsafe=next).id()
	    print 'groups', ndb.Key(urlsafe=current).get().name, ndb.Key(urlsafe=next).get().name
	    
	    prevent_val = getattr(obj_rate, current)[-1]
	    parent_val = getattr(ndb.Key(ObjectRating, current).get(), next)[-1]
	    next_val = parent_val * prevent_val
	    #print '+++', 	
	    if next in obj_rate.to_dict():	 	
	        old_value = getattr(obj_rate, next)[-1]
		getattr(obj_rate, next).extend([date, next_val+old_value])
	    else:	    	
		setattr(obj_rate, next, [date, next_val])
	    print '--!!--', obj_rate
	    print '--', prevent_val, parent_val, next_val 	
	obj_rate.put()	
	#print '____up___', child, parent
	#go_up(self, child, begin)

# ADD DATA Date !!??
def compute_rating(self, group_url):
	group = ndb.Key(urlsafe=group_url).get()
	#only for private_stat. For Base add ndb(Base/Group)... and group.stat
	objects = ObjectToGroup.query(ancestor=ndb.Key(ObjectToGroup, group.key.urlsafe())).fetch()
	rank_st_name = []
	rank_dict = {}
	for i, opt in enumerate(group.stats_private['opt']):
	    if opt == 'ranking':
		rank_st_name.append(group.stats_private['st_name'][i])
	print '!!1', rank_st_name
	for obj in objects:
	    rank_list = []
	    for st_name in rank_st_name:
		rank_list.append(float(getattr(obj, st_name)))
	    print '!!2', rank_list
	    rank_dict[obj.key.urlsafe()] = rank_list	
	print '!!3', rank_dict, group.st_place
	final_dict = compute_place_rating(group.st_place, rank_dict)
	print '!!4', final_dict
	date = time.time()
	for obj in objects:
	    sum_rank = 0	
	    for i, n in enumerate(rank_st_name):
		setattr(obj, n + '__R', final_dict[obj.key.urlsafe()][i])
	    list_rank = list_mult(group.st_w, final_dict[obj.key.urlsafe()])
	    sum_rank = sum(list_rank)
	    obj_rate = ndb.Key(ObjectRating, ndb.Key(urlsafe=obj.key.id()).urlsafe()).get()	
	    if obj_rate is None or group.key.urlsafe() not in obj_rate.to_dict():
		entity = ndb.Key(urlsafe=obj.key.id()).get()
		is_group = False
		if entity.key.kind() == 'Group':
		    is_group = True
		obj_rate = ObjectRating(name=entity.name, avatar=entity.avatar, is_group=is_group)
	    	setattr(obj_rate, group.key.urlsafe(), [date, sum_rank]) 
	        obj_rate.key = ndb.Key(ObjectRating, ndb.Key(urlsafe=obj.key.id()).urlsafe())
	    else:
		getattr(obj_rate, group.key.urlsafe()).extend([date, sum_rank])
	    #base_antety = ndb.Key(urlsafe=obj.key.id()).get()
	    #print "sssssssssssssssssssssssssss", base_antety.rate, obj.rate
	    #base_antety.rate.extend([time.time(), get_rate(base_antety) - get_rate(obj) + sum(sum_rank)]) # coeficent fogoten
	    #group.rate.extend(time.time(), group.rate[-1] + -obj.rate[-1] + sum(sum_rank)
	    obj.rate.extend([time.time(), sum_rank])	#?? !!
	    obj_rate.put()	
	    obj.put()
        return Answer()

def list_mult(lista, listb):
    #print "++++++++++", lista, listb	
    return [a*b for a,b in zip(lista,listb)]

def compute_place_rating(st_place, users):
    matr = []
    for i, st in enumerate(st_place):
	#print '@', users.items(), i#, val_list[i]
	if st == 1:
	    for usr, val_list in users.items():
		if float(val_list[i]) == 0.0:
		    val_list[i] = 99999999
		#print val_list[i] 
	    matr = sorted(users.items(), key=lambda x: x[1][i])
	    mult_rating(matr, i)
	    for usr, val_list in users.items():
		if val_list[i] == 99999999:
		    val_list[i] = 0 
	    users = dict(matr)
	if st == 2:
	    
	    matr = sorted(users.items(), key=lambda x: x[1][i], reverse=True)
	    mult_rating(matr, i)
    return dict(matr)
	
def mult_rating(matr, i):
    k = 0
    l = len(matr)	
    p = matr[0][1][i]
    same_place = []
    for j in range(l):
	k += 1
 	if p == matr[j][1][i]:
	    same_place.append(j)
	elif j == l - 1:
	    for sp in same_place:
		matr[sp][1][i] = l / (2.0 * (k - 1)) 
	    if j not in same_place:
	        matr[j][1][i] = l / (2.0 * k)
	else: 	   
	    p = matr[j][1][i]
	    for sp in same_place:
		matr[sp][1][i] = l / (2.0 * (k - 1))
	    same_place = []
	    same_place.append(j)


if __name__ == "__main__":
    users = {'a':[0,2,5], 'e':[3,1,5], 'b':[4,2,4], 'c':[3,2,3]}
# 	{'a':[2,2,5], 'e':[0.6,1,5], 'b':[0.5,2,4], 'c':[0.6,2,3]}
    st_place = [1,0,2]
    print compute_rating(st_place, users)
#print users
