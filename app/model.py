from google.appengine.ext import db
from google.appengine.api import users
import logging

class User(db.Model):
    auth_id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty()
    email = db.EmailProperty()
    phone = db.StringProperty()
    circles = db.ListProperty(db.Key)

    def to_dict(self):
        resp = {}
        for u in User._properties:
            resp[u] = str(getattr(self, u))
        resp['id'] = self.key().id()
        return resp

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
    circle = db.ReferenceProperty(Circle)
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    date = db.DateProperty()
    address = db.StringProperty()
    time = db.StringProperty()
    user = db.ReferenceProperty(User)
    details = db.TextProperty()

    def to_dict(self):
        resp = {}
        for p in Event._properties:
            resp[p] = str(getattr(self, p))
        resp['id'] = self.key().id()
        return resp

class Ride(db.Model):
    passengers_max = db.IntegerProperty()
    passengers_total = db.IntegerProperty()
    has_driver = db.BooleanProperty()
    driver = db.ReferenceProperty(User)
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
    event = db.ReferenceProperty(Event)

    def to_dict(self):
        resp = {}
        for p in Ride._properties:
            resp[p] = str(getattr(self, p))
        resp['id'] = self.key().id()
        if self.event != None: 
            resp['event'] = self.event.to_dict()
        return resp

class Comment(db.Model):
    user = db.ReferenceProperty(
        User,
        required = False,
        collection_name = 'user'
    )
    date = db.DateProperty()
    text = db.TextProperty()
    event = db.ReferenceProperty(Event)
    ride = db.ReferenceProperty(Ride)
    circle = db.ReferenceProperty(Circle)
    profile = db.ReferenceProperty(
        User,
        required = False,
        collection_name = 'profile'
    )

    def to_dict(self):
        resp = {}
        for p in Comment._properties:
            resp[p] = str(getattr(self, p))
        resp['id'] = self.key().id()
        if self.user:
            resp['user'] = self.user.to_dict()
        return resp

class Community(db.Model):
    name = db.StringProperty()
    address = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    # appId = db.StringProperty()
    # appSecret = db.StringProperty()
        
class ApplicationParameters(db.Model):
    apikey = db.StringProperty()
    notifyEmailAddr = db.StringProperty()
    fromEmailAddr = db.StringProperty()