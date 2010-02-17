#!/usr/bin/env python2.5
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




import wsgiref.handlers
import datetime
from datetime import date
from django.utils import simplejson
##from django.core import serializers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

#from appengine_django.models import BaseModel
from google.appengine.ext import db
from google.appengine.api import users

import logging
import urllib
import os.path

# Make this very flat to start with, then add references later...
class Ride(db.Model):
    max_passengers = db.IntegerProperty()
    num_passengers = db.IntegerProperty()
    driver = db.UserProperty()
    start_point_title = db.StringProperty()
    start_point_lat = db.FloatProperty()
    start_point_long = db.FloatProperty()
    destination_title = db.StringProperty()
    destination_lat = db.FloatProperty()
    destination_long = db.FloatProperty()
    ToD = db.DateTimeProperty()
    part_of_day = db.StringProperty()
    passengers = db.ListProperty(db.Key)
    contact = db.StringProperty()

    def to_dict(self):
        res = {}
        for k in Ride._properties:   ## special case ToD
            if k != 'ToD':
                res[k] = getattr(self,k) #eval('self.'+k)
        res['ToD'] = str(self.ToD)
        return res

class Passenger(db.Model):
    name = db.UserProperty()
    contact = db.StringProperty()
    location = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    ride = db.ReferenceProperty()
    
    """
    Check home page functionality regarding the search for passenger rides
    & list of passengers for driver rides
    
    Change method of display in entire project regarding passengers
    """

class MyClass:
    max_passengers = 0
    num_passengers = 0
    driver = "Brad"

class MainHandler(webapp.RequestHandler):

    def get(self):
        query = db.Query(Ride)
        ride_list = query.fetch(limit=100)
        user = users.get_current_user()
        greeting = ''
        logout = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
            logout = users.create_logout_url("/")
       
        self.response.out.write(template.render('index.html', {
            'ride_list': ride_list, 
            'greeting' : greeting,
            'nick' : user.nickname(),
            'logout':logout
            }))


class RideQueryHandler(webapp.RequestHandler):
    """
    Parse and process requests for rides
    returns json
    """

    def get(self):
        """
        Arguments:
        - `self`:

        The query may be filtered by after date, and before date.  Expect to get the dates
        in the form YYYY-MM-DD
        """
        # Create a query object
        allRides = Ride.all()
        # Check to see if the browser side provided us with before/after dates
        after_date = self.request.get('after')
        before_date = self.request.get("before")
        # If there is an after date then limit the rides to those after the date
        # using the filter method
        if after_date:
            y,m,d = after_date.split('-')
            allRides.filter('ToD >= ',datetime.datetime(int(y),int(m),int(d)))

        if before_date:
            y,m,d = before_date.split("-")
            allRides.filter('ToD <=',datetime.datetime(int(y),int(m),int(d)))
        

        logging.debug("after %s before %s", after_date, before_date)

        # Now put together the json result to send back to the browser.
        json = simplejson.dumps([r.to_dict() for r in allRides])
        self.response.headers.add_header('content-type','application/json')
        self.response.out.write(json)
        logging.debug('end get')
    

class NewRideHandler(webapp.RequestHandler):
    """
    For new Rides
    """

    def post(self):
        """
        Called when a new ride needs to be added to the database.
        Probably with all of this data it should be done as a form post.
        
        Arguments:
        - `self`:
        Web Arguments:
        - max_passengers
        - num_passengers
        - driver
        - start_point_title
        - start_point_lat
        - start_point_long
        - destination_title
        - destination_lat
        - destination_long
        - part_of_day
        - ToD
        - contact
        """

        newRide = Ride()
        maxp = self.request.get("maxp")
        inumber = self.request.get("contact")
        number = inumber[0:3]+'-'+inumber[3:6]+'-'+inumber[6:]
        newRide.contact = number
        newRide.max_passengers = int(maxp)
        newRide.num_passengers = 0
        newRide.driver = users.get_current_user()

        """ # For testing
        latlng = ['41.517658', '-95.452065']
        lat = float(latlng[0])
        lng = float(latlng[1])
        """
        lat = float(self.request.get("lat"))
        lng = float(self.request.get("lng"))
        checked = self.request.get("checked")
        if checked == 'true':
          newRide.start_point_title = self.request.get("from")
          newRide.start_point_lat = lat
          newRide.start_point_long = lng
          newRide.destination_title = "Luther College, Decorah, IA"
          newRide.destination_lat = 43.313059
          newRide.destination_long = -91.799501
        elif checked == 'false':
          newRide.start_point_title = "Luther College, Decorah, IA"
          newRide.start_point_lat = 43.313059
          newRide.start_point_long = -91.799501
          newRide.destination_title = self.request.get("to")
          newRide.destination_lat = lat
          newRide.destination_long = lng             
        y = int(self.request.get("year"))
        m = int(self.request.get("month")) + 1
        d = int(self.request.get("day"))
        early_late_value = int(self.request.get("earlylate"))
        part_of_day_value = int(self.request.get("partofday"))
        part_of_day = ''
        if early_late_value == 0:
          part_of_day += 'Early '
        else:
          part_of_day += 'Late '
        if part_of_day_value == 0:
          part_of_day += 'Morning'
        elif part_of_day_value == 1:
          part_of_day += 'Afternoon'
        else:
          part_of_day += 'Evening'
        newRide.part_of_day = part_of_day
        newRide.ToD = datetime.datetime(int(y),int(m),int(d))
        newRide.passengers = []
        newRide.put()
        query = db.Query(Ride)
        ride_list = query.fetch(limit=100)
        user = users.get_current_user()
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = 'Your ride has been created!'
        self.response.out.write(template.render('index.html', {
            'ride_list': ride_list, 
            'greeting': greeting,
            'message': message
            }))
  
class AddPassengerHandler(webapp.RequestHandler):
    """
    Handles addition of passengers
    """
    def post(self):
      """
      Called when adding a passenger to a ride
      
      Arguments:
      - 'self'
      
      Web Arguments:
      - user_name
      - ride_key
      """
      # The current user can add himself to the ride.  No need for this in the form.
      user_name = users.get_current_user()
      
      ride_key = self.request.get('ride_key')
      contact = self.request.get('contact')
      address = self.request.get('address')
      lat = float(self.request.get('lat'))
      lng = float(self.request.get('lng'))
      ride = db.get(db.Key(ride_key))
      if ride == None: # Check if the ride was found
        temp = os.path.join(os.path.dirname(__file__), 'templates/error.html')
        outstr = template.render(temp, {'error_message': 'Error in ride matching'})
        self.response.out.write(outstr)
      # Check if the current user is the driver
      elif ride.max_passengers == ride.num_passengers:
        doRender(self, 'error.html', {'error_message': 'This ride is full'})
      # Check if the current user is already on the ride
      already = False
      for p in ride.passengers:
        if db.get(p).name == user_name:
          already = True
      if already:
        temp = os.path.join(os.path.dirname(__file__), 'templates/error.html')
        outstr = template.render(temp, {'error_message': 'You are already registered for this ride!'})
        self.response.out.write(outstr)
      # Check if the current user is already the driver for the ride
      elif user_name == ride.driver:
        doRender(self, 'error.html', {'error_message': 'You can\'t be a passenger for a ride which you a driving.'})
      else:
        passenger = Passenger()
        passenger.name = user_name
        passenger.contact = contact
        passenger.location = address
        passenger.lat = lat
        passenger.lng = lng
        passenger.ride = db.Key(ride_key)
        pass_key = passenger.put()
        ride.num_passengers = ride.num_passengers + 1
        ride.passengers.append(pass_key)
        ride.put()

        if ride.num_passengers == ride.max_passengers:
          capacity_message = 'is now full.'
        else:
          num_left = ride.max_passengers - ride.num_passengers
          capacity_message = 'can hold ' + str(num_left) + ' more passengers.'
        query = db.Query(Ride)
        ride_list = query.fetch(limit=100)
        user = users.get_current_user()
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = 'You have been added to %s\'s ride.' % (ride.driver)
        self.response.out.write(template.render('index.html', {
            'ride_list': ride_list, 
            'greeting': greeting,
            'message': message
            }))

class HomeHandler(webapp.RequestHandler):
    """
    Displays personal homepage
    """
    def get(self):
      username = users.get_current_user()
      drive = db.Query(Ride)
      drive.filter('driver =', username)
      driverides = drive.fetch(limit=100)
      for ride in driverides:
        ride.passengerobjects = []
        ride.jsmonth = ride.ToD.month
        ride.jsyear = ride.ToD.year
        ride.jsday = ride.ToD.day 
        if ride.start_point_title == 'Luther College, Decorah, IA':
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
        if ride.start_point_title == 'Luther College, Decorah, IA':
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
                          'user': username,
                          'driverides': driverides, 
                          'passengerrides': passengerrides })
    
class RideInfoHandler(webapp.RequestHandler):
    """
    Displays detailed information regarding a specific ride
    Holds a GMap detailing the trip
    """
    def get(self):
      username = users.get_current_user()
      key = self.request.get('key')
      ride = db.get(key)
      if ride == None:
        doRender(self, 'error.html', {
                              'error_message': "No such ride exists."})
      else:
        ride.passengerobjects = []
        ride.jsmonth = ride.ToD.month
        ride.jsyear = ride.ToD.year
        ride.jsday = ride.ToD.day
        if ride.start_point_title == 'Luther College, Decorah, IA':
          ride.doOrPu = 0
        else:
          ride.doOrPu = 1
        for p in ride.passengers:
          passenger = db.get(p)
          if (ride.start_point_lat == passenger.lat and ride.start_point_long == passenger.long) or (ride.destination_lat == passenger.lat and ride.destination_long == passenger.lng):
            passenger.samePlace = True;
          else:
            passenger.samePlace = False;
          ride.passengerobjects.append(passenger)           
        doRender(self, 'rideinfo.html', {
                              'ride': ride})

class DeleteRideHandler(webapp.RequestHandler):
    """
    Deletes a ride using a key
    """
    def get(self):
      key = self.request.get('key')
      ride = db.get(key)
      if ride == None:
        doRender(self, 'error.html', {
                              'error_message': "No such ride exists."})
      else:
        db.delete(ride)
        query = db.Query(Ride)
        ride_list = query.fetch(limit=100)
        user = users.get_current_user()
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = 'Your ride has been deleted.'
        self.response.out.write(template.render('index.html', {
            'ride_list': ride_list, 
            'greeting' : greeting,
            'message' : message
            }))

class RemovePassengerHandler(webapp.RequestHandler):
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
        ride_list = query.fetch(limit=100)
        user = users.get_current_user()
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = '%s has been removed from %s\'s ride.' % (name, ride.driver)
        self.response.out.write(template.render('index.html', {
            'ride_list': ride_list, 
            'greeting' : greeting,
            'message' : message
            }))

class IncorrectHandler(webapp.RequestHandler):
    """
    Returns an error for URLs not defined
    """
    def get(self):
      doRender(self, 'error.html', {
                            'error_message': "Page does not exist."})
        
def doRender(handler, name='index.html', value={}):
    temp = os.path.join(os.path.dirname(__file__), 'templates/' + name)
    outstr = template.render(temp, value)
    handler.response.out.write(outstr)

def geocode(address):
 # This function queries the Google Maps API geocoder with an
 # address. It gets back a csv file, which it then parses and
 # returns a string with the longitude and latitude of the address.

 # This isn't an actual maps key, you'll have to get one yourself.
 # Sign up for one here: http://code.google.com/apis/maps/signup.html
#  mapsKey = 'ABQIAAAAn9H2MPjtzJCGP4OYVLJuOxQbtjENHIgppMgd3dAaKy16g5o_8xTNamzlZZNZ42SPIkttrL_Smwh7RQ'
  mapsKey = 'ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixQ2JlMNfqnGb2qqWZtmZLchh1TSjRS0zuchuhlR8g4tlMGrjg34sNmyjQ'
  mapsUrl = 'http://maps.google.com/maps/geo?q='
     
 # This joins the parts of the URL together into one string.
  url = ''.join([mapsUrl,urllib.quote(address),'&output=csv&key=',mapsKey])
    
 # This retrieves the URL from Google, parses out the longitude and latitude,
 # and then returns them as a string.
  coordinates = urllib.urlopen(url).read().split(',')
  #coorText = '%s,%s' % (coordinates[3],coordinates[2])
  return (float(coordinates[3]),float(coordinates[2]))


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    # prepopulate the database

    query = db.Query(Ride)

    
    if query.count() < 2:
        newRide = Ride()
        newRide.max_passengers = 3
        newRide.num_passengers = 0
        newRide.driver = users.User("bmiller@luther.edu")
        newRide.start_point_title = "Luther College, Decorah, IA"
        newRide.start_point_long, newRide.start_point_lat = geocode(newRide.start_point_title)
        newRide.destination_title = "Plymouth, MN"
        newRide.destination_long, newRide.destination_lat = geocode(newRide.destination_title)
        newRide.part_of_day = 'Early Morning'
        newRide.ToD = datetime.datetime(2009,9,15)
        newRide.passengers = []
        newRide.put()

        newRide = Ride()
        newRide.max_passengers = 1
        newRide.num_passengers = 0
        newRide.driver = users.User("willke02@luther.edu")
        newRide.start_point_title = "Luther College, Decorah, IA"
        newRide.start_point_long, newRide.start_point_lat = geocode(newRide.start_point_title)
        newRide.destination_title = "Des Moines, IA"
        newRide.destination_long, newRide.destination_lat = geocode(newRide.destination_title)
        newRide.part_of_day = 'Late Afternoon'
        newRide.ToD = datetime.datetime(2009,9,17)
        newRide.passengers = []
        newRide.put()
    
    
    
    application = webapp.WSGIApplication([('/', MainHandler),
                                  ('/getrides', RideQueryHandler ),
                                  ("/newride", NewRideHandler),
                                  ("/addpass", AddPassengerHandler),
                                  ('/home', HomeHandler),
                                  ('/rideinfo', RideInfoHandler),
                                  ('/deleteride', DeleteRideHandler),
                                  ('/removepassenger', RemovePassengerHandler),
                                  ('/.*', IncorrectHandler),
                                  ],
                                  debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
