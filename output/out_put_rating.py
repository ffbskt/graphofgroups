# -*- coding: utf-8 -*-
import endpoints
from google.appengine.api import users
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import ndb
from google.appengine.api import mail
import json
from models import *
from extra_library import *
#from google.appengine.ext.ndb import msgprop
#from add_funk import make_dict_from_stat
import time
import logging
import sys
from google.appengine.api import memcache
import re
from random import randint

def out_put_rating(self, group_urls=[]):
    print group_urls, 'uu'
    for url in group_urls:
	print ObjectRating.query().order(group_urls)		
    print '111', group_urls
    return AnswerRate(group_names=group_urls)
