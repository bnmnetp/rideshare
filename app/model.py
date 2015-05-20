from google.appengine.ext import db, blobstore
from google.appengine.api import users

class User(db.Model):
    auth_id = db.StringProperty()
    email_account = db.EmailProperty()
    password = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(default='')
    email = db.StringProperty(default='')
    phone = db.StringProperty(default='')
    circles = db.ListProperty(db.Key)
    photo = db.StringProperty()
    zip = db.IntegerProperty()
    noti_time = db.IntegerProperty()
    noti_type = db.StringProperty()
    notis = db.ListProperty(db.Key)
    email_pref = db.ListProperty(str)

    reset = db.StringProperty()

    address = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()

    def to_dict(self):
        resp = {}
        for u in User._properties:
            resp[u] = str(getattr(self, u))
        resp['id'] = self.key().id()
        return resp

    @property
    def name_x(self):
        if self.name:
            return self.name
        elif self.email:
            return self.email
        else:
            return 'User #' + str(self.key().id())

class Circle(db.Model):
    name = db.StringProperty()
    description = db.StringProperty()
    privacy = db.StringProperty()
    color = db.StringProperty()
    admins = db.ListProperty(db.Key)
    permission = db.StringProperty()
    requests = db.ListProperty(db.Key)
    zip = db.IntegerProperty()

    address = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()

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
    details = db.TextProperty()
    creator = db.ReferenceProperty(User)
    location = db.TextProperty()

    def to_dict(self):
        resp = {}
        for p in Event._properties:
            resp[p] = str(getattr(self, p))
        resp['id'] = self.key().id()
        return resp

class Ride(db.Model):
    creator = db.ReferenceProperty(
        User,
        required = False,
        collection_name = 'creator'
    )
    passengers_max = db.IntegerProperty()
    driver = db.ReferenceProperty(
        User,
        required = False,
        collection_name = 'driver'
    )
    driven_by = db.StringProperty()
    origin_add = db.StringProperty()
    origin_lat = db.FloatProperty()
    origin_lng = db.FloatProperty()
    dest_add = db.StringProperty()
    dest_lat = db.FloatProperty()
    dest_lng = db.FloatProperty()
    date = db.DateProperty()
    time = db.StringProperty()
    details = db.StringProperty()
    circle = db.ReferenceProperty(Circle)
    event = db.ReferenceProperty(Event)
    recurring = db.StringProperty()

    # @property
    # def orig(self):

    # @property
    # def dest(self):

    @property
    def date_picker(self):
        return self.date.strftime("%d/%m/%Y")
    
    @property
    def date_str(self):
        return self.date.strftime('%B %dth, %Y')

    def to_dict(self):
        resp = {}
        for p in Ride._properties:
            resp[p] = str(getattr(self, p))
        resp['id'] = self.key().id()
        if self.event != None: 
            resp['event'] = self.event.to_dict()
        return resp

    def is_passenger(self, user_key):
        passenger = Passenger.all().filter('ride =', self.key()).filter('user =', user_key).get()
        if passenger != None:
            return True
        else:
            return False

    @property
    def passengers(self):
        passengers = Passenger.all().filter('ride =', self.key()).fetch(None)
        return passengers

    @property
    def passengers_total(self):
        passengers = self.passengers
        total = 0
        for p in passengers:
            total += p.seats
        return total

class Requester(db.Model):
    user = db.ReferenceProperty(User)
    seats = db.IntegerProperty()
    event = db.ReferenceProperty(Event)        

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

class Notification(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    read = db.BooleanProperty()
    type = db.StringProperty()
    user = db.ReferenceProperty(User)
    ride = db.ReferenceProperty(Ride)
    circle = db.ReferenceProperty(Circle)
    text = db.TextProperty()

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

class Noti(db.Model):
    relation = db.Key()
    user = db.ReferenceProperty(User)
    type = db.StringProperty()
    status = db.StringProperty() # new, view, ack

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

class Passenger(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    ride = db.ReferenceProperty(Ride)
    user = db.ReferenceProperty(User)
    seats = db.IntegerProperty()
    message = db.TextProperty()

class Messages(db.Model):
    sent = db.DateTimeProperty(auto_now_add=True)
    circle = db.ReferenceProperty(Circle)
    sender = db.ReferenceProperty(User)
    message = db.TextProperty()

class Org(db.Model):
    name = db.StringProperty()
    email = db.StringProperty()
    slug = db.StringProperty()
    circle = db.ReferenceProperty(Circle)