﻿# -*- coding: utf-8 -*-

# Show group, and home page visible stat full. Need admin, user change stat 

import endpoints
from google.appengine.api import users
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import ndb
from google.appengine.api import mail
import json
from models import *
#from extra_library import *
#from google.appengine.ext.ndb import msgprop
#from add_funk import make_dict_from_stat
import time
import datetime
import logging
import sys
import os
#from test import *
from nero import *
from rating import *
from lib import out_put_rating, show, build, test	 
from google.appengine.api import app_identity
import cloudstorage
import mimetypes
import base64



JS_CLIENT_ID = 'your client key same as in GG.py'


IF_BASE = {True:'stats', False:'stats_private'}
# 0 - {mail:[data,val]}
# nero - {mail:[data,val,cor]} + w + compute
OPT = {'link':unicode,'string':unicode,'integer':int,'float':float,'nero':{},'0':{}, 'ranking':[int, float]}

LAMBDA = 0.4
TBANK = {'In':{}, 'Out':{}} #test bank

def to_str(k):
	if k is None:
	   return ''
	return k
def get_rate(entity):
    #print "_____________", dir(entity), entity.to_dict()	
    if 'rate' in entity._to_dict() and len(entity.rate) > 0:
	return entity.rate[-1]
    entity.rate.extend([time.time(), 0.0])	
    return 0.0	

	



	 

def split_message(*args):
    m = max([x.split(', ').__len__() for x in args if x is not None])
    spl = []
    for st in args:
	if st is not None:
	    ln = st.split(', ')
    	else:
	    ln = [None,]
	while ln.__len__() < m:
	    ln.append(ln[-1])
    	spl.append(ln)
    return spl


@endpoints.api(name='rrrq', version='v1', allowed_client_ids=[
endpoints.API_EXPLORER_CLIENT_ID,
JS_CLIENT_ID
],
scopes=[endpoints.EMAIL_SCOPE])
class Try(remote.Service):
	
    def get_role(self, group, message):
	#print '::', group, message
	try:
	    message.role=ndb.Key(ObjectToGroup, group.key.urlsafe(), ObjectToGroup, ndb.Key(Base, message.whom_show).urlsafe()).get().role
	except AttributeError:
	    try:
		group.role_propertys['@open']
		message.role=['@open',]
	    except KeyError:
	        raise Exception('You are not here, (permission denied)')
		        

    

    def add_users(self, message):
	#print ' +- fb  add_users create base entity In', message	
	for mail, name in zip(*split_message(message.mail, message.name)):
	    #print '!', mail, name
	    if ndb.Key(Base, mail).get() is not None:
		continue 
	    entity = Base(name=name)
	    entity.key = ndb.Key(Base, mail)
            entity.put()
	    #print ' ++ Out add_users', entity
	    if len(split_message(message.mail)) == 1:
	        return entity
	    else: #????? after for?
	        return 0

    def object_to_group(self, child_key, group_key, role, parent_group=None):
	#print ' +- fb object_to_group In ch, gk, r, pg', child_key, group_key, role, parent_group
	#, #group_key.kind() 
	key = ndb.Key(ObjectToGroup, group_key, ObjectToGroup, child_key)
	if parent_group is not None:
	    p_groups = ObjectToGroup.query(
		ObjectToGroup.child_key==child_key, ObjectToGroup.parent_group==parent_group).fetch()
	    for past in p_groups:
		#len(past_group.inout) % 2 == 1 mean current group or 0 history (no load)
	        if past_group is not None and len(past_group.inout) % 2 == 1:
		    past_group.inout.append(datetime.datetime.now()) 
		    past_group.put()  
	        #print 'Time', datetime.datetime, past.inout
	#print '333333', key.get(), group_key, child_key	  	
	if key.get() is not None:
	    raise Exception('Object alredy in group use edit')
	    pass
	else: 
	    utg = ObjectToGroup(child_key=child_key, parent_group=parent_group)
	    utg.key = key
	if utg.role is None: 
	    utg.role = [role,] 	
	elif role not in utg.role:
	    utg.role.append(role)
	utg.put()
	#print ' ++ fb Out object_to_group', utg
	return utg


    


    def fill_attr(self, stat, entity, upgrade=False, auth_mail=None, group_name=None):
	#print '_____', stat
	#print ' +- fb fill_attr. In st', stat, '\n entity', entity, '\n upg, auth, gname', upgrade, auth_mail, group_name
	 
	#data = int(data)
	#print ':::', stat
	if not upgrade:
	    for st_name, val, opt in zip(stat['st_name'], stat['value'], stat['opt']):
	   #see other GG and add w to OTG, compute to Obj.
		#print ' ------IMP44 ', st_name, opt, entity.to_dict() 
		if st_name in entity.to_dict() and not (opt == 'hist' and  len(getattr(entity, st_name)) == 0):
		    continue
		if opt == 'nero':
		    #print 'NERO', entity.mail, st_name, auth_mail
		    setattr(entity, st_name, 'answers 0')
		    setattr(entity, st_name+'__A', 0)
		    setattr(entity, st_name+'__I', 0)
		    #setattr(entity, 'w__' + st_name, 0.01)
		    #continue 
		
		elif opt == 'photo':
		    setattr(entity, st_name, None)
		elif opt == 'ranking':
		    setattr(entity, st_name, 0)
		elif opt == 'points':
		    setattr(entity, st_name, 0.0)
		elif opt == 'hist': #hist - not int
		    if auth_mail is None:	
		        setattr(entity, st_name, [time.time(), 0])
		    else:    
		    	setattr(entity, st_name, [auth_mail, str(time.time()), '0']) #!! add url, date
		elif opt == '0' or opt == 'name': #!! ??
		    if hasattr(entity, st_name):
			if getattr(entity, st_name) is None:
			    setattr(entity, st_name, val)
		    else:
		        setattr(entity, st_name, val)	
		else:
		    setattr(entity, st_name, val)
		#print '--88--', entity
		#print ' ++ (not upgrade) Out fill_attr', entity
	else:
	    #print '-->>', stat['st_name'], auth_mail
	    for st_name, val, opt in zip(stat['st_name'], stat['value'], stat['opt']):	
		#print ':  :', opt, opt == 'nero'
	        if opt == 'a':
		    #print 'NEROp', entity.mail, st_name, auth_mail
		    #role=ObjectToGroup.query(ObjectToGroup.name==auth_mail, ObjectToGroup.group_name==group_name).get().role
		    itr = getattr(entity, st_name[:-3] + '__I')
		    #print '::', #entity.key, entity.key.kind()
		    #print ndb.Key(NeroStat, str(itr), 
				#NeroStat, st_name, NeroStat, entity.key.urlsafe(), 
				#NeroStat, auth_mail).get()	
		    if ndb.Key(NeroStat, str(itr), 
				NeroStat, st_name, NeroStat, entity.key.urlsafe(), 
				NeroStat, auth_mail).get() is None:
			ans = getattr(entity, st_name[:-3])
			if 'answers' in ans:
			    ans = 'answers ' + str(int(ans[7:]) + 1)
			setattr(entity, st_name[:-3], ans)
			#print val, 'answers' in ans
		    nst = NeroStat( #entity keyid becouse OTG and BASE has same key_value 
			val=float(val))
		    nst.key=ndb.Key(NeroStat, str(itr), NeroStat, st_name, NeroStat, entity.key.urlsafe(), NeroStat, auth_mail)
		    nst.put()	
		    #print '!!!0', entity, st_name, val
		    #setattr(getattr(entity, st_name), 'aa', [1,2])
		    
		    #print '  +++ put nero', nst
		    #pass
		elif opt == 'hist':
		    if auth_mail is None:	
		        getattr(entity, st_name).extend([time.time(), val])
		    else:    
		    	getattr(entity, st_name).extend([auth_mail, time.time(), val])	
		    
		    pass
		elif opt == 'photo':
		    
		    bucket_name = app_identity.get_default_gcs_bucket_name()
		    file_content = base64.b64decode(val.split(',')[1])
		    real_path = ''
		    file_name = (val.split(';')[0])
		    real_path = os.path.join('/', bucket_name, entity.key.urlsafe(), file_name)
		    create_photo_list = False
		    try:
		        getattr(entity, "photo__list")
		    except AttributeError:
			create_photo_list = True
			setattr(entity, "photo__list", [file_name,])	
		    if file_name and file_content and (create_photo_list or file_name not in entity.photo__list):
		        with cloudstorage.open(real_path, 'w', content_type=type(file_content)) as f:
		            f.write(file_content)    
			setattr(entity, st_name, file_name)
		        if not create_photo_list:
			    entity.photo__list.append(file_name)
		elif opt == 'like': #Like it is button! Remove it!!!
			flag = False
			try:
 			    getattr(entity, st_name)[auth_mail]
			    flag = True
			except KeyError, AttributeError:
			    pass
			if flag and getattr(entity, st_name)[auth_mail] == val:
			     pass
			elif not flag or getattr(entity, st_name)[auth_mail] != val:
			    sumlike = getattr(entity, st_name)["ans__"].split('/-')	
			    if val == '0':
			        getattr(entity, st_name)["ans__"] = sumlike[0]+ '/-' +str(int(sumlike[1]) + 1)
			    if val == '1':
				getattr(entity, st_name)["ans__"] = str(int(sumlike[1]) + 1)+ '/-' +sumlike[0]	
			    getattr(entity, st_name)[auth_mail] = val	
		else:
		    #print ' --------2', entity, st_name
		    setattr(entity, st_name, val) 
		#print ' ++ (upgrade) Out fill_attr', entity 
		
		
    def put_object(self, message):
	#, , , , uname=message.name,
	#print ' +- fb put_object. In', message
	for k, gr_a, cr, g, r, c_url, g_url in zip(*split_message(message.child_object,
						message.child_gr_author,
				 		message.group_creator, 
						message.group_name, 
						message.role,
						message.child_url,
						message.group_url)):
	    if g_url is not None:
	   	group_key = ndb.Key(urlsafe=g_url)
	    else:
	        group_key = ndb.Key(Group, cr, Group, g)
	    group = group_key.get()	
	    if group_key.get() is None:
	        raise Exception('No group')
	    if gr_a is None and c_url is None:	
 	        kind = 'user'
	        child_key = ndb.Key(Base, k)			
	    elif gr_a is not None  and c_url is None:	    
		kind = 'group'
		child_key = ndb.Key(Group, gr_a, Group, k)
		#print kind, '$'
	    else:
		child_key = ndb.Key(urlsafe=c_url)	 
	    otg = self.object_to_group(
			child_key=child_key.urlsafe(), 
			group_key=group_key.urlsafe(), role=r, parent_group=group.parent_group)	
	    entity = child_key.get() #if use url entity must exist, no need kind
	    #print '######IMP22   ', entity
   	    if entity is None:
		if kind == 'user':
		    #print '!!@@@@@', uname, r	
		    mess = User(mail=k)
		    entity = self.add_users(mess) # add_user funk
		elif kind == 'group':
		    mess = GroupStat(name=k, creator_mail=gr_a)#????????
		    entity = self.create_group(mess) 
	    	    
	    #self.object_to_group(key_value=k, group_name=g, role=r, parent_group=group.parent_group)
	    self.fill_attr(group.stats, entity, group_name=group.parent_group)
	    self.fill_attr(group.stats_private, otg, group_name=group.parent_group)	    
	    #print '--pt us', group.invite, group.ask_join

	    try:
	        group.invite.pop(k, None)
	    except KeyError, AttributeError: 
		pass
	    #print '#########  IMP',entity
	    entity.put()
	    otg.rate = [time.time(), 0]
	    otg.put()  
	    try:
    		del group.ask_join[c_url]
		#group.ban.remove(str(k))
	    except KeyError, ValueError:
		pass
    		#print "!!KE ask_j", group.ask_join, k	
	    if k not in group.joined:
		group.joined.append(k)
	    group.put()
	    #print '-2-pt us', group.invite, group.ask_join
	    #print	
	    #print "__________", group.key.id(), ObjectToGroup.query(ancestor=ndb.Key(ObjectToGroup, group.key.urlsafe())).fetch()	
	    try:
	        sender_address = mess.whom_show
	        subject = "GraphOfGroups" 
		if mess.name is None:
		    mess.name = ' ' 
	        body = u"Вас пригласили в группу " + g +"\n" + mess.name
	        mail.send_mail(sender_address, k, subject, body)
	    except: # ??? what exception
		print " !! InvalidEmailError"
	    #print ' ++  Out put_object put group (-) put entity', entity, '\n put otg', otg 
    
	

    

 

    
#----------Back end Functions-------------------------------------------
    @ndb.transactional(xg=True)
    @endpoints.method(User,
Answer,
path='add_user',
http_method='PUT',
name='add_user')
    def add_user(self, message):
	self.put_object_to_group(PutObjectTo(child_object=message.mail, group_name='General parametrs', group_creator='ffbskt@gmail.com', role='user'))
	entity = ndb.Key(Base, message.mail).get()
	#print 'ADDUSER', unicode(entity.name), entity.name is None, (message.name).encode('utf-8') #unknown
	if entity.name is None or entity.name==' ':
	    entity.name = message.name
	entity.put()
	return Answer(ans = 'Sucses')

    @ndb.transactional(xg=True)
    @endpoints.method(GroupStat,
Answer,
path='create_group',
http_method='PUT',
name='create_group')
    def create_group(self, message):
	#edit group and delete_role [any role or ban, ask_join]
	user = endpoints.get_current_user()
	if user is None:
	    raise endpoints.UnauthorizedException()
	# if creator_mail is None #!! ?? How change,/ add_stat
	message.creator_mail = user.email()
	return build.create_groups(self, message)

    @endpoints.method(GroupStat,
Answer,
path='update_group',
http_method='PUT',
name='update_group')
    def update_group(self, message):
	#edit group and delete_role [any role or ban, ask_join]
	user = endpoints.get_current_user()
	if user is None:
	    raise endpoints.UnauthorizedException()
	message.creator_mail = user.email()
	return build.update(self, message)

    @ndb.transactional(xg=True)
    @endpoints.method(PutObjectTo,
Answer,
path='put_object_to_group',
http_method='PUT',
name='put_object_to_group')
    def put_object_to_group(self, message):
    	#print ':::*',message.name
	#message.group_creator
	#message.group_name
	self.put_object(message)
	return Answer()


    @endpoints.method(PutObjectTo,
Answer,
path='invite_to_group',
http_method='PUT',
name='invite_to_group')
    def invite_to_group(self, message):
	user = endpoints.get_current_user()
	if user is None:
	    raise endpoints.UnauthorizedException()
	entity = ndb.Key(Group, message.group_name).get()
	#print '$', entity.invite
	for obj, r in zip(*split_message(message.child_object, message.role)):
	    #print 'sddd'
	    #print 'sddd2', entity.invite, entity.ban, entity.joined
	    if obj not in entity.invite or obj not in entity.ban or obj not in entity.joined:
	        
	        if obj in entity.ask_join:
		    self.put_object_to_group(PutObjectTo(child_object=message.child_object,  group_name=message.group_name, role=r))
	    	else:
		    entity.invite[obj]=r
	#print '$', entity.invite
	entity.put()
	return Answer()


    @ndb.transactional(xg=True)
    @endpoints.method(PutObjectTo,
Answer,
path='ask_to_join',
http_method='PUT',
name='ask_to_join')
    def ask_to_join(self, message):
	#print '_____________', message.child_url
	user = endpoints.get_current_user()
	if user is None:
	    raise endpoints.UnauthorizedException()
	if message.child_gr_author is not None:
	    entity = ndb.Key(urlsafe=message.group_url).get()
	    child = ndb.Key(Group, user.email(), 
					Group, message.child_object).get()	 
	    message.child_url = child.key.urlsafe()
	entity = ndb.Key(urlsafe=message.group_url).get()
	
	if message.child_url is None:  #FOR TEST
	    message.child_url = ndb.Key(Base, user.email()).urlsafe()
	    child = ndb.Key(Base, user.email()).get() 
	#print '_____________', message.child_url
	date = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	entity.ask_join[message.child_url] = [child.name, str(child.rate[-1]), date]
	#print '---', entity.ask_join
	entity.put()
	sender_address = "Денис Волконский <ffbskt@gmail.com>"
	subject = "Shrink complete!"
	user_email = 'ffbskt@gmail.com'
	body = "We shrunk all the images attached to your notes!"
	#mail.send_mail(sender_address, user_email, subject, body) # remove ffbskt@gmail.com
	return Answer(ans=user.email())



    @endpoints.method(Show,
FullGroup,
path='show_group',
http_method='PUT',
name='show_group')
    def show(self, message):
	user = endpoints.get_current_user()
	if user is None:
	    raise endpoints.UnauthorizedException()
	if message.whom_show == '' or message.whom_show is None:
	    message.whom_show = user.email()
	#message.tmail_this = message.tmail
	message.tmail_this = user.email()
	if message.group_url is None: #add g_auth and multiple groups
	    e = Group.query(Group.name==message.group_name).fetch()
	    #print 'aaaaaaaaa', e, message.group_name
	    if len(e) != 1:
	  	raise Exception('Groups with this name more or less then 1')
	    message.group_url=e[0].key.urlsafe()
	#print '##############', message.url, message.whom_show
	#ADD message.frame, message.top_rateRate(url=obj.key.id(), name=obj.name, avatar=obj.avatar,
	#		   kind=obj.is_group, rating=str(getattr(obj, url)[-1]))
	#    answer.rate_obj.append(rate_bl)
	return show.show_group(self, message)

    @endpoints.method(Show,
User,
path='show_user',
http_method='PUT',  #GET
name='show_user')
    def show_user(self, message):
	user = endpoints.get_current_user()
	if user is None:
	    raise endpoints.UnauthorizedException()
	answer = User()
	message.whom_show = user.email()
	if message.url == '' or message.url is None:
	    message.url = ndb.Key(Base, user.email()).urlsafe()
	if message.tmail_this == '':
	    message.tmail_this = user.email()
	#print '______', message.url, ndb.Key(urlsafe=message.url).id()
	if ndb.Key(urlsafe=message.url).id() != user.email():
	    message.for_user = False	
	stat = show.get_stat(self, message, answer)# after test -> user.email())
	#ADD message.frame, 
	top = ndb.Key(Group, 'ffbskt@gmail.com', Group, 'General parametrs').get().top_rate
	for obj in top:
	    answer.top_rate.append(Rate(url=obj[0], name=obj[1], avatar=obj[2],
			   kind=obj[3], rating=obj[4]))	
	return answer

    @endpoints.method(Show,
AllUserGroup,
path='all_user_group',
http_method='GET',
name='all_user_group')
    def all_user_group(self, message):
	user = endpoints.get_current_user()
	if user is None:
	    raise endpoints.UnauthorizedException()
	# Test after user.email()
	if message.whom_show == '':
	    message.whom_show = user.email()
	#message.tmail_this = message.tmail
	if message.tmail_this == '':
	    message.tmail_this = user.email()
	groups = ObjectToGroup.query(ObjectToGroup.key_value==message.whom_show).fetch()
	ans = AllUserGroup()
	for group in groups:
	    ans.groups_name.append(group.group_name)	
	return ans	

    @endpoints.method(Show,
AllUserGroup,
path='all_group',
http_method='GET',
name='all_group')
    def all_group(self, message):
	user = endpoints.get_current_user()
	if user is None:
	    raise endpoints.UnauthorizedException()
	if message.tmail_this == '' or message.tmail_this == None:
	    message.tmail_this = user.email()
	#add number people and raiting
	groups = Group.query().fetch()

	ans = AllUserGroup()
	for group in groups:
	    ans.groups_name.append(group.key.id())
	    auth_key = ndb.Key(Base, group.key.parent().id())	
	    ans.group_author.append(auth_key.get().name)
	    ans.url_author.append(auth_key.urlsafe())	
	    ans.content.append(group.content)
	    ans.people.append(len(group.joined))
	    ans.url.append(group.key.urlsafe())
	    if len(group.rate) > 0: 
	    	ans.rate_group.append(str(group.rate[-1]))
	    else:
		ans.rate_group.append(str(group.rate))	
	    otg = ndb.Key(ObjectToGroup, group.key.urlsafe(), ObjectToGroup, ndb.Key(Base, user.email()).urlsafe()).get()
	    if otg is not None and '__creator' in otg.role:
	        ans.groups_created_name.append(group.key.id())	
	    u_url = ndb.Key(Base, user.email()).urlsafe()	
	    #print 'ppppppppppppppppp', group.name, group.ask_join, message.tmail_this, group.joined	
	    if (u_url in group.ask_join) or (message.tmail_this in group.joined) or (message.tmail_this in group.ban):
		#try:
	        getattr(ans, 'tryed').append(True)
		#except:
		#    setattr(ans, 'tryed', [True])
		#    print 'f', ans
	    else:
		#try:
	        getattr(ans, 'tryed').append(False)
		#except:
		#    setattr(ans, 'tryed', [False])
 		#getattr(ans, 'tryed').append(False)
	    #print '--_______________________________________________ ---------------------------------------------', group.invite, (user.email() in group.invite)
	    try:
	        if message.tmail_this in group.invite:
		    ans.invited_n.append(message.tmail_this)
		    ans.invited_r.append(group.invite[message.tmail_this])
	        else:
 		    ans.invited_n.append(' ')
		    ans.invited_r.append(' ')
	    except AttributeError: #Error ?
		ans.invited_n.append(' ')
		ans.invited_r.append(' ')
	#print ans
	return ans

#!!Edit user -> Edit Object
    @ndb.transactional(xg=True)
    @endpoints.method(User,
Answer,
path='edit_user',
http_method='POST',
name='edit_user')
    def edit_user(self, message):
	#print 'OOOOOOOOOOOOOOOOOOOOOO'
	user = endpoints.get_current_user()
	if user is None:
	        raise endpoints.UnauthorizedException()
	#if message.mail is not None and message.mail != ' ':
	#    entity = ndb.Key(Base, message.mail).get()
	#elif message.card_id != ' ' and message.card_id is not None:
	 #   entity = Base.query(Base.card_id==message.card_id).get()
	#else:
	#    entity = ndb.Key(Base, user.email()).get()
	#print '!', message
	entity = 0
	for st_block in message.stat_block:
	    if len(st_block.return_ch) == 0:
		continue
	    #Load all groups!! fix to only if change
	    stat_name = [[],[],[]]
	    [[stat_name[0].append(st_block.st_name[i]), stat_name[1].append(st_block.st_def[i]), stat_name[2].append(st_block.st_opt[i])] for i in st_block.return_ch]
	#print stat_name
	    stat = {'st_name':stat_name[0], 'value':stat_name[1], 'opt':stat_name[2]}
	    #print '~', message.key_value, st_block.group_name
	    if st_block.group_name == "General parametrs":
		entity = ndb.Key(urlsafe=message.url).get()
	    else:
		entity = ndb.Key(ObjectToGroup, st_block.group_url, ObjectToGroup, message.url).get()
		#print 'OTG entity edit', message.key_value, st_block.group_name == "General parametrs  ", st_block.group_name
	    
	    #print entity, stat, message.parent_group 
	    self.fill_attr(stat, entity, upgrade=True, group_name=message.parent_group, auth_mail=user.email())
	#print stat, entity
	    entity.put()
	return Answer(ans = 'Sucses')

    @endpoints.method(EditRole,
Answer,
path='edit_role',
http_method='PUT',
name='edit_role')
    def edit_role(self, message):
	#Don't protect by user.email
	otg = ndb.Key(ObjectToGroup, message.group, ObjectToGroup, message.user_url).get()
	if message.is_add:
	    otg.role.append(message.role)
	else:
	    otg.role.remove(message.role)
	otg.put()
	#print '#otg#', otg
      	return Answer(ans = 'Sucses')	

    @endpoints.method(Answer,
Answer,
path='TEST',
http_method='PUT',
name='TEST')
    def TEST(self, message):
	self.start(Answer())
	#test.T_Normativ(self)
	#test.T_high_perfomance(self)
	#test.tl(self)  #test for nfc, put all old users 
	test.T_group_structure(self)
	param1={'name':'Team2', 'st_name':['name', 'games', 'points', 'role'], 'st_opt':['name', '0', 'ranking', '0'], 'st_place':[2], 'st_w':[1.0], 'st_ifbase':[True,False,False,False], 'role_propertys_add':[{'name':'@open', 'change':[],'visible': ['name', 'games', 'points', 'role']}]}
	param2={'name':'Tornament', 'st_name':['name', 'games', 'vin'], 'st_opt':['name', '0', 'ranking'], 'st_place':[2], 'st_w':[1.0], 'st_ifbase':[True,False,False], 'role_propertys_add':[{'name':'@open', 'change':[],'visible': ['name', 'games', 'vin']}]}
	test.add_stat(['Team1','Team2','Team3'], 'Tornament', param2, self, athors=['ffbskt@gmail.com','ffbskt@gmail.com','ffbskt@gmail.com'])
	test.add_stat(['bpl7@','bpl8@','bpl9@'], 'Team2', param1, self)
	test.add_stat(['bpl4@','bpl5@','bpl6@', 'ffbskt@gmail.com'], 'Team1', param1, self)
	return Answer()

    @endpoints.method(Answer,
Answer,
path='Clear',
http_method='PUT',
name='Clear')
    def Clear(self, message):
	#print "--Clear remove all"
	test.T_remove_all(self, message)
	return Answer()

    @endpoints.method(CopyGroup,
Answer,
path='copy_template',
http_method='PUT',
name='copy_template')
    def copy_template(self, message):
	#print ' -+ \nfb copy_template In', message
	user = endpoints.get_current_user()
	if user is None:
	    raise endpoints.UnauthorizedException()
	if message.old_author == user.email() and message.new_name == message.old_name:
	    raise Exception('Key same. Your remove old_group')
	#Take old name and author and copy only stats and role_prop
	#!! Add group_url or gname
	if message.old_url is None:	
	    old_entity = ndb.Key(Group, message.old_author, Group, message.old_name).get()
	else:
	    old_entity = ndb.Key(urlsafe=message.old_url).get()	
	new_entity = Group()#parent=ndb.Key(Group, message.new_name))
	new_entity.key=ndb.Key(Group, user.email(), Group, message.new_name)
	new_entity.content = message.content
	#new_entity. free is_open, avatar, 
	#new_entity.key_value = message.new_name
	#print '@', (old_entity.to_dict()[role_propertys])
	new_entity.role_propertys = old_entity.role_propertys
	new_entity.stats = old_entity.stats
	new_entity.stats_private = old_entity.stats_private
	new_entity.st_w = old_entity.st_w
	new_entity.st_place = old_entity.st_place
	new_entity.name = message.new_name
	#new_entity.name = message.new_name
	#if message.parent_group is None:
	#    message.parent_group = message.new_name
	new_entity.parent_group = message.parent_group 
	new_entity.put()
	self.put_object_to_group(PutObjectTo(child_object=user.email(), group_name=message.new_name, group_creator=user.email(), role='__creator'))
	self.put_object_to_group(PutObjectTo(child_object=message.new_name,  child_gr_author=user.email(), group_name='General parametrs', group_creator='ffbskt@gmail.com', role='group'))
	#print ' ++ Out', new_entity
	return Answer(ans = 'Sucses')

    @endpoints.method(Answer,
TemplateList,
path='load_template',
http_method='GET',
name='load_template')
    def load_template(self, message):
	groups = Group.query().fetch()
	templates = TemplateList() 
	for group in groups:
	    
	    creator = ndb.Key(Base, group.key.parent().id()).get().name
	    templates.group_name.append(group.key.id() + '(' + creator + ')')	
	    #templates.auth_name.append(creator)
	    templates.group_url.append(group.key.urlsafe())
	#print templates
        return templates	

    @endpoints.method(EditEntityAttr,
Answer,
path='edit_entity_value',
http_method='PUT',
name='edit_entity_value')
    def edit_entity_value(self, message):
	user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
	#print user.nickname()
	sender_address = 'ffbskt@gmail.com'
	subject = "GraphOfGroups"
	body = u"Вас пригласили в группу "
	mail.send_mail(sender_address, 'ffbskt@gmail.com', subject, body)
	#To show attribute input value=None
	if message.child_object is not None and message.group_url is not None:
	    entity = ndb.Key(ObjectToGroup, message.group_url, ObjectToGroup, message.child_object).get()
	elif message.child_object is not None:
	    entity = ndb.Key(urlsafe=message.child_object).get()
	elif message.group_url is not None:
	    entity = ndb.Key(urlsafe=message.group_url).get()
	#print str(getattr(entity, message.attribute_name))
	if message.value is None:
	    return Answer(ans=str(getattr(entity, message.attribute_name)))
	setattr(entity, message.attribute_name, message.value)
	entity.put()
	return Answer(ans=str(getattr(entity, message.attribute_name)))

    @endpoints.method(CardId,
Answer,
path='use_card',
http_method='GET',
name='use_card')
    def use_card(self, message):
	#Change card_id if has child_object, add+1 only to list
	admin = endpoints.get_current_user()
	if admin is None:
	        raise endpoints.UnauthorizedException() 
	if message.group_url is None:
	    message.group_url = ndb.Key(Group, message.group_auth, 
					Group, message.group_name).urlsafe()
	    #print dir(Base.query(Base.card_id==message.card_id))		
	user = Base.query(Base.card_id==message.card_id).get()
	if user is None and not (message.child_object is None or message.child_object == u''):
	    user = ndb.Key(Base, message.child_object).get()
	    if user is None:
		return Answer(ans='Error this email not registered')
	    if user.id_open or admin.email() == 'ffbskt@gmail.com': #remove when build openid  
	        user.card_id = message.card_id
		user.id_open = False
	        user.put()
	        return Answer(ans='add card')
	    return Answer(ans='Error user_id is closed')	
	elif user is None:
		return Answer(ans='Error card_id')	
	ukey = user.key.urlsafe()	
	entity = ndb.Key(ObjectToGroup, message.group_url,
			ObjectToGroup, ukey).get()
	if entity is None:
	    return Answer(ans='Error user is not in this group (add user)')	
	    #print '--ent', entity
	data=time.time()
	delay = data - float(getattr(entity, message.stat_pls)[-2]) 
	#print 'qqqqqq', getattr(entity, message.stat_pls)	
	if delay < 1000 and len(getattr(entity, message.stat_pls)) > 3:
	    return Answer(ans='Already been'+str(delay))
	val = getattr(entity, message.stat_pls)[-1]
	    #print val
	    
	getattr(entity, message.stat_pls).extend([admin, str(data), int(val) + 1])
	#getattr(entity, message.stat_pls).append(int(val) + 1)    
	
	#print '#####', message, message.child_object == u''

	    #val = "Ok param" + 'gps='+message.gps + 'mail='+user.email() + 'card='+message.card_id +'group='+ message.group_url + 'fild='+message.stat_name + entity.name
	entity.put()
	#print type(val), type(user.name), type(str(data))
  	return Answer(ans=unicode(str(val) + '  ' + user.name + ' time ' + str(data)))

    @endpoints.method(CompNero,
Answer,
path='compute_nero',
http_method='PUT',
name='compute_nero')
    def compute_nero(self, message):
	user = endpoints.get_current_user()
	if user is None:
	        raise endpoints.UnauthorizedException()
        #role=ObjectToGroup.query(ObjectToGroup.key_value==user.email(), ObjectToGroup.group_name==message.group_name).get().role
# itr??
	entity = ndb.Key(ObjectToGroup, message.valued_object, ObjectToGroup, message.group_name).get()
	#print entity
	itr = getattr(entity, message.st_name+'__I')
  	evs = NeroStat.query(ancestor=ndb.Key(NeroStat, str(itr), 
				NeroStat, message.st_name+'__A', NeroStat, entity.key.urlsafe())).fetch()
	#print " 1", evs
	#T = message.val
	w = []
	A = []
	mult = []
	Q = {}
	ref_profile = []
	for ref in evs:
	    #print ref.key, ref.key.id(),w
	    ref_profile.append(ndb.Key(ObjectToGroup, ref.key.id(), ObjectToGroup, message.group_name).get())
	    A.append(ref.val)
	    w.append(getattr(ref_profile[-1], message.st_name+'__W'))
	    #print getattr(ref_profile[-1], message.st_name+'__W')
	#print '----', A, w, message.teacher_val
	data = compute_nero(A, w, message.teacher_val)
	for i, users in enumerate(ref_profile):
	    setattr(users, message.st_name+'__W', data[2][i])
	    #print '==', users, data[2]
	    users.put()
	setattr(entity, message.st_name, '(T:'+str(message.teacher_val)+' m:'+str(data[1])+')') 
	entity.put() 	
	return Answer()

    @endpoints.method(ShowPict,
ShowPict,
path='show_picture',
http_method='GET',
name='show_picture')
    def show_picture(self, message):
	
	bucket_name = app_identity.get_default_gcs_bucket_name()
	#print '&&&&&&&', bucket_name, message.obj_url, message.pname
	real_path = os.path.join('/', bucket_name, message.obj_url,
message.pname)
	ans = ShowPict()
	#try:
 	with cloudstorage.open(real_path, 'r') as f:
	    ans.picture = f.read()
  	        #self.response.headers.add_header('Content-Type', content_t)
	#except:
	#    print '# # EXCEPT'
	#print '# #', ans.picture[:100], message.obj_url, message.pname
	return ans

    @endpoints.method(EditEntityAttr,
Answer,
path='add_chat',
http_method='PUT',
name='add_chat')
    def add_chat(self, message):
	user = endpoints.get_current_user()
	if user is None:
	        raise endpoints.UnauthorizedException()
        group = ndb.Key(urlsafe=message.group_url).get()
	name = ndb.Key(Base, user.email()).get().name
	data = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	if group.chat is None:
	    group.chat = ''
	group.chat = name + ' \''+ data +'\': ' + message.value + '\n' + group.chat
	group.put()
	return Answer()

    @endpoints.method(Answer,
Answer,
path='start',
http_method='PUT',
name='start')
    def start(self, message):
	#print "--fe start, !clear all. If user ffbskt create_group General parametrs with st('name', 'content', 'avatar', 'rate') all base and put_object_to_group(ffbskt as admin)" 
	user = endpoints.get_current_user()
	#Option public Test for role admin
	if user is None:
	        raise endpoints.UnauthorizedException()
	if user.email() == 'ffbskt@gmail.com':
	    test.start(self)
 	return Answer()

    @endpoints.method(Show,
Answer,
path='compute_rate',
http_method='PUT',
name='compute_rate')
    #To Base!!!, Otg, where save rate Renue full for b or p!
    def compute_rate(self, message):
	if message.group_url is None:
	    message.group_url = ndb.Key(Group, message.group_author, Group, message.group_name).urlsafe()
	return compute_rating(self, message.group_url)

    @endpoints.method(Show,
Answer,
path='compute_top',
http_method='PUT',
name='compute_top')
    #To Base!!!, Otg, where save rate Renue full for b or p!
    def compute_top(self, message):
	if message.group_url is None:
	    message.group_url = ndb.Key(Group, message.group_author, Group, message.group_name).urlsafe()
	compute_top_raiting(self, child=message.group_url, begin=message.group_url)
	out_put_rating.out_put_rating(self)
        return Answer()	


#timer
    @ndb.transactional	
    @endpoints.method(Timer,
Answer,
path='timer',
http_method='PUT',  #GET
name='timer')
    def timer(self, message):
	# Structure
	#entity.key.id() "who made change": entity.history == {url "which obj change": [[time, action, st, val] ] } - what change
	entity = 0
	#print '+++++++++++^^^^^', message
	user = endpoints.get_current_user()
	if user is None:
	    entity = ndb.Key(Base, '@unknown').get()
	else:
	    entity = ndb.Key(Base, user.email()).get()
	if message.url in entity.history:
	    entity.history[message.url].append([message.time_in, message.time_out, message.action,
						 message.obj, message.val])
	else:
	    entity.history[message.url] = [[message.time_in, message.time_out, message.action,
						 message.obj, message.val], ]
	entity.put()
	#print '^^^^^', entity.history, entity.key.id()
        return Answer()	



app = endpoints.api_server([Try])
