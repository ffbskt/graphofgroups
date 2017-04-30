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
import suported_function
#from extra_library import *
#from google.appengine.ext.ndb import msgprop
#from add_funk import make_dict_from_stat
#import time
#import logging
#import sys
#from google.appengine.api import memcache
#import re
#from random import randint
#from datetime import datetime

IF_BASE = {True:'stats', False:'stats_private'}
# 0 - {mail:[data,val]}
# nero - {mail:[data,val,cor]} + w + compute
#OPT = {'link':unicode,'string':unicode,'integer':int,'float':float,'nero':{},'0':{}, 'ranking':[int, float]}

#LAMBDA = 0.4



def create_groups(self, message):
    print ' +- fb create_groups. in', message 
    #Allways create new separate group, and we need a parent for make ObjectToGroup
    for name in message.name.split(', '): #what is admin??
        #if message.parent_group is None:
            #message.parent_group = message.name
        entity = ndb.Key(Group, message.creator_mail, Group, name).get()
        if entity is not None:	
	   #??? in key if mail == admin!!
	    entity = edit_group(self, message, entity)
	    if 'ask_join' in message.role_delete:
	        entity.ask_join = {}
	    if 'ban' in message.role_delete:
	        entity.ban = []
	    if message.free is not None:
	        entity.free = message.free
 	    entity.st_place=message.st_place
            entity.st_w=message.st_w	
	    entity.content=message.content
            entity.public_view=message.public_view
            entity.parent_group=message.parent_group
	    entity.put()
	    print '^^^^^^^^^', entity, message.st_w	
	    #print '1', entity.name
	    continue
	       #print "0111", name
	entity = Group(name=name)
	entity.key = ndb.Key(Group, message.creator_mail, Group, name) 
        entity.put()# or remove all default from list!!!		
        entity = edit_group(self, message, entity) 
        
        if name != 'General parametrs':
            self.put_object_to_group(PutObjectTo(child_object=name,  child_gr_author=message.creator_mail, group_name='General parametrs', group_creator='ffbskt@gmail.com', role='group'))
        #else: #!!>?? what do with g rate???
    	#entity.rate.extend([time.time(), 0])	
        entity.name = name
        entity.content=message.content
        entity.free=message.free
        entity.st_place=message.st_place
        entity.st_w=message.st_w
        entity.public_view=message.public_view
        entity.parent_group=message.parent_group		
        entity.put()
        #print ' ++ Out create_groups', entity
    return Answer(ans = 'Sucses')



def update(self, message):
    #print '  +- fb  update group and fill_atr for all obj"s there In. ', message 
    entity = ndb.Key(Group, message.creator_mail, Group, message.name).get()		
    if entity.key.parent().id() == message.creator_mail:
        objects = ObjectToGroup.query(ancestor=ndb.Key(ObjectToGroup, entity.key.urlsafe())).fetch()
	    	
        for object in objects:
		#ch_obj = 0
		#if '@' in object.name: # !! EROR??? object.mail/ key_value
		   # ch_obj = ndb.Key(Base, object.name).get()
		#else:
		    #ch_obj = ndb.Key(Group, object.name).get()		
    	    base_entity = ndb.Key(urlsafe=object.key.id()).get()
	    #print '_________', entity.stats, base_entity
            self.fill_attr(entity.stats, base_entity)#entity.parent_group
    	    self.fill_attr(entity.stats_private, object)
	    object.put()
	    base_entity.put()
		#print ' ++ Out', object
	return Answer(ans = 'Sucses')
    return Answer(ans = 'only creator')

def edit_group(self, message, entity):
	#print "START ", entity.key, entity.role_propertys, message
	#print ' +- fb edit_group add stat from message', message, '\n to entity', entity
	suported_function.join_st(message.st_name, message.st_ifbase, False) # add False if st_name haven't st_
 	ranking_stat = []
	nero = []
	nero_a = []
	like = []
	for i, n, ifbase in zip(range(len(message.st_name)), message.st_name, message.st_ifbase):
	    if n not in getattr(entity, IF_BASE[ifbase])['st_name']:
	        getattr(entity, IF_BASE[ifbase])['st_name'].append(unicode(n))
	    	if message.st_def.__len__() > i:
	            getattr(entity, IF_BASE[ifbase])['value'].append(unicode(message.st_def[i]))
	    	else:
		    getattr(entity, IF_BASE[ifbase])['value'].append(unicode(0))
	    	if message.st_opt.__len__() > i:
	            getattr(entity, IF_BASE[ifbase])['opt'].append(unicode(message.st_opt[i]))
	    	else:
		    getattr(entity, IF_BASE[ifbase])['opt'].append(unicode(0))
	    if message.st_opt.__len__() > i:
		if message.st_opt[i] == 'ranking' and unicode(n + '__R') not in entity.stats['st_name']:
			ranking_stat.append(unicode(n + '__R'))
			getattr(entity, IF_BASE[ifbase])['st_name'].append(unicode(n + '__R'))
			getattr(entity, IF_BASE[ifbase])['value'].append([time.time(), 0.0]) #[] to comp derivative, data???
			getattr(entity, IF_BASE[ifbase])['opt'].append(unicode('points'))
		if message.st_opt[i] == 'nero' and unicode(n + '__A') not in entity.stats['st_name']:
			nero.extend([unicode(n + '__W'), unicode(n + '__I')])
			nero_a.append(unicode(n + '__A'))			
			getattr(entity, IF_BASE[ifbase])['st_name'].append(unicode(n + '__A'))
			getattr(entity, IF_BASE[ifbase])['value'].append(0) #[] to comp derivative, data???
			getattr(entity, IF_BASE[ifbase])['opt'].append(unicode('a'))
			getattr(entity, IF_BASE[ifbase])['st_name'].append(unicode(n + '__W'))
			getattr(entity, IF_BASE[ifbase])['value'].append(0.1) #[] to comp derivative, data???
			getattr(entity, IF_BASE[ifbase])['opt'].append(unicode('w'))
			getattr(entity, IF_BASE[ifbase])['st_name'].append(unicode(n + '__I'))
			getattr(entity, IF_BASE[ifbase])['value'].append(0) #[] to comp derivative, data???
			getattr(entity, IF_BASE[ifbase])['opt'].append(unicode('itr'))	
		#Each stat - nero Add nero here (3 - nero) ? without itr?
		#getattr(entity, IF_BASE[ifbase])['st_name'].append(unicode(n + '__WT, WL, WM'))	  
	try:
	    for d in message.role_delete:
	        entity.role_propertys[d] = {'change':[], 'visible':[]}
	except: #keyval
	    pass
	for nm in message.role_propertys_add:
	    #print "CHANGE PROPERTY", message.role_propertys_add
	    name = unicode(nm.name)
	    if not entity.role_propertys.has_key(name):
	        entity.role_propertys[name] = {'change':[], 'visible':[]}
	    for role_prop in nm.change:
		if unicode(role_prop) not in entity.role_propertys[name]['change']:
		    getattr(entity, 'role_propertys')[name]['change'].append(role_prop)	
	            #entity.role_propertys[name]['change'].append(role_prop) #problem with group
	    for visible in nm.visible:
		if unicode(visible) not in entity.role_propertys[name]['visible']:
 	            entity.role_propertys[name]['visible'].append(visible)
	    #print "RES  ch ", entity.role_propertys[name]['change']
	    #If not in rp
	    for st_name in ranking_stat:
	        entity.role_propertys[name]['visible'].append(st_name)
	    for st_name in nero:
		#print 'IS DA', st_name[:-3] in nm.change, st_name[:-3]   
		if st_name[:-3] in nm.change:
	            entity.role_propertys[name]['visible'].append(st_name)
	    for st_name in nero_a:
		if st_name[:-3] in nm.change:
	            entity.role_propertys[name]['change'].append(st_name)
	    #for st_name in like:
		#entity.role_propertys[name]['change'].append(st_name)
	#print ' ++ Out edit_group', entity	
	return entity

