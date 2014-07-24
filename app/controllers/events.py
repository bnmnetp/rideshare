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

        event.date_str = event.date.strftime('%B %dth, %Y')

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

class JoinEvent(BaseHandler):
    def post(self, event_id):
        self.auth()

        user = self.current_user()

        event = Event.get_by_id(int(circle_id))

        if not circle:
            self.redirect('/')
            return None

        json_str = self.request.body
        data = json.loads(json_str)

        if data['type'] == 'join':
            message = 'Joined the event.'
            if user.key() not in event.attending:
                event.attending.append(user.key())
        elif data['type'] == 'leave':
            message = 'Left the event.'
            if user.key() in event.attending:
                event.attending.remove(user.key())

        event.put()

        self.response.write(json.dumps({
            'message': message
        }))

class EventHandler(BaseHandler):
    def get(self):
        self.auth()

        user = self.current_user()

        today = date.today()

        events_user = Event.all().filter('circle IN', user.circles).filter('date >=', today).fetch(100)

        events_all = Event.all().filter('date >=', today).fetch(100)

        doRender(self, 'events.html', {
            'events_user': events_user,
            'events_all': events_all,
            'user': user
        })

    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        events = Event.all()

        today = date.today()
        events.filter('date >=', today)

        if data['circle'] != '':
            events.filter('circle = ',  data['circle'])

        self.response.write(json.dumps([e.to_dict() for e in events]))

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

        if data['circle'] != '':
            circle = Circle.get_by_id(int(data['circle']))
            if circle:
                event.circle = circle.key()
        else:
            event.circle = None

        event.put()
        response = {
            'message': 'Event added!'
        }
        self.response.write(json.dumps(response))