#!/usr/bin/env python
import os, glob, os.path, codecs, logging, cgi, urllib, urllib2
from datetime import datetime

import webapp2


import base64
import Cookie
import email.utils
import hashlib
import hmac
import time
import wsgiref.handlers
import facebook

from app.base_handler import BaseHandler

from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from google.appengine.ext.db import Key
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from myutil import *
#from model import Recipe, FBUser
#from recipe_dissect import ParsedRecipe
#
from google.appengine.ext.webapp import util

userId= None
logging.getLogger().setLevel(logging.DEBUG)

  
def get_current_user():
    return User()




def parse_cookie(value):
    """Parses and verifies a cookie value from set_cookie"""
    if not value: return None
    parts = value.split("|")
    if len(parts) != 3: return None
    if cookie_signature(parts[0], parts[1]) != parts[2]:
        logging.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 30 * 86400:
        logging.warning("Expired cookie %r", value)
        return None
    try:
        return base64.b64decode(parts[0]).strip()
    except:
        return None


def cookie_signature(*parts):
    """Generates a cookie signature.

    We use the Facebook app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(FACEBOOK_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts: hash.update(part)
    return hash.hexdigest()


def set_cookie(response, name, value, domain=None, path="/", expires=None):
    """Generates and signs a cookie for the give name/value"""
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(value, timestamp)
    cookie = Cookie.BaseCookie()
    cookie[name] = "|".join([value, timestamp, signature])
    cookie[name]["path"] = path
    if domain: cookie[name]["domain"] = domain
    if expires:
        cookie[name]["expires"] = email.utils.formatdate(
            expires, localtime=False, usegmt=True)
    response.headers.add("Set-Cookie", cookie.output()[12:])




class LoginHandler(BaseHandler):
    def get(self):
        self.login()
    def post(self):
        self.login()
    def login(self):

        token = self.request.get('token')
        if len(token)>1: #check to see if this is the second time this function has been called during this login.
            logging.debug(token)
            url = 'https://rpxnow.com/api/v2/auth_info'
            args = {
                'format': 'json',
                'apiKey': '34c757714707e1132d12375b1cfd30706758d2a8',
                'token': token
            }
            r = urllib2.urlopen(url=url,
                           data=urllib.urlencode(args)
                           )
            profile = json.load(r)['profile']
            logging.debug(profile)
            provider = profile['providerName']
        else:
            provider ="Facebook"

        if provider =="Google":
            user = FBUser.get_by_key_name(profile["googleUserId"])
            if not user:
               logging.debug("User not found:  id = " + str(profile["googleUserId"]))
               user = FBUser(key_name=str(profile["googleUserId"]), id=str(profile["googleUserId"]),
                          name=profile['displayName'], access_token=" ",
                          profile_url=profile["url"],email=profile['email'],public_link=profile["googleUserId"],loginType="google")
               user.put()
            else:
               user.access_token=" "
               user.put()

            set_cookie(self.response, "fb_user", str(profile["googleUserId"]),
                   expires=time.time() + 30 * 86400)
            self.redirect("/main")
        else:

            verification_code = self.request.get("code")
            nexthop = self.request.get('lasthop')
            args = dict(client_id=FACEBOOK_APP_ID, redirect_uri=self.request.path_url)
            logging.debug(verification_code)
            if self.request.get("code"):
                logging.debug("SAY WHAAAAAT")
                args["client_secret"] = FACEBOOK_APP_SECRET
                args["code"] = self.request.get("code")
                response = cgi.parse_qs(urllib2.urlopen(
                    "https://graph.facebook.com/oauth/access_token?" +
                    urllib.urlencode(args)).read())
                access_token = response["access_token"][-1]
       

                # Download the user profile and cache a local instance of the
                # basic profile info
                profile = json.load(urllib2.urlopen(
                    "https://graph.facebook.com/me?" +
                    urllib.urlencode(dict(access_token=access_token))))
                logging.debug(profile.keys())

                user = FBUser.get_by_key_name(profile["id"])
                if not user:
                   logging.debug("User not found:  id = " + str(profile["id"]))
                   user = FBUser(key_name=str(profile["id"]), id=str(profile["id"]),
                              name=profile["name"], access_token=access_token,
                              profile_url=profile["link"],public_link=profile["id"],loginType="facebook")
                   user.put()
                else:
                   user.access_token=access_token
                   user.put()

                set_cookie(self.response, "fb_user", str(profile["id"]),
                       expires=time.time() + 30 * 86400)
                logging.debug("SAY WHAAAAAT")
                self.redirect("/main")
            else:
                args["scope"] = "publish_stream,email,offline_access,manage_pages"
                self.redirect(
                    "https://graph.facebook.com/oauth/authorize?" +
                    urllib.urlencode(args))


class LogoutHandler(BaseHandler):
    def get(self):
        set_cookie(self.response, "fb_user", "", expires=time.time() - 86400)
        self.redirect("/signout")

