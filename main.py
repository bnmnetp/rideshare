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

import app.secrets as secrets

from app.model import *

app_config = {
    'webapp2_extras.sessions': {
        'cookie_name': '_simpleauth_sess',
        'secret_key': secrets.SESSION_KEY
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

from app.controllers.circles import *
from app.controllers.events import *
from app.controllers.rides import *
from app.controllers.comments import *
from app.controllers.users import *

from app.common.toolbox import doRender

# Creates Community entry on first run.
aquery = db.Query(Community)
if aquery.count() == 0:
    #development site
    community = Community(
        name = secrets.community['name'],
        address = secrets.community['address'],
        lat = secrets.community['lat'],
        lng = secrets.community['lng']
    )
    community.put()
    
class MapHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()
        circle_id = self.request.get('circle')
        if circle_id:
            circle = Circle.get_by_id(int(circle_id))
        else:
            circle = None
        doRender(self, 'index_rework.html', {
            'user': user,
            'circle': circle
        })

class LoginHandler(BaseHandler):
    def get(self):
        doRender(self, 'loginPage.html', {})

class HomeHandler(BaseHandler):
    def get(self):
        self.auth()
        aquery = db.Query(Community)
        community = aquery.get()
        user = self.current_user()

        notis = Notification.all().filter('user = ', user.key()).fetch(10)

        today = datetime.date.today()
        upcoming = Ride.all().filter('date > ', today).fetch(20)

        for up in upcoming:
            if user.key() in up.passengers:
                up.is_pass = True
            else:
                up.is_pass = False
            if user.key() == up.driver.key():
                up.is_driver = True
            else:
                up.is_driver = False

        doRender(self, 'home.html', { 
            'user': user,
            'notis': notis,
            'upcoming': upcoming
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
        self.auth()
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
    ('/', LoginHandler),
    ('/map', MapHandler),

    # controllers/rides.py
    ('/rides', RideHandler),
    ('/ride/(\d+)', GetRideHandler),
    ('/join_ride', RideJoinHandler),
    ("/newride", NewRideHandler),
    ('/home', HomeHandler),
    # end rides

    # controllers/users.py
    ('/user/(\d+)', GetUserHandler),
    ('/user/edit/(\d+)', EditUserHandler),
    ('/user/notification/(\d+)', NotificationUserHandler),
    ('/user', UserHandler),
    ('/user/photo/(\d+)', GetImage),
    # end users

    # controllers/comments.py
    ('/comment', CommentHandler),
    ('/comments', FetchComments),
    ('/comment/(\d+)', GetComment),
    # end comments

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