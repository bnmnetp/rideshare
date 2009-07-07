#!/usr/bin/env python
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
    driver = db.StringProperty()  # change to User later
    start_point_title = db.StringProperty()
    start_point_lat = db.FloatProperty()
    start_point_long = db.FloatProperty()
    destination_title = db.StringProperty()
    destination_lat = db.FloatProperty()
    destination_long = db.FloatProperty()
    ToD = db.DateTimeProperty()
    passengers = db.StringListProperty()

    def to_dict(self):
        res = {}
        for k in Ride._properties:   ## special case ToD
            if k != 'ToD':
                res[k] = getattr(self,k) #eval('self.'+k)
        res['ToD'] = str(self.ToD)
        return res

class MyClass:
    max_passengers = 0
    num_passengers = 0
    driver = "Brad"

class MainHandler(webapp.RequestHandler):

    def get(self):
        self.response.out.write(template.render('index.html', {}))


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
        - ToD
        """

        newRide = Ride()
        newRide.max_passengers = int(self.request.get("maxp"))
        newRide.num_passengers = 0
        newRide.driver = self.request.get("driver")
        newRide.start_point_title = self.request.get("startloc")
        newRide.start_point_long, float(self.request.get("startlong"))
        newRide.start_point_lat, float(self.request.get("startlat"))
        newRide.destination_title = self.request.get("dest")
        newRide.destination_long = float(self.request.get("destlong"))
        newRide.destination_lat  = float(self.request.get("destlat"))
        y,m,d = self.request.get("date").split("-")
        newRide.ToD = datetime.datetime(int(y),int(m),int(d))
        newRide.passengers = []
        newRide.put()

        temp = os.path.join(os.path.dirname(__file__),'templates/success.html')
        outstr = template.render(temp,{})
        self.response.out.write(outstr)

        
        
def geocode(address):
 # This function queries the Google Maps API geocoder with an
 # address. It gets back a csv file, which it then parses and
 # returns a string with the longitude and latitude of the address.

 # This isn't an actual maps key, you'll have to get one yourself.
 # Sign up for one here: http://code.google.com/apis/maps/signup.html
  mapsKey = 'ABQIAAAAn9H2MPjtzJCGP4OYVLJuOxQbtjENHIgppMgd3dAaKy16g5o_8xTNamzlZZNZ42SPIkttrL_Smwh7RQ'
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
        newRide.driver = "Brad"
        newRide.start_point_title = "Decorah, IA"
        newRide.start_point_long, newRide.start_point_lat = geocode(newRide.start_point_title)
        newRide.destination_title = "Plymouth, MN"
        newRide.destination_long, newRide.destination_lat = geocode(newRide.destination_title)
        newRide.ToD = datetime.datetime(2009,9,15)
        newRide.passengers = []
        newRide.put()

        newRide = Ride()
        newRide.max_passengers = 1
        newRide.num_passengers = 0
        newRide.driver = "Kevin"
        newRide.start_point_title = "Decorah, IA"
        newRide.start_point_long, newRide.start_point_lat = geocode(newRide.start_point_title)
        newRide.destination_title = "Des Moines, IA"
        newRide.destination_long, newRide.destination_lat = geocode(newRide.destination_title)
        newRide.ToD = datetime.datetime(2009,9,17)
        newRide.passengers = []
        newRide.put()
    
    
    
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/getrides', RideQueryHandler ),
                                          ("/newride", NewRideHandler),
                                          ],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
