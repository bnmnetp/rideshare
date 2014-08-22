import webapp2
from simpleauth import SimpleAuthHandler
from app.base_handler import BaseHandler

# testing
from app.controllers.test_account import email_test
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

from google.appengine.api import mail

from google.appengine.ext import db

from app.controllers.circles import *
from app.controllers.events import *
from app.controllers.rides import *
from app.controllers.comments import *
from app.controllers.users import *
from app.controllers.invites import *
from app.controllers.alert import *
from app.controllers.accounts import *
from app.controllers.home import *

from app.common.toolbox import doRender

class Marketing(BaseHandler):
    def get(self):
        doRender(self, 'marketing/home.html')

class GetStarted(BaseHandler):
    def get(self):
        doRender(self, 'marketing/get_started.html')
    
class MapHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        circle = self.circle()

        doRender(self, 'map.html', {
            'user': user,
            'circle': circle
        })

class IncorrectHandler(BaseHandler):
    def get(self):
        self.redirect('/')

class HelpHandler(BaseHandler):
    def get(self):
        user = self.current_user()

        doRender(self, 'help.html', {
            'user': user
        })

app = webapp2.WSGIApplication([
    ('/', Marketing),
    ('/get_started', GetStarted),
    ('/map', MapHandler),

    # controllers/accounts.py
    ('/login', LoginHandler),
    ('/register', RegisterHandler),

    # controllers/home.py
    ('/home', HomeHandler),

    # controllers/rides.py
    ('/rides', RideHandler),
    ('/ride/(\d+)', GetRideHandler),
    ('/ride/(\d+)/edit', EditRide),
    ('/ride/(\d+)/driver', JoinDriver),
    ("/newride", NewRideHandler),
    ('/filter', FilterRides),
    ('/event/(\d+)/(\w+)', RideEvent),

    # controllers/users.py
    ('/user/(\d+)', GetUserHandler),
    ('/user/edit/(\d+)', EditUserHandler),
    ('/user/notification/(\d+)', NotificationUserHandler),
    ('/user', UserHandler),
    ('/user/photo/(\d+)', GetImage),

    # controllers/comments.py
    ('/comment', CommentHandler),
    ('/comments', FetchComments),
    ('/comment/(\d+)', GetComment),

    # controllers/circles.py
    ('/circle/(\d+)', GetCircleHandler),
    ('/circle/(\d+)/invite', GetCircleInvite),
    ('/circle/(\d+)/invited', CircleInvited),
    ('/circle/(\d+)/change', ChangeCircle),
    ('/circle/(\d+)/edit', EditCircle),
    ('/circle/(\d+)/kick', KickMember),
    ('/circle/(\d+)/promote', PromoteMember),
    ('/circle/(\d+)/request', RequestJoin),
    ('/circle/(\d+)/accept', RequestAccept),
    ('/newCircle', NewCircleHandler),
    ('/circles', CircleHandler),
    ('/join_circle', JoinCircle),

    # controllers/invites.py
    ('/invite/(\d+)', SendInvite),
    ('/invite/(\d+)/name', SendInviteName),
    ('/invite/(\d+)/email', SendInviteEmail),
    ('/invite/names', GetNames),
    ('/invites', ViewInvites),

    # controllers/events.py
    ('/event/(\d+)', GetEventHandler),
    ('/events', EventHandler),
    ('/newevent', NewEventHandler),

    # controllers/alert.py
    ('/alert/(\d+)/dismiss', DismissAlert),

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

    ('/email_test', email_test),
    ('/help', HelpHandler),
    ('/.*', IncorrectHandler)
],
    config = app_config,
    debug = True
)