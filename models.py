from google.appengine.ext import ndb
from google.appengine.ext.ndb.polymodel import PolyModel
from protorpc import messages
from protorpc import message_types
import json
import time

class Base(ndb.Expando):
    #name = ndb.StringProperty()#, required=True)
#Code history /stat_name/:[[value, time, admin],[]] \|/	
    history = ndb.JsonProperty(default={}) 
    #role = ndb.JsonProperty()
    #mail = ndb.StringProperty() #its key.id()
    #key_value = ndb.StringProperty(indexed=True) #key
    card_id = ndb.StringProperty(indexed=True)
    id_open = ndb.BooleanProperty(default=True)		
    creator = ndb.StringProperty()  
    #lesson_in = ndb.IntegerProperty(default=0)
    #lesson_remain = ndb.IntegerProperty(default=0)
    #content = ndb.StringProperty()	    
    invite = ndb.StringProperty()
    photo__list = ndb.StringProperty(repeated=True) #check name to prevent collision
    rate = ndb.FloatProperty(repeated=True)
    frame = ndb.StringProperty(repeated=True)	
class Group(ndb.Expando):
    name = ndb.StringProperty(indexed=True, required=True)#
    content = ndb.StringProperty()
    parent_group = ndb.StringProperty()  #user could be only at one of this group
    #if parent_group == parent group admin... could same capabilities	
    #key_value = ndb.StringProperty(indexed=True) #Key prop	
    history = ndb.JsonProperty() 
    role = ndb.JsonProperty()
    #mail = ndb.StringProperty()
    in_group = ndb.IntegerProperty(default=0)
    #creator_mail = ndb.StringProperty() #?? if it in key == ancestore
    #is_open = ndb.BooleanProperty(default=False)
    #invite = ndb.StringProperty()
    photo_list = ndb.StringProperty(repeated=True)	
#{val[], def[], kind - json, opt}
    stats = ndb.JsonProperty(default={'st_name':[], 'value':[], 'opt':[]})
    stats_private = ndb.JsonProperty(default={'st_name':[], 'value':[], 'opt':[]}) #only in this group access	
    # only for private, rate
    st_w = ndb.JsonProperty(default=[]) #Summarise rankings
    st_place = ndb.JsonProperty() #different options for compute poits 
 				  #0 - current, 1/2 - foward/backward sort + 1/x
    role_propertys = ndb.JsonProperty(default = {
		"admin":{"change":[],
			"visible":[]},
		"user":{"change":["@name"], #Only own
		    	"visible":[]},
		"__creator":{"change":['@invite'],
			   "visible":[]},
		"__id":{"change":['@invite'],
			   "visible":[]}
		 })
    ask_join = ndb.JsonProperty(default={}) #url:[mail,role,mess]
    joined = ndb.JsonProperty(default=[]) #url
    ban = ndb.JsonProperty(default=[]) #mail
    invite = ndb.JsonProperty(default={}) #mail	
    chat = ndb.TextProperty()
    rate = ndb.FloatProperty(repeated=True)
    top_rate = ndb.JsonProperty(default=[]) #top 3 obj down this group [[avt, n, rate, url, kind], [],[]]	
    frame = ndb.StringProperty(repeated=True) # history mark if obj in top3	
    free = ndb.BooleanProperty(default=False) #anybody can add to group	 
    public_view = ndb.BooleanProperty(default=False) #avary body could see ??add @open_view
    #passing_top = {}#{deep_level:[[url,kind,rate,name],[2],[3]]} 
    #current_top =		

class ObjectToGroup(ndb.Expando):
    parent_group = ndb.StringProperty(indexed=True) #
    #group_key = ndb.StringProperty(required=True)#group_name == OTG.key.parent().id() 
    child_key = ndb.StringProperty(indexed=True, required=True) #key_value 
    role = ndb.JsonProperty()
    rate = ndb.FloatProperty(repeated=True)
    inout = ndb.DateProperty(repeated=True) #if user out of group len%2 = 0 

class NeroStat(ndb.Expando):
    data = ndb.DateTimeProperty(auto_now=True)
    val = ndb.FloatProperty()
    role = ndb.StringProperty()
    group = ndb.StringProperty()

class ObjectRating(ndb.Expando):
    name=ndb.StringProperty()
    avatar = ndb.StringProperty() 
    is_group = ndb.BooleanProperty()
    #@classmethod
    #def query_book(cls, url):
    #    return cls.query().order(-cls.url)		  	
    pass
    #rate = ndb.FloatProperty(repeated=True)
#-------------- Message classes----------------------------------------


class Role(messages.Message):
    name = messages.StringField(1)
    change = messages.StringField(2, repeated=True)
    visible = messages.StringField(3, repeated=True)

class StatBlock(messages.Message):
    st_name = messages.StringField(1, repeated=True)
    st_def = messages.StringField(2, repeated=True)
    st_opt = messages.StringField(3, repeated=True)
    st_ch = messages.BooleanField(4, repeated=True)
    return_ch = messages.IntegerField(5, repeated=True) #if stat change
    group_name = messages.StringField(6)
    group_rate = messages.StringField(7)
    group_url = messages.StringField(8) #??? for why???
    new_message = messages.BooleanField(9) #need to do
    group_role = messages.StringField(10) #each role have own stat
    obj_url = messages.StringField(11) 
    obj_kind = messages.StringField(12)  

class Rate(messages.Message):
    url = messages.StringField(1)
    name = messages.StringField(2)
    avatar = messages.StringField(3)
    kind = messages.BooleanField(4)
    rating = messages.StringField(5)

class User(messages.Message):
    name = messages.StringField(1, default=' ')
    card_id = messages.StringField(2, default=' ')
    lesson_in = messages.IntegerField(3, default=0)
    lesson_remain = messages.IntegerField(4, default=0)
    mail = messages.StringField(5, default=' ') #Remove?
    role = messages.StringField(6, default='user')    
    role_delete = messages.StringField(7, repeated=True)
    role_propertys_add = messages.MessageField(Role, 8) #?? for group only
    if_change = messages.BooleanField(9, default=False)
    url = messages.StringField(10)
    parent_group = messages.StringField(11)    
    stat_block = messages.MessageField(StatBlock, 12, repeated=True)
    top_rate = messages.MessageField(Rate, 13, repeated=True)
    frame = messages.StringField(14, repeated=True)		
    #groups_name = messages.StringField(16, repeated=True)

class EditRole(messages.Message):
    is_add = messages.BooleanField(1)
    user_url = messages.StringField(2)
    group = messages.StringField(3)
    role = messages.StringField(4)	

class GroupStat(messages.Message):
    name = messages.StringField(1) 
    #admin = messages.StringField(2)
    content = messages.StringField(3) 	
    #users = messages.StringField(3)
    short = messages.StringField(4)
    st_name = messages.StringField(5, repeated=True)
    st_def = messages.StringField(6, repeated=True)
    st_opt = messages.StringField(7, repeated=True)
    st_ch = messages.BooleanField(8, repeated=True)	
    st_ifbase = messages.BooleanField(9, repeated=True) #1-base 0-privat
    st_place = messages.IntegerField(10, repeated=True)
    st_w = messages.FloatField(11, repeated=True)			
    role_delete = messages.StringField(12, repeated=True)
    role_propertys_add = messages.MessageField(Role, 13, repeated=True)
    creator_mail = messages.StringField(14)
    parent_group = messages.StringField(15)
    is_open = messages.BooleanField(16) #Open group to join
    return_ch = messages.IntegerField(17, repeated=True) #mark edited stat in group
    free = messages.BooleanField(18)
    public_view = messages.StringField(19)

class Show(messages.Message):
    url = messages.StringField(1)
    group_url = messages.StringField(2) 		
    parent_group = messages.StringField(3)	
    whom_show = messages.StringField(4) #Test whom show	, look at entity
    tmail_this = messages.StringField(5)#Test which person show 
    role = messages.StringField(6, repeated=True)
    user_name = messages.StringField(7)	
    group_name = messages.StringField(8)
    group_author = messages.StringField(9)
    for_user = messages.BooleanField(10, default=True)		

class AllUserGroup(messages.Message):
    groups_name = messages.StringField(1, repeated=True)
    content = messages.StringField(2, repeated=True)  
    people = messages.IntegerField(3, repeated=True)
    tryed = messages.BooleanField(4, repeated=True)
    invited_n = messages.StringField(5, repeated=True)
    invited_r = messages.StringField(6, repeated=True)
    url = messages.StringField(7, repeated=True)
    group_author = messages.StringField(8, repeated=True)
    url_author = messages.StringField(9, repeated=True)	
    rate_group = messages.StringField(10, repeated=True)
    groups_created_name = messages.StringField(11, repeated=True)				
    # tryedd = messages.BooleanField(7, repeated=True) #

class ToJoine(messages.Message):
    url = messages.StringField(1)
    name = messages.StringField(2) 		
    rate = messages.StringField(3)
    time = messages.StringField(4)
    role = messages.StringField(5)
    kind = messages.StringField(6)	
class FullGroup(messages.Message):
    name = messages.StringField(1)
    other_group_stat = messages.StringField(2, repeated=True)
    user_group_stat = messages.MessageField(User, 3, repeated=True)
    ask_join = messages.MessageField(ToJoine, 4, repeated=True) #name role email_message
    secret_mail = messages.StringField(5, repeated=True)
    user_role = messages.StringField(6, repeated=True)	
    chat = messages.StringField(7)
    url = messages.StringField(8)
    roles = messages.StringField(9, repeated=True)		
    creator = messages.BooleanField(10, default=False)
    add_id = messages.BooleanField(11, default=False)
    top_rate = messages.MessageField(Rate, 13, repeated=True)
    frame = messages.StringField(14, repeated=True) #history 
    joined = messages.StringField(15, repeated=True) #urls		

class PutObjectTo(messages.Message):
    child_object = messages.StringField(1) #mail or group name
    child_gr_author = messages.StringField(2)
    parent_group = messages.StringField(3)#???
    role = messages.StringField(4, default='user')
    name = messages.StringField(5)
    rate = messages.StringField(6)
    group_name = messages.StringField(7)
    group_creator = messages.StringField(8)
    group_url = messages.StringField(9)		
    child_url = messages.StringField(10)
    #!! invitor = messages.StringField(9) who add to group 	
    #sender_mail = messages.StringField(5) 
    #kind = messages.StringField(6, default='user') #-private, group/user# remove???
    	
    #separate = messages.BooleanFild(9, default='True')

class Answer(messages.Message):
    ans = messages.StringField(1)

class CopyGroup(messages.Message):
    old_name = messages.StringField(1)
    new_name = messages.StringField(2)
    parent_group = messages.StringField(3)
    content = messages.StringField(4) #free avatar... 
    old_author = messages.StringField(5)
    old_url = messages.StringField(6)
    		

class TemplateList(messages.Message):
    group_name = messages.StringField(1, repeated=True)
    auth_name = messages.StringField(2, repeated=True)	
    group_url = messages.StringField(3, repeated=True)

class EditEntityAttr(messages.Message):
    child_object = messages.StringField(1)
    group_url = messages.StringField(2)
    value = messages.StringField(3)
    attribute_name = messages.StringField(4)

class CardId(messages.Message):
    child_object = messages.StringField(1) #lower case!!
    card_id = messages.StringField(2)
    stat_pls = messages.StringField(3)
    group_url = messages.StringField(4)
    group_name = messages.StringField(5)
    group_auth = messages.StringField(6)
    #stat_name = messages.StringField(7)
    #gps = messages.StringField(8)			

class CompNero(messages.Message):
    valued_object = messages.StringField(1)
    st_name = messages.StringField(2)
    group_url = messages.StringField(3)
    teacher_val = messages.FloatField(4)

#class CompLike(messages.Message):
#    valued_object = messages.StringField(1)
#    st_name = messages.StringField(2)
#    group_name = messages.StringField(3)
#    like = messages.BoolField(4)


class ShowPict(messages.Message):
    picture = messages.BytesField(1)
    pname = messages.StringField(2)
    obj_url = messages.StringField(3) 

class Timer(messages.Message):
    url = messages.StringField(1)
    time_in = messages.StringField(2)
    time_out = messages.StringField(3) 
    action = messages.StringField(4, repeated=True) #st_name + @
    obj = messages.StringField(5, repeated=True)
    val = messages.StringField(6, repeated=True)

class RequestRate(messages.Message):#delete
    urls = messages.StringField(1, repeated=True)
 
    
class AnswerRate(messages.Message):#delete
    rate_obj = messages.MessageField(Rate, 1, repeated=True)
    group_names = messages.StringField(2, repeated=True)



	
