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
#from datetime import datetime

KIND_ENT = {'Base':'user', 'Group':'group'}
def show_group(self, message):
	#answer = User()
	print ' +- fb show_group fill FullGroup() use get_stat  In', message
	group = ndb.Key(urlsafe=message.group_url).get()
	full_group = FullGroup(name=group.key.id())
	full_group.user_group_stat = []	
#
	#print message.group_url#,  ObjectToGroup.query().fetch()[1].key().parent()#ndb.Key(urlsafe=message.group_url).urlsafe()
	objects = ObjectToGroup.query(ancestor=ndb.Key(ObjectToGroup, message.group_url)).fetch()
	self.get_role(group, message)
	for objec in objects:	
	    message.url = objec.key.id() #remove from gt_st too
	    answer = User()
	    #answer.url = objec.key.id()	
 	    get_stat(self, message, answer)# after test user.email())
	    answer.role = str(objec.role)
	    full_group.user_group_stat.append(answer) 
	    full_group.joined.append(objec.key.id())	
    #----------ask invite-------
	#entity = ndb.Key(Group, message.group_name).get()
	full_group.chat = group.chat
	#print '+==', entity.role_propertys, message.role
	for i in message.role: 	
	    if '@invite' in group.role_propertys[i]['change']:
	        for key_value, d in group.ask_join.iteritems():
		    kind = ndb.Key(urlsafe=key_value).kind()	
		    join = ToJoine(url=key_value, name=d[0], rate=d[1], time=d[2], kind=KIND_ENT[kind])	
		    full_group.ask_join.append(join)
		    #---------------------------------------
	if '__creator' in message.role: #to change roles in group
	    full_group.creator = True
	if '__id' in message.role: #to change roles in group
	    full_group.add_id = True
	#put all roles to choose in add new user table
	for role in group.role_propertys:
	    full_group.roles.append(role)
	for obj in group.top_rate:
	    full_group.top_rate.append(Rate(url=obj[0], name=obj[1], avatar=obj[2],
			   kind=obj[3], rating=obj[4]))	
	full_group.frame.extend(group.frame) 	
	#print ' +- fb show_group Out', full_group
	#print '###@', group
        return full_group

def get_stat(self, message, answer):
    #print ' -+ fb get_stat In mes ans', message, answer
    prop = get_prop(self, message) #add group_name
    prop_to_answer(self, answer, message, prop)
    answer.url = message.url
    try:
        #answer.card_id = entity.card_id
        pass	
    except AttributeError:
        pass
    #print ' ++ Out get_stat', answer 

def join_list(cur, add, stats, group_url, for_user=True):
    gstat = {}	
    s = {}	
    if True in cur:
	s = cur[True]	
    for i, st in enumerate(stats['st_name']):
	#print "666666666666666", st, add, for_user, '@' + st in add['change']
	if st in add['change']:
	    gstat[st] = []
	    gstat[st].append(stats['opt'][i])
	    gstat[st].append(1)
	elif for_user and ('@' + st) in add['change']:
	    #print '11111111111111111'
	    gstat[st] = []
	    gstat[st].append(stats['opt'][i])
	    gstat[st].append(1)
	elif st not in gstat and st not in s and st in add['visible']:
	    gstat[st] = []
	    gstat[st].append(stats['opt'][i])
	    gstat[st].append(0)
	if group_url in cur:
	#!!error if gstat have same name as already has
	    cur_update(cur[group_url], gstat)
	else:
	    cur[group_url] = gstat
    #print '--gs', gstat, ' \ncur',cur

def cur_update(cur_gurl, gstat):
    for st in gstat:
        if st in cur_gurl and cur_gurl[st][1] == 0 and gstat[st][1] == 1:
	    cur_gurl[st][1] = 1
    	else:
	    cur_gurl[st] = gstat[st]

def get_prop(self, message):
    #print ' -+ fb get_prop take all info about Group In', message
    prop = {}
    g_rates = {}	
    if message.group_url is None:	
        utg_obj = ObjectToGroup.query(ObjectToGroup.child_key==message.url).fetch()
        for gr in utg_obj:	
            group_url = gr.key.parent().id()
            group = ndb.Key(urlsafe=group_url).get()
	    self.get_role(group, message)
	    g_rates[group_url] = {'rate':group.rate}
            join_prop(self, prop, group, message, group_url, message.for_user)	
    else:
        group = ndb.Key(urlsafe=message.group_url).get()
        #print '^^^', group.role_propertys
        self.get_role(group, message)
        g_rates[message.group_url] = {'rate':group.rate}
        join_prop(self,prop, group, message, message.group_url, False)
    #print ' ++ Out get_prop', prop, '\n rate  ', g_rates    
    return prop, g_rates

def join_prop(self, prop, group, message, group_url, for_user):
    #print message.role	
    for role in message.role:
	if role in group.role_propertys:
	    join_list(prop, group.role_propertys[role], group.stats, True, for_user=for_user)
            join_list(prop, group.role_propertys[role], group.stats_private, group_url, for_user=for_user)

def prop_to_answer(self, answer, message, props):
    #print ' -+ fb prop_to_answer put entity props to answer In ans mes prop', answer, message, props 
    prop = props[0]
    entity = 0
    for group_url, stats in sorted(prop.iteritems()):
        st_bl = StatBlock(group_name="General parametrs")
        if group_url is True:
	    entity = ndb.Key(urlsafe=message.url).get()
	    #for h in entity.frame:
	    answer.frame.extend(entity.frame)
        else:
	    entity = ndb.Key(ObjectToGroup, group_url, ObjectToGroup, message.url).get()
	    st_bl.group_rate = str(props[1][group_url]['rate'][-1])
	    #print '+++', ndb.Key(urlsafe=group_url).id()
	    st_bl.group_name = ndb.Key(urlsafe=group_url).id()
	    ## !! Made url for General param???
	    st_bl.group_url = group_url	    
        st_bl.obj_url = entity.key.urlsafe()
        st_bl.obj_kind = entity.key.kind()
        #answer.stat_block.group_name.append(str(gname))
        #print '@@@@@', entity, message.whom_show, gname
        for st, opt_ch in sorted(stats.iteritems()):
            #print '->>', st, opt_ch, unicode(getattr(entity, st))
	    #print getattr(entity, st)
	    if '__A' in st:
	        itr = getattr(entity, st[:-3]+'__I')
	        nero = ndb.Key(NeroStat, str(itr), 
			NeroStat, st, NeroStat, entity.key.urlsafe(), #group and obj
			NeroStat, message.url).get()
	        if nero is not None:			
	            val = nero.val
                    st_bl.st_def.append(unicode(val))
	        else:
		    st_bl.st_def.append(unicode('your opinion'))		    
            #if type(getattr(entity, v)) == type(list()):
	    #answer.st_def.append(unicode(getattr(entity, v)[-1]))
            #else:	
             #   answer.st_def.append(unicode(getattr(entity, v)))
            #answer.st_opt.append(   )
	    else:
	        if opt_ch[0] == 'hist':
		    st_bl.st_def.append(unicode(getattr(entity, st)[-1]))
                else:	
	            st_bl.st_def.append(unicode(getattr(entity, st)))
	            #print "-------------22----",st, st_bl.st_def
            st_bl.st_name.append(st)
            st_bl.st_opt.append(opt_ch[0])
            if opt_ch[0] == 'nero':
	        st_bl.st_ch.append(bool(0))
	    else:
                st_bl.st_ch.append(bool(opt_ch[1]))
	    #if group_url: #If i need open General parametr group
	        #st_bl.group_url = message.url
	    #sorted(st_bl, key=lambda x: x[1])
	
        answer.stat_block.append(st_bl)
    if answer.stat_block is None:
	answer.stat_block.append(StatBlock())		
        #p = prop_class	
    #print ' ++ Out prop_to_answer', answer
