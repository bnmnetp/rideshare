from app.common.toolbox import doRender, split_address
from google.appengine.ext import db
from app.model import *
from google.appengine.api import mail
import datetime
from datetime import date
import json
from app.base_handler import BaseHandler

class GetEventHandler(BaseHandler):
    def get(self, id):
        self.auth()

        user = self.current_user()

        event = Event.get_by_id(int(id))

        rides = Ride.all().filter('event = ', event.key()).fetch(100)

        for ride in rides:
            ride.orig = split_address(ride.origin_add)
            ride.dest = split_address(ride.dest_add)
            if user.key() == ride.driver.key():
                ride.is_driver = True
            else:
                ride.is_driver = False
            if user.key() in ride.passengers:
                ride.is_passenger = True
            else:
                ride.is_passenger = False

        comments = Comment.all().filter('event = ', event.key()).order('-date')

        doRender(self, 'view_event.html', {
            'event': event,
            'rides': rides,
            'comments': comments,
            'user': user
        })

class EventHandler(BaseHandler):
    def get(self):
        self.auth()

        user = self.current_user()

        events_user = Event.all().filter('circle IN', user.circles).fetch(100)

        events_all = Event.all().fetch(100)

        doRender(self, 'events.html', {
            'events_user': events_user,
            'events_all': events_all,
            'user': user
        })

    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        events = Event.all()

        if data['circle'] != '':
            events.filter('circle = ',  data['circle'])

        self.response.write(json.dumps([e.to_dict() for e in events]));

class EventQueryHandler(BaseHandler):
    """
    Parse and process requests for events
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
        allEvents = Event.all()

        # Check to see if the browser side provided us with before/after dates
        after_date = self.request.get('after')
        before_date = self.request.get("before")
        # If there is an after date then limit the rides to those after the date
        # using the filter method
        if after_date:
            y,m,d = after_date.split('-')
            allEvents.filter('ToD >= ',datetime.date(int(y),int(m),int(d)))


        if before_date:
            y,m,d = before_date.split("-")
            allEvents.filter('ToD <=',datetime.date(int(y),int(m),int(d)))
        logging.debug(self.request.get("circle"))
        allEvents.filter('circle =',self.request.get("circle"))
        logging.debug("after %s before %s", after_date, before_date) 

        # Now put together the json result to send back to the browser.
        json = simplejson.dumps([e.to_dict() for e in allEvents])
        self.response.headers.add_header('content-type','application/json')
        self.response.out.write(json)
        logging.debug('end get')


class NewEventHandler(BaseHandler):
    def post(self):
        event = Event()

        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        # Creates date object from Month/Day/Year format
        d_arr = data['date'].split('/')
        d_obj = datetime.date(int(d_arr[2]), int(d_arr[0]), int(d_arr[1]))

        # Refer to model.py for structure of data
        # class Event
        event.name = data['name']
        event.lat = data['lat']
        event.lng = data['lng']
        event.address = data['address']
        event.date = d_obj
        event.time = data['time']
        event.details = data['details']
        event.user = user.key()

        if 'circle' in data:
            circle = Circle.get_by_id(data['circle'])
            if circle:
                event.circle = circle.key()
        else:
            event.circle = None

        event.put()
        response = {
            'message': 'Event added!'
        }
        self.response.write(json.dumps(response))

class NewEventRideHandler(BaseHandler):
    """
    For new Event Rides
    """

    def get(self):

        user = self.current_user
        newRide = Ride()
        maxp = self.request.get("maxp")
        inumber = self.request.get("contact")
        if not "-" in inumber:
            number = inumber[0:3]+'-'+inumber[3:6]+'-'+inumber[6:]
        else:
            number = inumber
        newRide.contact = number

        isDriver = self.request.get("isDriver")
        if isDriver.lower() == "false":
            isDriver = False
        else:
            isDriver = True
        
        aquery = db.Query(College)
        mycollege= aquery.get()


        lat = float(self.request.get("lat")) * (random.random() * (1.000001-.999999) + 1.000001)
        lng = float(self.request.get("lng")) * (random.random() * (1.000001-.999999) + 1.000001)
        checked = self.request.get("toLuther")
        if checked == 'true':
            newRide.start_point_title = self.request.get("from")
            newRide.start_point_lat = lat
            newRide.start_point_long = lng
            newRide.destination_title = mycollege.name
            newRide.destination_lat = mycollege.lat
            newRide.destination_long = mycollege.lng
        elif checked == 'false':
            newRide.start_point_title = mycollege.name
            newRide.start_point_lat = mycollege.lat
            newRide.start_point_long = mycollege.lng
            newRide.destination_title = self.request.get("to")
            newRide.destination_lat = lat
            newRide.destination_long = lng             
        y = int(self.request.get("year"))
        m = int(self.request.get("month"))
        d = int(self.request.get("day"))
        time = self.request.get("time")
        early_late_value = int(self.request.get("earlylate"))

        part_of_day = ''
        newRide.event = self.request.get("eventId")
        newRide.time = time
        newRide.part_of_day = part_of_day
        logger = logging.getLogger('MySite')
        logger.info(str(m))
        newRide.ToD = datetime.date(int(y),int(m),int(d))

        newRide.max_passengers = int(maxp)
        newRide.num_passengers = 0
        newRide.passengers = []

        if isDriver:
            newRide.driver = user.id
            newRide.drivername = FBUser.get_by_key_name(user.id).nickname()
        else:
            user_name = user.id
            passenger = Passenger()
            passenger.name = user_name
            passenger.fullname = FBUser.get_by_key_name(user.id).nickname()
            logging.debug(FBUser.get_by_key_name(user.id).nickname())
            passenger.contact = number
            passenger.location = newRide.destination_title
            passenger.lat = lat
            passenger.lng = lng
            pass_key = passenger.put()
            newRide.passengers.append(pass_key)
            newRide.num_passengers = 1

        newRide.comment = self.request.get("comment")
        newRide.circle = self.request.get("circleType")
        ride_key = newRide.put()
        
        if not isDriver:
            passenger.ride = ride_key
            passenger.put()

        query = db.Query(Ride)
        query.filter("ToD > ", datetime.date.today())
        query.filter("circle = ",self.request.get("circle"))
        ride_list = query.fetch(limit=100)
        self.sendRideEmail(newRide)
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = 'Your ride has been created!'
        path = os.path.join(os.path.dirname(__file__), 'templates/map.html')
        self.response.out.write(str(template.render(path, {
            'ride_list': ride_list, 
            'greeting': greeting,
            'message': message,
            'mapkey' : MAP_APIKEY,
            })))

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

class AddEventsHandler(BaseHandler):
    def get(self):
        community = db.Query(Community).get()
        circle = self.request.get("circle")
        doRender(self, "addevents.html", {
            "circle": circle,
            "community": community
        })

class AddMultipleEventsHandler(BaseHandler):
    def post(self):
        logger = logging.getLogger('MySite')
        locations = self.request.str_params.getall("eventlocation")
        names = self.request.str_params.getall("eventname")
        dates = self.request.str_params.getall("eventdate")
        times = self.request.str_params.getall("eventtime")
        circle = self.request.get("circle")
        for i in range(len(locations)):
            if len(locations[i])>0:
                result = Geocoder.geocode(str(locations[i]))[0]
                logger.info(circle)
                if result:
                    newEvent = Event()
                    newEvent.creator = self.current_user.id
                    newEvent.name = names[i]
                    newEvent.lat = result.coordinates[0]
                    newEvent.lng = result.coordinates[1]
                    newEvent.address = locations[i]
                    newEvent.circle = circle
                    newEvent.time = times[i]
                    date = dates[i]
                    newEvent.ToD = datetime.date(int(date[6:]),int(date[0:2]),int(date[3:5]))
                    newEvent.put()
            
            
        self.redirect("/main")