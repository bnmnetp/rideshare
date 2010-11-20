from google.appengine.ext import db
from google.appengine.api import users


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
            if k != 'ToD' and k != 'driver':
                res[k] = getattr(self,k) #eval('self.'+k)
        res['ToD'] = str(self.ToD)
        res['email'] = self.driver.email()
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

class ApplicationParameters(db.Model):
    apikey = db.StringProperty()
