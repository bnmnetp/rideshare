from app.common.toolbox import doRender
from django.utils import simplejson
from google.appengine.ext import db
from app.model import *
import os.path
from app.base_handler import BaseHandler
import webapp2

class LoginPageHandler(BaseHandler):
    def get(self):
        print self.session
        aquery = db.Query(Community)
        community = aquery.get()
        user = self.current_user
        if user:
            self.redirect("/main")
        else:
            doRender(self, 'loginPage.html', {
              'community': community
            })

class SignOutHandler(BaseHandler):
    def get(self):
      aquery = db.Query(College)
      mycollege = aquery.get()
      doRender(self, 'logout.html', {'logout_message': "Thanks for using the "+ mycollege.name + " Rideshare Website!", "college": mycollege})