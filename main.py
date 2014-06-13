# This is actually the development one.
# lutherrideshare.appspot key: ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixS0LiYWImofzW4gd3oCqtkHKt0IaBT-STdq-gdH-mW2_ejMPXqxnfJjgw

# This has the app id of ridesharebeta   and is also on ridesharebeta.appspot.com
# rideshare.luther.edu key:  ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixQ2JlMNfqnGb2qqWZtmZLchh1TSjRS0zuchuhlR8g4tlMGrjg34sNmyjQ
#!/usr/bin/env python2.7

import webapp2
from simpleauth import SimpleAuthHandler
from app.base_handler import BaseHandler

# testing
from app.controllers.test_account import create_user
# end testing

from app.secrets import SESSION_KEY

from app.model import *

app_config = {
    'webapp2_extras.sessions': {
        'cookie_name': '_simpleauth_sess',
        'secret_key': SESSION_KEY
    },
    'webapp2_extras.auth': {
        'user_attributes': []
    }
}

import wsgiref.handlers
import datetime
from datetime import date
from google.appengine.api import mail

import jinja2
from google.appengine.ext import db

from app.pygeocoder import Geocoder

import logging
import urllib
import random
import os.path

from app.controllers.account_flow import *
from app.controllers.circles import *
from app.controllers.events import *
from app.controllers.rides import *
from app.controllers.comments import *
from app.controllers.users import *

from app.common.toolbox import doRender

## Testing Code
aquery = db.Query(Community)
if aquery.count() == 0:
    #development site
    community = Community(
        name = "Luther College",
        address = "700 College Drive Decorah,IA",
        lat = 43.313059,
        lng = -91.799501,
    )
    community.put()
## Testing Code End
 

class MainHandler(BaseHandler):
  def get(self):
    self.auth()
    user = self.current_user()
    aquery = db.Query(Community)
    community = aquery.get()

    circles_all = Circle.all()
    circles_user = Circle.all().filter('__key__ IN', user.circles)

    doRender(self, 'main.html', {
        'circles_user': circles_user,
        'circles_all': circles_all,
        'community': community,
        'user': user
    })
    
class MapHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()
        doRender(self, 'index_rework.html', {
            'user': user
        })

class HomeHandler(BaseHandler):
    def get(self):
        self.auth()
        aquery = db.Query(Community)
        community = aquery.get()
        user = self.current_user()

        doRender(self, 'home.html', { 
            'user': user
        })

class ConnectPageHandler(BaseHandler):
    def get(self):
        user = self.current_user
        userID = user.id
        doRender(self, 'connectride.html',{
            'drivernum': userID
        })

class IncorrectHandler(BaseHandler):
    def get(self):
        doRender(self, 'error.html', {
            'error_message': "Page does not exist."
        })

class HelpHandler(BaseHandler):
    def get(self):
        user = self.current_user()

        doRender(self, 'help.html', {
            'user': user
        })

class DetailHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        doRender(self, 'details.html', {
            'user': user
        })
    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        self.auth()
        user = self.current_user()

        user.email = data['email']
        user.phone = data['phone']

        user.put()

        resp = {
            'message': 'Information updated'
        }

        self.response.write(json.dumps(resp))

app = webapp2.WSGIApplication([
    ('/', LoginPageHandler),
    ('/map', MapHandler),
    ('/main', MainHandler),

    # controllers/rides.py
    ('/rides', RideHandler),
    ('/ride/(\d+)', GetRideHandler),
    ('/join_ride', RideJoinHandler),
    ('/getrides', RideQueryHandler),
    ("/newride.*", NewRideHandler),
    ("/addpass", AddPassengerHandler),
    ("/adddriver",AddDriverHandler),
    ('/home', HomeHandler),
    ('/rideinfo', RideInfoHandler),
    ('/deleteride', DeleteRideHandler),
    ('/editride', EditRideHandler),
    # end rides

    # controllers/users.py
    ('/user/(\d+)', GetUserHandler),
    ('/user', UserHandler),
    # end users

    ('/signout', SignOutHandler),
    ('/comment', CommentHandler),
    ('/comments', FetchComments),

    # controllers/circles.py
    ('/circle/(\d+)', GetCircleHandler),
    ('/addCircle', AddCircleHandler),
    ('/newCircle',NewCircleHandler),
    ('/circles', CircleHandler),
    ('/join_circle', JoinCircle),
    # end circles

    # controllers/events.py
    ('/event/(\d+)', GetEventHandler),
    ('/events', EventHandler),
    ('/newevent', NewEventHandler),
    ('/getevents', EventQueryHandler),
    ('/neweventride', NewEventRideHandler),
    ('/addevents', AddEventsHandler),
    # end events

    # auth routes
    webapp2.Route(
        '/auth/<provider>',
        handler='app.auth_handler.AuthHandler:_simple_auth',
        name='auth_login'
    ),
    webapp2.Route(
        '/auth/<provider>/callback', 
        handler='app.auth_handler.AuthHandler:_auth_callback',
        name='auth_callback'
    ),
    webapp2.Route(
        '/logout',
        handler='app.auth_handler.AuthHandler:logout',
        name='logout'
    ),
    ('/details', DetailHandler),
    # end auth routes
    ('/testing', create_user),
    ('/help', HelpHandler),
    ('/.*', IncorrectHandler)
    ],
    config = app_config,
    debug = True)

# This is actually the development one.
# lutherrideshare.appspot key: ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixS0LiYWImofzW4gd3oCqtkHKt0IaBT-STdq-gdH-mW2_ejMPXqxnfJjgw

# This has the app id of ridesharebeta   and is also on ridesharebeta.appspot.com
# rideshare.luther.edu key:  ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixQ2JlMNfqnGb2qqWZtmZLchh1TSjRS0zuchuhlR8g4tlMGrjg34sNmyjQ