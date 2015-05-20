import webapp2
import urllib2
from simpleauth import SimpleAuthHandler
from app.base_handler import BaseHandler
import app.secrets as secrets
from app.model import *
import wsgiref.handlers
from google.appengine.api import mail
from google.appengine.ext import db

# testing
from app.controllers.test_account import email_test
# end testing

from app.controllers.circles import *
from app.controllers.events import *
from app.controllers.rides import *
from app.controllers.comments import *
from app.controllers.users import *
from app.controllers.invites import *
from app.controllers.alert import *
from app.controllers.accounts import *
from app.controllers.home import *
from app.controllers.calendar import *

from app.cron.notifications import *

from app.common import toolbox

app_config = {
    'webapp2_extras.sessions': {
        'cookie_name': '_simpleauth_sess',
        'secret_key': secrets.SESSION_KEY
    },
    'webapp2_extras.auth': {
        'user_attributes': []
    }
}

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

        toolbox.render(self, 'map2.html', {
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

class RideStats(BaseHandler):
    def get(self, ver_id):
        if ver_id != 'rced':
            self.redirect('/')
        else:
            rides = Ride.all().fetch(None)
            total_distance = 0
            adjusted_distance = 0
            total_rides = 0
            adjusted_rides = 0

            total_members = User.all().count()
            for r in rides:
                o_lat_lng = str(r.origin_lat) + ',' + str(r.origin_lng)
                d_lat_lng = str(r.dest_lat) + ',' + str(r.dest_lng)
                r.total_passengers = Passenger.all().filter('ride =', r.key()).count()
                url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&units=imperial" % (o_lat_lng, d_lat_lng)

                if r.driver:
                    d = db.get(r.driver.key())
                    if not d:
                        r.driver = None

                response = urllib2.urlopen(url)
                json_geocode = json.loads(response.read())
                if json_geocode['rows'][0]['elements'][0]['status'] == 'OK':
                    meters = json_geocode['rows'][0]['elements'][0]['distance']['value']

                    r.distance = meters * 0.000621371192
                    r.adjusted_miles = r.distance * (r.total_passengers + 1)

                    total_distance += r.distance
                    adjusted_distance += r.adjusted_miles
                    total_rides += 1
                    adjusted_rides += (1 + r.total_passengers)
                else:
                    r.distance = 0
                    r.adjusted_miles = 0

                users = User.all().fetch(None)

            toolbox.render(self, 'stats.html', {
                'rides': rides,
                'total_distance': total_distance,
                'adjusted_distance': adjusted_distance,
                'total_rides': total_rides,
                'adjusted_rides': adjusted_rides,
                'total_members': total_members,
                'users': users
            })

app = webapp2.WSGIApplication([
    ('/', Marketing),
    ('/get_started', GetStarted),
    ('/circle/(\d+)/map', MapHandler),
    ('/stats/(\w+)', RideStats),

    # login for orgs
    ('/org/(\w+)', OrgLogin),

    # cron
    ('/notifications/check', CheckNotifications),

    # controllers/accounts.py
    ('/login', LoginHandler),
    ('/register', RegisterHandler),
    ('/reset_password', PasswordReset),
    ('/reset/(\w+)', NewPassword),

    # controllers/home.py
    ('/home', Home),

    # controllers/calendar.py
    ('/calendar', GetCalendar),

    # controllers/rides.py
    ('/rides', GetRides),
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
    ('/user/edit/(\d+)/pref', EditPrefHandler),
    ('/user/(\d+)/delete', DeleteUser),
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
    ('/circle/(\d+)/delete', DeleteCircle),
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
    ('/invite/(\d+)/name', SendInviteName),
    ('/invite/(\d+)/email', SendInviteEmail),
    ('/invite/names', GetNames),
    ('/invites', ViewInvites),

    # controllers/events.py
    ('/event/(\d+)', GetEventHandler),
    ('/event/(\d+)/edit', EditEvent),
    ('/event/(\d+)/delete', DeleteEvent),
    ('/event/(\d+)/request', EventRequest),
    ('/event/(\d+)/unrequest', EventUnrequest),
    ('/events', EventHandler),
    ('/newevent', NewEventHandler),

    # controllers/alert.py
    ('/alert/dismiss', DismissAlert),

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