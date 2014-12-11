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

from app.cron.notifications import *

from app.common import toolbox

class GetStarted(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()
        toolbox.render(self, 'get_started.html',  {
            'user': user
        })

class Marketing(BaseHandler):
    def get(self):
        redirect = invited = None
        if 'redirect' in self.request.GET:
            redirect = self.request.GET['redirect']
        if 'invited' in self.request.GET:
            invited = self.request.GET['invited']
            self.session['invited'] = str(invited)
        print(redirect, invited)
        invite = None
        if redirect and invited:
            invite = Circle.get_by_id(int(invited))
        toolbox.render(self, 'marketing/home.html', {
            'invite': invite
        })
    
class MapHandler(BaseHandler):
    def get(self, circle_id):
        self.auth()
        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        toolbox.render(self, 'map.html', {
            'user': user,
            'circle': circle
        })

class IncorrectHandler(BaseHandler):
    def get(self):
        self.redirect('/')

class HelpHandler(BaseHandler):
    def get(self):
        user = self.current_user()

        toolbox.render(self, 'help.html', {
            'user': user
        })

app = webapp2.WSGIApplication([
    ('/', Marketing),
    ('/get_started', GetStarted),
    ('/circle/(\d+)/map', MapHandler),

    # cron
    ('/notifications/check', CheckNotifications),

    # controllers/accounts.py
    ('/login', LoginHandler),
    ('/register', RegisterHandler),
    ('/reset_password', PasswordReset),
    ('/reset/(\w+)', NewPassword),

    # controllers/home.py
    ('/home', HomeHandler),

    # controllers/rides.py
    ('/rides', RideHandler),
    ('/ride/(\d+)', GetRide),
    ('/ride/(\d+)/edit', EditRide),
    ('/ride/(\d+)/driver', JoinDriver),
    ('/ride/(\d+)/passenger', JoinPassenger),
    ('/ride/create', CreateRide),
    ('/ride/(\d+)/delete', DeleteRide),
    ('/filter', FilterRides),

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
    ('/circle/(\d+)/message', CircleMessage),
    ('/circle/(\d+)/members', CircleMembers),
    ('/circle/(\d+)/requests', CircleRequests),
    ('/circle/(\d+)/rides', CircleRides),
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
    ('/event/(\d+)/edit', EditEvent),
    ('/event/(\d+)/delete', DeleteEvent),
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
        '/signout',
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