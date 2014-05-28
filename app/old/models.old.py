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