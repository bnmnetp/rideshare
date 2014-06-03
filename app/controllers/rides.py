from app.common.toolbox import doRender
from app.model import *
from google.appengine.ext import db
import datetime
from datetime import date
import json
from app.base_handler import BaseHandler

class RideHandler(BaseHandler):
    def get(self):
        self.auth()

        doRender(self, 'rides.html', {})
    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        rides = Ride.all()

        if data['circle']:
            rides.filter('circle = ', data['circle'])

        results = json.dumps([r.to_dict() for r in rides])
        self.response.write(results)

class RideJoinHandler(BaseHandler):
    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        ride = Ride.get_by_id(int(data['id']))

        if ride:
            # Possible input for data['type']: ['passenger', 'driver']
            if data['type'] == 'passenger':
                passenger = Passenger()
                passenger.name = "Replace"
                passenger.contact = "Replace"
                passenger.add = ride.origin_add
                passenger.lat = ride.origin_lat
                passenger.lng = ride.origin_lng
                pass_key = passenger.put()
                ride.passengers.append(pass_key)
            elif data['type'] == 'driver':
                ride.passengers_max = 1
                ride.passengers_total = 0
                ride.driver = True
                # Replace
                ride.driver_name = "Replace"
                ride.contact = "Replace"

            ride.put()

            if ride.driver != True:
                passenger.ride = ride_key
                passenger.put()

            response = {
                'message': 'Ride added'
            }
            self.response.write(json.dumps(response))

        else:
            self.response.status_int(500)
            response = {
                'message': 'Ride not found!',
                'error': True
            }
            self.response.write(json.dumps(response))


class RideQueryHandler(BaseHandler):
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
        logger = logging.getLogger('MySite')
        logger.info(str(self.request))
        # Create a query object
        allRides = Ride.all()
        # Check to see if the browser side provided us with before/after dates
        after_date = self.request.get('after')
        before_date = self.request.get("before")
        # If there is an after date then limit the rides to those after the date
        # using the filter method
        if after_date:
            y,m,d = after_date.split('-')
            allRides.filter('ToD >= ',datetime.date(int(y),int(m),int(d)))


        if before_date:
            y,m,d = before_date.split("-")
            allRides.filter('ToD <=',datetime.date(int(y),int(m),int(d)))
        logging.debug(self.request.get("circle"))
        allRides.filter('circle =',self.request.get("circle"))
        logging.debug("after %s before %s", after_date, before_date)
    
        if self.request.get("event"):
            allRides.filter('event =',self.request.get("event"))
        else:
            allRides.filter('event =',None)
        # Now put together the json result to send back to the browser.
        json = simplejson.dumps([r.to_dict() for r in allRides])
        self.response.headers.add_header('content-type','application/json')
        self.response.out.write(json)
        logging.debug('end get')
    
class NewRideHandler(BaseHandler):
    def post(self):
        ride = Ride()
        
        json_str = self.request.body
        data = json.loads(json_str)

        # Creates date object from Month/Day/Year format
        d_arr = data['date'].split('/')
        d_obj = datetime.date(int(d_arr[2]), int(d_arr[1]), int(d_arr[0]))

        # Refer to model.py for structure of data
        # class Ride
        ride.origin_add = data['origin']['address']
        ride.origin_lat = data['origin']['lat']
        ride.origin_lng = data['origin']['lng']
        ride.dest_add = data['destination']['address']
        ride.dest_lat = data['destination']['lat']
        ride.dest_lng = data['destination']['lng']
        ride.date = d_obj
        ride.time = data['time']
        ride.passengers = []

        if data['driver'] == True:
            ride.passengers_max = int(data['max_passengers'])
            ride.passengers_total = 0
            ride.driver = data['driver']
            ride.driver_name = "Replace"
            ride.contact = "Replace"
        else:
            passenger = Passenger()
            passenger.name = "Replace"
            passenger.contact = "Replace"
            passenger.add = data['origin']['address']
            passenger.lat = data['origin']['lat']
            passenger.lng = data['origin']['lng']
            pass_key = passenger.put()
            ride.passengers.append(pass_key)

        ride.circle = ""
        ride.event = ""

        ride_key = ride.put()
        if data['driver'] != True:
            passenger.ride = ride_key
            passenger.put()

        # self.send_email()
        response = {
            'message': 'Ride added!'
        }
        self.response.write(json.dumps(response))
        

    def sendRideEmail(self,ride):
      
        driverName = None
        passengerName = None
        subject = "New Ride "
        if ride.driver:
            if self.current_user.loginType == "google":
               to = self.current_user.email
               logging.debug(to)
            driverName = self.current_user.nickname()
        else:
            p = db.get(ride.passengers[0])
            logging.debug(p)
            #if self.current_user.loginType == "google":
               #to = p.email
            passengerName = self.current_user.nickname()
            
        sender = FROM_EMAIL_ADDR
        announceAddr = NOTIFY_EMAIL_ADDR
        if driverName:
            subject += "Announcement"
            body = """
A new ride is being offered.  %s is offering a ride from %s to %s on %s.
Please go to %s if you want to join this ride.

Thanks,

The Rideshare Team
""" % (driverName,ride.start_point_title,ride.destination_title,ride.ToD,rideshareWebsite)
        else:
            subject += "Request"
            body = """
A new ride request has been posted.  %s is looking for a ride from %s to %s on %s.
If you are able to take this person in your car, please go to %s
        
Thanks,

The Rideshare Team
""" % (passengerName,ride.start_point_title,ride.destination_title,ride.ToD,rideshareWebsite)

        if self.current_user.loginType == "facebook":
          logging.debug(self.current_user.access_token)
          graph = facebook.GraphAPI(self.current_user.access_token)
          graph.put_object("me", "feed", message=body)
          #pageGraph = facebook.GraphAPI("AAAECeZAfUaeoBAHYuYZC8NN9djZAlA6PZBpJnCWvZCxZBnDeEWQcdj3YuBZCWEJbPZA1E35QiCHqYmCxXsNkqT82tn67nMitdirfjxvZBAZBCfWzRKbCFZAHFZCH")
          #pageGraph.put_object("144494142268497","feed",message=body)

class AddPassengerHandler(BaseHandler): 
    """
    Handles addition of passengers
    """
    def get(self):
      """
      Called when adding a passenger to a ride
      
      Arguments:
      - 'self'
      
      Web Arguments:
      - user_name
      - ride_key
      """
      # The current user can add himself to the ride.  No need for this in the form.
      aquery = db.Query(College)
      mycollege= aquery.get()
      user_name = self.current_user.id
      
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
        if db.get(p).name== user_name:
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
        passenger.fullname = FBUser.get_by_key_name(user_name).nickname()
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
        query.filter("ToD > ", datetime.date.today())
        ride_list = query.fetch(limit=100)
        user = self.current_user
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = 'You have been added to %s ride.' % (ride.driver)
        self.sendDriverEmail(ride)
        path = os.path.join(os.path.dirname(__file__), 'templates/map.html')
        self.response.out.write(template.render(path, {
            'ride_list': ride_list, 
            'greeting': greeting,
            'message': message,
            'mapkey':MAP_APIKEY, 
            'college':mycollege           
            }))

    def sendDriverEmail(self,ride):
        logging.debug(ride.driver)
        driver = FBUser.get_by_key_name(ride.driver)
        logging.debug(driver)
        if not ride.driver:
            return
        if driver.loginType == "google":
           to = driver
        else:
           logging.debug(ride.driver)
           to = FBUser.get_by_key_name(ride.driver)
           logging.debug(to)
        sender = FROM_EMAIL_ADDR
        subject = "New Passenger for your ride"
        p = db.get(ride.passengers[-1])
        user = FBUser.get_by_key_name(p.name)
        body = """
Dear %s,
We wanted to let you know that %s has been added to your ride
from %s to %s on %s.  If you need to contact %s you can do so at %s.

Thanks for being a driver!

Sincerely,

The Rideshare Team
""" % (to.nickname(), user.nickname(), ride.start_point_title, ride.destination_title,
       ride.ToD, user.nickname(), p.contact)

        if driver.loginType == "google":
          logging.debug(body)
          mail.send_mail(sender,to.email,subject,body)
        else:
          graph = facebook.GraphAPI(to.access_token)
          logging.debug(graph)
          graph.put_object("me", "feed", message=body)

class AddDriverHandler(BaseHandler):

    def get(self):
        ride_key = self.request.get("key")
        contact = self.request.get("contact")
        numpass = self.request.get("numpass")
        user = self.current_user
        
        ride = Ride.get(ride_key)
        ride.driver = user.id
        ride.drivername = FBUser.get_by_key_name(user.id).nickname()
        ride.contact = contact
        ride.max_passengers = int(numpass)
        ride.put()

        for p in ride.passengers:
            logger = logging.getLogger('MySite')
            logger.info(str(p))
            passenger = Passenger.get(p)
            if passenger.loginType =="google":
              self.sendRiderEmail(ride,passenger.email,"google")
            elif passenger.loginType=="facebook":
              self.sendRiderEmail(ride, passenger.name, "facebook")

        self.response.out.write("OK")

    def sendRiderEmail(self, ride, to,loginType):

        if loginType == "facebook":
           to = FBUser.get_by_key_name(to)
           user = self.current_user
           logging.debug(to)

        sender = FROM_EMAIL_ADDR
        subject = "Change in your ride"
        
        body = """
Dear %s,

We have good news about your request for a ride from %s to %s on %s.
%s has agreed to drive.  You can contact the driver at %s.

Have a safe trip!

Sincerely,

The Rideshare Team
""" % (to.nickname(),  ride.start_point_title, ride.destination_title, ride.ToD,
       user.nickname(), ride.contact)
        if loginType == "google": 
           logging.debug(body)
           mail.send_mail(sender,to,subject,body)
        else:
           graph = facebook.GraphAPI(to.access_token)
           graph.put_object("me", "feed", message=body)

class EditRideHandler(BaseHandler):
    def get(self):
        aquery = db.Query(College)
        mycollege= aquery.get()
        ride_key = self.request.get("key")
        ride = db.get(ride_key)
        username = self.current_user.id
        dayparts = ride.part_of_day.split()
        
        plist = []
        for p in ride.passengers:
            logging.debug(db.get(p).name)
            plist.append(db.get(p).name)
        
        doRender(self, 'edit.html', { 
                          'user': username,
                          'ride': ride,
                          'earlylate' : dayparts[0],
                          'mae' : dayparts[1],
                          'plist': plist,
                          'college':mycollege
                                         }
                 )

class ChangeRideHandler(BaseHandler):
    def post(self):
        aquery = db.Query(College)
        mycollege= aquery.get()
        user = self.current_user
        username = user.id
        ride = Ride.get(self.request.get("key"))

        contact = self.request.get("contact")
        comment = self.request.get("ridecomment")
        partofday = self.request.get("partofday")
        earlylate = self.request.get("earlylate")
        maxp = self.request.get("numpass")

        pofd = early_late_strings[earlylate] + " " + part_of_day_strings[partofday]

        ride.part_of_day = pofd
        ride.contact = contact
        ride.comment = comment
        ride.max_passengers = int(maxp)

        ride.put()
        self.redirect("/")

class RideInfoHandler(BaseHandler):
    """
    Displays detailed information regarding a specific ride
    Holds a GMap detailing the trip
    """
    def get(self):
      aquery = db.Query(College)
      mycollege= aquery.get()
      username = self.current_user
      key = self.request.get('key')
      ride = db.get(key)
      if ride == None:
        doRender(self, 'error.html', {
                              'error_message': "No such ride exists.","college":mycollege})
      else:
        ride.passengerobjects = []
        ride.jsmonth = ride.ToD.month
        ride.jsyear = ride.ToD.year
        ride.jsday = ride.ToD.day
        if ride.start_point_title == mycollege.name:
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
            'ride': ride,
            'mapkey':MAP_APIKEY,
            'college': mycollege
            })

class DeleteRideHandler(BaseHandler): #NEEDS WORK
    """
    Deletes a ride using a key
    """
    def get(self):
        key = self.request.get('key')
        ride = db.get(key)
        if ride == None:
            doRender(self, 'error.html', {
                              'error_message': "No such ride exists."})
        elif ride.num_passengers == 0:
            db.delete(ride)

        else:
            ride.driver = None
            ride.put()
            for p in ride.passengers:
              passenger = Passenger.get(p)
              passenger = FBUser.get_by_key_name(p.name)
              if passenger.loginType =="google":
                self.sendRiderEmail(ride,passenger.email,"google")
              elif passenger.loginType=="facebook":
                self.sendRiderEmail(ride, passenger.name, "facebook")

            
        user = self.current_user
        aquery = db.Query(College)
        mycollege= aquery.get()
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = 'Your ride has been deleted.'
        path = os.path.join(os.path.dirname(__file__), 'templates/map.html')
        self.response.out.write(template.render(path, {
            'greeting' : greeting,
            'message' : message,
            'mapkey':MAP_APIKEY, 
            'college': mycollege,
            'nick' : user.nickname()        
            }))

    def sendRiderEmail(self, ride, to, loginType):
        
        if loginType == "facebook":
            to = FBUser.get_by_key_name(to)
            logging.debug(to)
        sender = FROM_EMAIL_ADDR
        subject = "Change in your ride"
        
        body = """
        Dear %s,

        We wanted to let you know that there has been a change in status of your ride
        from %s to %s on %s.  Unfortunately the driver is unable to drive anymore.
        The ride will remain, but it will appear as a ride
        that is in need of a driver.  When a new driver is found you will be notified
        by email.


        Sincerely,

        The Rideshare Team
        """ % (to.nickname(),  ride.start_point_title, ride.destination_title, ride.ToD)
        if loginType == "google":
            mail.send_mail(sender,to,subject,body)
        else:
            try:
                graph = facebook.GraphAPI(to.access_token)
                graph.put_object("me", "feed", message=body)

            except:
               logging.debug(graph.put_object("me", "feed", message=body))