from google.appengine.ext import db, blobstore
from google.appengine.api import users

class User(db.Model):
    auth_id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(default='')
    email = db.EmailProperty()
    phone = db.StringProperty(default='')
    circles = db.ListProperty(db.Key)
    photo = db.StringProperty()
    noti_time = db.IntegerProperty()
    noti_type = db.StringProperty()

    def to_dict(self):
        resp = {}
        for u in User._properties:
            resp[u] = str(getattr(self, u))
        resp['id'] = self.key().id()
        return resp

class Circle(db.Model):
    name = db.StringProperty()
    description = db.StringProperty()
    privacy = db.StringProperty()
    color = db.StringProperty()
    admins = db.ListProperty(db.Key)
    def to_dict(self):
        d = {}
        d['id'] = Circle.key().id()
        d['name'] = Circle.name
        d['description'] = Circle.description
        d['privacy'] = Circle.privacy
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
    attending = db.ListProperty(db.Key)

    def to_dict(self):
        resp = {}
        for p in Event._properties:
            resp[p] = str(getattr(self, p))
        resp['id'] = self.key().id()
        return resp

class Ride(db.Model):
    passengers_max = db.IntegerProperty()
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
    details = db.StringProperty()
    circle = db.ReferenceProperty(Circle)
    event = db.ReferenceProperty(Event)
    recurring = db.StringProperty()

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

class Notification(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    read = db.BooleanProperty()
    text = db.TextProperty()
    user = db.ReferenceProperty(User)
    ride = db.ReferenceProperty(Ride)

    def to_dict(self):
        resp = {}
        for n in Notification._properties:
            resp[n] = str(getattr(self, n))
        resp['id'] = self.key().id()
        if self.user:
            resp['user'] = self.user.to_dict()
        if self.ride:
            resp['ride'] = self.ride.to_dict()
        return resp

class Invite(db.Model):
    circle = db.ReferenceProperty(Circle)
    email = db.StringProperty()
    user = db.ReferenceProperty(
        User,
        required = False,
        collection_name = 'to_user'
    )
    sender = db.ReferenceProperty(
        User,
        required = False,
        collection_name = 'from_user'
    )

class ApplicationParameters(db.Model):
    apikey = db.StringProperty()
    notifyEmailAddr = db.StringProperty()
    fromEmailAddr = db.StringProperty()