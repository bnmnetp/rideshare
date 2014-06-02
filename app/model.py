from google.appengine.ext import db
from google.appengine.api import users
import logging

# Make this very flat to start with, then add references later...
class Ride(db.Model):
    passengers_max = db.IntegerProperty()
    passengers_total = db.IntegerProperty()
    driver = db.BooleanProperty()
    driver_name = db.StringProperty()
    origin_add = db.StringProperty()
    origin_lat = db.FloatProperty()
    origin_lng = db.FloatProperty()
    dest_add = db.StringProperty()
    dest_lat = db.FloatProperty()
    dest_lng = db.FloatProperty()
    date = db.DateProperty()
    time = db.StringProperty()
    passengers = db.ListProperty(db.Key)
    contact = db.StringProperty()
    details = db.StringProperty()
    circle = db.StringProperty()
    event = db.StringProperty()

    def to_dict(self):
        resp = {}
        for p in Ride._properties:
            resp[p] = str(getattr(self, p))
        resp['id'] = self.key().id()
        return resp


class Passenger(db.Model):
    name = db.StringProperty()
    # fullname = db.StringProperty()
    contact = db.StringProperty()
    add = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    ride = db.ReferenceProperty()
    
    """
    Check home page functionality regarding the search for passenger rides
    & list of passengers for driver rides
    
    Change method of display in entire project regarding passengers
    """

class Community(db.Model):
    name = db.StringProperty()
    address = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    # appId = db.StringProperty()
    # appSecret = db.StringProperty()

class Circle(db.Model):
    name = db.StringProperty()
    description = db.StringProperty()
    def to_dict(self):
        d = {}
        d['id'] = Circle.key().id()
        d['name'] = Circle.name
        d['description'] = Circle.description
        return d

class Event(db.Model):
    name = db.StringProperty()
    circle = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    date = db.DateProperty()
    address = db.StringProperty()
    time = db.StringProperty()
    creator = db.StringProperty()

    # def to_dict(self):
    #     res = {}
    #     res['ToD'] = str(self.ToD)
    #     res['name'] = str(self.name)
    #     res['lat'] = self.lat
    #     res['lng'] = self.lng
    #     res['id'] = str(self.key().id())
    #     res['address'] = str(self.address)
    #     res['circle']= self.circle
    #     res["time"] = self.time
    #     logging.debug(str(self.key().id()))
    #     return res
        
class ApplicationParameters(db.Model):
    apikey = db.StringProperty()
    notifyEmailAddr = db.StringProperty()
    fromEmailAddr = db.StringProperty()


class User(db.Model):
    id = db.StringProperty()
    auth_id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty()
    email = db.EmailProperty()
    circles = db.ListProperty(int)