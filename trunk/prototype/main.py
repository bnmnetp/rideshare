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
#from appengine_django.models import BaseModel
from google.appengine.ext import db
from google.appengine.api import users

import logging
import urllib

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
        self.response.out.write('Hello World!')


class RideQueryHandler(webapp.RequestHandler):
    """
    Parse and process requests for rides
    returns json
    """

    def get(self):
        """
        Arguments:
        - `self`:

        The query may be filtered by start date, end date
        """
        allRides = Ride.all()
        after_date = self.request.get('after')
        before_date = self.request.get("before")
        if after_date:
            y,m,d = after_date.split('-')
            allRides.filter('ToD >= ',datetime.datetime(int(y),int(m),int(d)))

        if before_date:
            y,m,d = before_date.split("-")
            allRides.filter('ToD <=',datetime.datetime(int(y),int(m),int(d)))
        

        logging.debug("after %s before %s", after_date, before_date)


        json = simplejson.dumps([r.to_dict() for r in allRides])
        self.response.headers.add_header('content-type','application/json')
        self.response.out.write(json)
        logging.debug('end get')
    
        


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    # prepopulate the database
    query = db.Query(Ride)
    # TODO:  use google python geocoder to lookup lat/long for start/dest    
    if query.count() < 2:
        newRide = Ride()
        newRide.max_passengers = 3
        newRide.num_passengers = 0
        newRide.driver = "Brad"
        newRide.start_point_title = "Decorah, IA"
        newRide.destination_title = "Plymouth, MN"
        newRide.ToD = datetime.datetime(2009,9,15)
        newRide.passengers = []
        newRide.put()

        newRide = Ride()
        newRide.max_passengers = 1
        newRide.num_passengers = 0
        newRide.driver = "Kevin"
        newRide.start_point_title = "Decorah, IA"
        newRide.destination_title = "Des Moines, IA"
        newRide.ToD = datetime.datetime(2009,9,17)
        newRide.passengers = []
        newRide.put()
    
    
    
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/getrides', RideQueryHandler )],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
