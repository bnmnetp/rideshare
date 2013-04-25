from google.appengine.ext import db
from google.appengine.api import users
import logging
from google.appengine.dist import use_library
use_library('django', '1.2')
# Make this very flat to start with, then add references later...
class Ride(db.Model):
    max_passengers = db.IntegerProperty()
    num_passengers = db.IntegerProperty()
    driver = db.StringProperty()
    drivername = db.StringProperty()
    start_point_title = db.StringProperty()
    start_point_lat = db.FloatProperty()
    start_point_long = db.FloatProperty()
    destination_title = db.StringProperty()
    destination_lat = db.FloatProperty()
    destination_long = db.FloatProperty()
    ToD = db.DateProperty()
    part_of_day = db.StringProperty()
    time = db.StringProperty()
    passengers = db.ListProperty(db.Key)
    contact = db.StringProperty()
    comment = db.StringProperty()
    circle = db.StringProperty()
    event = db.StringProperty()

    def to_dict(self):
        res = {}
        for k in Ride._properties:   ## special case ToD
            if k != 'ToD' and k != 'driver' and k != 'passengers':
                res[k] = getattr(self,k) #eval('self.'+k)
        res['ToD'] = str(self.ToD)
        if self.driver:
            res['driver'] = self.driver
        else:
            res['driver'] = "needs driver"
        res['key'] = unicode(self.key())
        res['passengers'] = [str(p) for p in self.passengers]
        return res

class Passenger(db.Model):
    name = db.StringProperty()
    fullname = db.StringProperty()
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

class College(db.Model):
    name = db.StringProperty()
    address = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    appId= db.StringProperty()
    appSecret= db.StringProperty()

class Circle(db.Model):
    name = db.StringProperty()
    description = db.StringProperty()

class Event(db.Model):
    name = db.StringProperty()
    circle = db.StringProperty()
    lat = db.FloatProperty()
    lng= db.FloatProperty()
    ToD =db.DateProperty()
    address = db.StringProperty()
    time= db.StringProperty()
    creator = db.StringProperty()

    def to_dict(self):
        res = {}
        res['ToD'] = str(self.ToD)
        res['name'] = str(self.name)
        res['lat'] = self.lat
        res['lng'] = self.lng
        res['id'] = str(self.key().id())
        res['address'] = str(self.address)
        res['circle']= self.circle
        res["time"] = self.time
        logging.debug(str(self.key().id()))
        return res
        
class ApplicationParameters(db.Model):
    apikey = db.StringProperty()
    notifyEmailAddr = db.StringProperty()
    fromEmailAddr = db.StringProperty()    
    
