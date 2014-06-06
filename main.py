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

from app.model import *

from app.controllers.account_flow import *
from app.controllers.circles import *
from app.controllers.events import *
from app.controllers.rides import *
from app.controllers.comments import *

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
        doRender(self, 'index_rework.html', {})

class SubmitRatingHandler(BaseHandler):
    def post(self):
        aquery = db.Query(College)
        mycollege = aquery.get()  
        drivernum = self.request.get("driver")
        text = self.request.get("ratetext")
        ooFrating = self.request.get("ooFrating") # Out Of Five
        user = FBUser.get_by_key_name(drivernum)
        user.drivercomments.append(text)
        user.numrates = user.numrates + 1
        if user.rating == None:
            user.rating = float(ooFrating)
        else:
            user.rating = user.rating + float(ooFrating)
        user.put()
        doRender(self, "submit.html", {"college", mycollege})
        self.redirect("/home")

class HomeHandler(BaseHandler):
    def get(self):
        self.auth()
        aquery = db.Query(Community)
        community = aquery.get()
        user = self.current_user()

        doRender(self, 'home.html', { 
            'community': community,
            'user': user
        })

class RateHandler(BaseHandler):
    
    def get(self):
      aquery = db.Query(College)
      mycollege= aquery.get()  
      drivernum = self.request.get('dkey')
      user = FBUser.get_by_key_name(drivernum)
      doRender(self, 'ratedriver.html', {
            'driver': user.nickname(),
            'drivernum':drivernum,
            'college':mycollege
            })
      
class RemovePassengerHandler(BaseHandler):
    """
    Removes a passenger using a key and the current user
    """
    def get(self):
      rkey = self.request.get('rkey')
      ride = db.get(rkey)
      pkey = self.request.get('pkey')
      passenger = db.get(pkey)
      #self.response.out.write('Would remove %s from %s ride' % (passenger.name, ride.driver))
      if ride == None:
        doRender(self, 'error.html', {
                              'error_message': "No such ride exists."})
      elif passenger == None:
        doRender(self, 'error.html', {
                              'error_message': "No such passenger exists."})
      else:
        name = passenger.name
        ride.passengers.remove(passenger.key())
        passenger.delete()
        ride.num_passengers -= 1
        ride.put()
        query = db.Query(Ride)
        query.filter("ToD > ", datetime.date.today())
        ride_list = query.fetch(limit=100)
        user = self.current_user
        aquery = db.Query(College)
        mycollege= aquery.get()
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = '%s has been removed from %s\'s ride.' % (name, ride.driver)
        doRender(self, 'map.html', {
            'ride_list': ride_list, 
            'greeting' : greeting,
            'college': mycollege,
            'address': mycollege.address,
            'nick' : user.nickname(),
            'logout':'/auth/logout',
            'mapkey':MAP_APIKEY,
        })

class DriverRatingHandler(BaseHandler):

    def get(self):
        drivernum = self.request.get('drivernum')
        user = FBUser.get_by_key_name(drivernum)
        ratingslist= user.drivercomments
        name = user.nickname()
        if user.rating != None:
            rating = user.rating / user.numrates
        else:
            rating= 0.00
        numrates = user.numrates
      
        doRender(self, 'driverrating.html', {
            'ratingslist': ratingslist,
            'name': name,
            'rating':str(rating)[0:3],
            'numrates':numrates
        })

class SchoolErrorHandler(BaseHandler):
    
    def get(self):
      aquery = db.Query(College)
      mycollege= aquery.get() 
      doRender(self, 'schoolerror.html', {"college": mycollege})

class RideSuccessHandler(BaseHandler):
    def get(self):
       aquery = db.Query(College)
       mycollege= aquery.get() 
       noDriver = 0
       noPass = 0
       goodRide = 0
       myquery = db.Query(Ride)
       rides = myquery.fetch(limit=1000000)
       for ride in rides:
           logging.debug(ride.driver)
           if ride.driver == None:
               noDriver += 1
           else:
               if ride.num_passengers >0:
                   goodRide += 1
               else:
                   noPass += 1
       doRender(self, 'ridesuccess.html', {
            'noDriver': noDriver,
            'noPass': noPass,
            'goodRide': goodRide,
            'totalRides': len(rides),
            'college': mycollege
        })   

class ConnectPageHandler(BaseHandler):

    def get(self):
        user = self.current_user
        userID = user.id
        doRender(self, 'connectride.html',{
            'drivernum': userID
        })

class DatabaseHandler(BaseHandler):
    def get(self):
        ID = self.request.get('ID', None)
        
        if ID is None:
            # First request, just get the first name out of the datastore.
            ride = db.Query(Ride).get()
            ID = ride.ID

        q = db.Query(Ride)
        rides = q.fetch(limit=2)
        current_ride = rides[0]
        if len(rides) == 2:
            next_ride = rides[1].ID
            next_url = '/update?ID=%s' % urllib.quote(next_ride)
        else:
            next_ride = 'FINISHED'
            next_url = '/'  # Finished processing, go back to main page.
        # In this example, the default values of 0 for num_votes and avg_rating are
        # acceptable, so we don't need to do anything other than call put().
        if not isinstance(current_ride.driver,str):
           current_ride.put()

        doRender(self, 'update.html', {
            'current_name': ID,
            'next_name': next_ride,
            'next_url': next_url,
        })

class IncorrectHandler(webapp2.RequestHandler):
    """
    Returns an error for URLs not defined
    """
    def get(self):
        doRender(self, 'error.html', {
            'error_message': "Page does not exist."
        })

class HelpHandler(BaseHandler):
    def get(self):
        doRender(self, 'help.html', {})

class AllHandler(BaseHandler):
    def get(self):
        self.auth()
        doRender(self, 'index_rework.html', {})

class MovePassengerHandler(BaseHandler):
    def post(self):
        user= self.current_user
        keys = self.request.get("keys")
        keyList = keys.split("|")
        pRide= Ride.get(keyList[0])
        dRide= Ride.get(keyList[1])
        logging.debug(dRide)
        for passenger in pRide.passengers:
            if dRide.passengers:
                dRide.passengers.append(passenger)
            else:
                dRide.passengers=[passenger]
        dRide.num_passengers = dRide.num_passengers +len(pRide.passengers)
        dRide.put()
        db.delete(keyList[0])

        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                        (user.nickname(), users.create_logout_url("/")))
        message = 'You have added passengers to your ride.'

        doRender(self, 'index.html', {
            'greeting' : greeting,
            'message' : message,
            'mapkey':MAP_APIKEY,
        })

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

    ('/applyedits', ChangeRideHandler),
    ('/removepassenger', RemovePassengerHandler),
          ('/signout', SignOutHandler),
          ('/ratedriver', RateHandler),
          ('/submittext', SubmitRatingHandler),
    ('/driverrating',DriverRatingHandler),
          ('/school',SchoolErrorHandler),
    ('/ridesuccess',RideSuccessHandler),

    ('/comment', CommentHandler),

    # controllers/circles.py
    ('/circle/(\d+)', GetCircleHandler),
    ('/addCircle', AddCircleHandler),
    ('/newCircle',NewCircleHandler),
    ('/circles', CircleHandler),
    ('/join_circle', JoinCircle),
    # end circles

    # controllers/events.py
    ('/events', EventHandler),
    ('/newevent', NewEventHandler),
    ('/getevents', EventQueryHandler),
    ('/neweventride', NewEventRideHandler),
    ('/addevents', AddEventsHandler),
    ('/addmultipleevents',AddMultipleEventsHandler),
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
    # end auth routes

    ('/movepass', MovePassengerHandler),
    ('/connectride',ConnectPageHandler),
    ('/databasefix', DatabaseHandler),
    ('/testing', create_user),
    ('/help', HelpHandler),
    ('/.*', IncorrectHandler)
    ],
    config = app_config,
    debug=True)

# This is actually the development one.
# lutherrideshare.appspot key: ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixS0LiYWImofzW4gd3oCqtkHKt0IaBT-STdq-gdH-mW2_ejMPXqxnfJjgw

# This has the app id of ridesharebeta   and is also on ridesharebeta.appspot.com
# rideshare.luther.edu key:  ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixQ2JlMNfqnGb2qqWZtmZLchh1TSjRS0zuchuhlR8g4tlMGrjg34sNmyjQ