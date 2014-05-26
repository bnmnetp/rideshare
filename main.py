# This is actually the development one.
# lutherrideshare.appspot key: ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixS0LiYWImofzW4gd3oCqtkHKt0IaBT-STdq-gdH-mW2_ejMPXqxnfJjgw

# This has the app id of ridesharebeta   and is also on ridesharebeta.appspot.com
# rideshare.luther.edu key:  ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixQ2JlMNfqnGb2qqWZtmZLchh1TSjRS0zuchuhlR8g4tlMGrjg34sNmyjQ
#!/usr/bin/env python2.7
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2

# testing
from app.controllers.test_account import create_user

choice = "facebook"

import wsgiref.handlers
import datetime
from datetime import date
from django.utils import simplejson
from google.appengine.api import mail

##from django.core import serializers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import jinja2
import app.facebook

#from appengine_django.models import BaseModel
from google.appengine.ext import db
if choice != "facebook":
   from google.appengine.api import users
else:
   import app.nateusers as users
   from app.nateusers import LoginHandler, LogoutHandler, BaseHandler, FBUser

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

from app.common.toolbox import doRender

MAP_APIKEY=""
FROM_EMAIL_ADDR="ridesharedecorah@gmail.com"
NOTIFY_EMAIL_ADDR="ridesharedecorah@gmail.com"
rideshareWebsite = "http://www.decorahrideshare.com"

early_late_strings = { "0": "Early", "1": "Late" }
part_of_day_strings = { "0": "Morning", "1": "Afternoon", "2": "Evening" }

mycollege = College(name = "Luther College",
    address = "700 College Drive Decorah,IA",
    lat = 43.313059, lng = -91.799501,
    appId = "193298730706524",
    appSecret = "44d7cce20524dc91bf7694376aff9e1d")

aquery = db.Query(College)
if aquery.count() == 0:
    #development site
    mycollege = College(name = "Luther College",
        address = "700 College Drive Decorah,IA",
        lat = 43.313059, lng = -91.799501,
        appId = "193298730706524",
        appSecret = "44d7cce20524dc91bf7694376aff9e1d")
    #live site   
    #college = College(name ="Luther College", address= "700 College Drive Decorah,IA", lat =43.313059, lng=-91.799501, appId="284196238289386",appSecret="07e3ea3ffda4aa08f8c597bccd218e75")   
    #college = College(name= "LaCrosse University", address = "1725 State Street, La Crosse, WI", lat=43.812834, lng=-91.229022,appId="193298730706524",appSecret="44d7cce20524dc91bf7694376aff9e1d")
    #college = College(name="Decorah", address="Decorah, IA", appId="177023452434948", appSecret="81a9f8776108bd1f216970823458533d", lat=43.303306, lng=-91.785709)
    mycollege.put()
 

class MainHandler(BaseHandler):
  def get(self):
    self.current_user_id = "123";
    user = FBUser.get_by_key_name(self.current_user_id)
    aquery = db.Query(College)
    mycollege= aquery.get()

    eventsList = []
    circles = []
    for item in user.circles:
        query = db.Query(Event)
        query.filter("ToD > ", datetime.date.today())
        query.filter("circle =",str(item))
        event_list = query.fetch(limit=100)
        logging.debug(event_list)
        for event in event_list:
          eventsList.append(event.to_dict())
        circles.append(Circle.get_by_id(int(item)))
    doRender(self, 'main.html', {
            'event_list': eventsList,
            'circles' : circles,
            'college':mycollege,
            'logout':'/auth/logout',
            'nick':self.current_user.nickname()
            })
    
class MapHandler(BaseHandler):

    def get(self):
        query = db.Query(Ride)
        query.filter("ToD > ", datetime.date.today())
        logging.debug(self.request.get("circle"))
        query.filter("circle = ",self.request.get("circle"))
        ride_list = query.fetch(limit=100)
        
        aquery = db.Query(College)
        mycollege= aquery.get()
        user = self.current_user
        logging.debug(users.create_logout_url("/"))
        greeting = ''
        logout = ''
        #if user:
        #    greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
        #          (user.nickname(), users.create_logout_url("/")))
        #    logout = users.create_logout_url("/")
        #    logging.debug(logout)
        #else:
        #    self.redirect('/auth/login')
        #    return
        
        logging.debug(mycollege.address)
        doRender(self, 'map.html', {
            'ride_list': ride_list, 
            'greeting' : greeting,
            'college': mycollege,
            'address': mycollege.address,
            'nick' : user.nickname(),
            'user':user.id,
            'logout':'/auth/logout',
            'mapkey':MAP_APIKEY,
            })

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
    """
    Displays personal homepage
    """
    def get(self):
      aquery = db.Query(College)
      mycollege= aquery.get()
      user = self.current_user
      username = user.id
      events = db.Query(Event)
      events.filter('creator =',self.current_user.id)
      event_list = events.fetch(limit=100)
      drive = db.Query(Ride)
      drive.filter('driver =', username)
      driverides = drive.fetch(limit=100)
      for ride in driverides:
        ride.passengerobjects = []
        ride.jsmonth = ride.ToD.month
        ride.jsyear = ride.ToD.year
        ride.jsday = ride.ToD.day 
        if ride.start_point_title == mycollege.name:
          ride.doOrPu = 0
        else:
          ride.doOrPu = 1
        for p in ride.passengers:
          ride.passengerobjects.append(db.get(p))
      passengers = db.Query(Passenger)
      passengers.filter('name =', username)
      passengerList = passengers.fetch(limit=100) # All passenger objects with 'my' name
      passengerrides = [] # Will contain all Rides the user is a passenger for
      for p in passengerList:
        passengerrides.append(p.ride)
      for ride in passengerrides:
        if ride.start_point_title == mycollege.name:
          ride.doOrPu = 0
        else:
          ride.doOrPu = 1
        ride.passengerobjects = [] # Will contain all Passenger objects for each Ride
        ride.jsmonth = ride.ToD.month
        ride.jsyear = ride.ToD.year
        ride.jsday = ride.ToD.day 
        for p in ride.passengers:
          ride.passengerobjects.append(db.get(p))
      doRender(self, 'home.html', { 
                          'college':mycollege,  
                          'user': user.nickname(),
                          'driverides': driverides, 
                          'logout':'/auth/logout',
                          'passengerrides': passengerrides,
                          'event_list':event_list })



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


class IncorrectHandler(webapp.RequestHandler):
    """
    Returns an error for URLs not defined
    """
    def get(self):
      doRender(self, 'error.html', {
                            'error_message': "Page does not exist."})

class HelpHandler(BaseHandler):
    def get(self):
        doRender(self, 'help.html', {})

class ReworkHandler(BaseHandler):
    def get(self):
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

def geocode(address):
 # This function queries the Google Maps API geocoder with an
 # address. It gets back a csv file, which it then parses and
 # returns a string with the longitude and latitude of the address.

 # This isn't an actual maps key, you'll have to get one yourself.
 # Sign up for one here: http://code.google.com/apis/maps/signup.html
#  mapsKey = 'ABQIAAAAn9H2MPjtzJCGP4OYVLJuOxQbtjENHIgppMgd3dAaKy16g5o_8xTNamzlZZNZ42SPIkttrL_Smwh7RQ'

  mapsUrl = 'http://maps.google.com/maps/geo?q='
     
 # This joins the parts of the URL together into one string.
  url = ''.join([mapsUrl,urllib.quote(address),'&output=csv&key=',MAP_APIKEY])
    
 # This retrieves the URL from Google, parses out the longitude and latitude,
 # and then returns them as a string.
  coordinates = urllib.urlopen(url).read().split(',')
  #coorText = '%s,%s' % (coordinates[3],coordinates[2])
  return (float(coordinates[3]),float(coordinates[2]))

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, WebApp World!')

app = webapp2.WSGIApplication([
    ('/', LoginPageHandler),
    ('/map', MapHandler),
    ('/main',MainHandler),

    # controllers/rides.py
    ('/getrides', RideQueryHandler ),
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
    ('/auth/login', LoginHandler),
    ('/auth/logout',LogoutHandler),
          ('/signout', SignOutHandler),
          ('/ratedriver', RateHandler),
          ('/submittext', SubmitRatingHandler),
    ('/driverrating',DriverRatingHandler),
          ('/school',SchoolErrorHandler),
    ('/ridesuccess',RideSuccessHandler),

    # controllers/circles.py
    ('/updateCircles',UpdateCirclesHandler),
    ('/changecircles',ChangeCirclesHandler),
    ('/addCircle', AddCircleHandler),
    ('/newCircle',NewCircleHandler),
    # end circles

    # controllers/events.py
    ('/newevent',NewEventHandler),
    ('/getevents',EventQueryHandler),
    ('/neweventride', NewEventRideHandler),
    ('/addevents',AddEventsHandler),
    ('/addmultipleevents',AddMultipleEventsHandler),
    # end events

    ('/movepass', MovePassengerHandler),
    ('/connectride',ConnectPageHandler),
    ('/databasefix', DatabaseHandler),
    ('/map_rework', ReworkHandler),
    ('/testing', create_user),
    ('/help', HelpHandler),
    ('/.*', IncorrectHandler)
    ],
    debug=True)

# This is actually the development one.
# lutherrideshare.appspot key: ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixS0LiYWImofzW4gd3oCqtkHKt0IaBT-STdq-gdH-mW2_ejMPXqxnfJjgw

# This has the app id of ridesharebeta   and is also on ridesharebeta.appspot.com
# rideshare.luther.edu key:  ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixQ2JlMNfqnGb2qqWZtmZLchh1TSjRS0zuchuhlR8g4tlMGrjg34sNmyjQ
