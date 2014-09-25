from app.common import toolbox
from google.appengine.ext import db
from app.model import *
from google.appengine.api import mail
import datetime
from datetime import date
import json
from app.base_handler import BaseHandler
from app.common.voluptuous import *

class GetEventHandler(BaseHandler):
    def get(self, id):
        self.auth()

        user = self.current_user()

        event = Event.get_by_id(int(id))

        event.date_str = event.date.strftime('%B %dth, %Y')

        offered = Ride.all().filter('event = ', event.key()).filter('driver != ', None).fetch(None)
        requested = Ride.all().filter('event = ', event.key()).filter('driver = ', None).fetch(None)

        for ride in offered:
            ride.orig = toolbox.format_address(ride.origin_add)
            ride.dest = toolbox.format_address(ride.dest_add)
            if ride.driver and user.key() == ride.driver.key():
                ride.is_driver = True
            else:
                ride.is_driver = False
            if user.key() in ride.passengers:
                ride.is_passenger = True
            else:
                ride.is_passenger = False

            ride.seats_availible = ride.passengers_max - ride.passengers_total

        for ride in requested:
            ride.orig = toolbox.format_address(ride.origin_add)
            ride.dest = toolbox.format_address(ride.dest_add)
            if ride.driver and user.key() == ride.driver.key():
                ride.is_driver = True
            else:
                ride.is_driver = False
            if user.key() in ride.passengers:
                ride.is_passenger = True
            else:
                ride.is_passenger = False


        toolbox.render(self, 'view_event.html', {
            'event': event,
            'offered': offered,
            'requested': requested,
            'user': user,
            'circle': self.circle()
        })

class EventHandler(BaseHandler):
    def get(self):
        self.auth()

        user = self.current_user()

        today = date.today()

        circle = self.circle()

        events_all = Event.all().filter('circle =', circle).filter('date >=', today).fetch(None)

        toolbox.render(self, 'events.html', {
            'events_all': events_all,
            'user': user,
            'circle': circle
        })

    def post(self):
        self.auth()

        json_str = self.request.body
        data = json.loads(json_str)

        events = Event.all()

        today = date.today()
        events.filter('date >=', today)

        if data['circle'] != False:
            circle = Circle.get_by_id(int(data['circle']))
            events.filter('circle = ',  circle.key())

        self.response.write(json.dumps([e.to_dict() for e in events]))

class NewEventHandler(BaseHandler):
    def post(self):
        self.auth()
        event = Event()

        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        event_validator = Schema({
            Required('name'): unicode,
            Required('lat'): float,
            Required('lng'): float,
            Required('address'): unicode,
            Required('date'): toolbox.create_date(),
            'time': unicode,
            'details': unicode
        }, extra = True)

        try:
            data = event_validator(data)
        except MultipleInvalid as e:
            print str(e)
            return self.json_resp(500, {
                'error': True,
                'message': 'Invalid data'
            })

        # Refer to model.py for structure of data
        # class Event
        event.name = data['name']
        event.lat = data['lat']
        event.lng = data['lng']
        event.address = data['address']
        event.date = data['date']
        event.time = data['time']
        event.details = data['details']
        event.creator = user.key()
        event.user = user.key()

        if data['circle']:
            circle = Circle.get_by_id(int(data['circle']))
            if circle:
                event.circle = circle.key()
        else:
            event.circle = None

        event.put()
        response = {
            'message': 'Event added!',
            'id': event.key().id()
        }
        self.response.write(json.dumps(response))

class EditEvent(BaseHandler):
    def get(self, event_id):
        self.auth()

        user = self.current_user()

        event = Event.get_by_id(int(event_id))

        properties = ['name', 'date', 'time', 'details', 'address', 'lat', 'lng']

        event_json = toolbox.grab_json(event, properties)

        event_json['date'] = toolbox.date_picker(event.date)

        toolbox.render(self, 'edit_event.html', {
            'event': event,
            'event_json': event_json,
            'user': user
        })
    def post(self, event_id):
        self.auth()

        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        event = Event.get_by_id(int(event_id))

        event.name = data['name']
        event.data = data['date']
        event.time = data['time']
        event.details = data['details']
        event.address = data['address']
        event.lat = data['lat']
        event.lng = data['lng']
        event.put()

        self.json_resp(200, {
            'message': 'Event edited',
            'id': event.key().id()
        })

class DeleteEvent(BaseHandler):
    def post(self, event_id):
        self.auth()

        user = self.current_user()

        event = Event.get_by_id(int(event_id))

        json_str = self.request.body
        data = json.loads(json_str)

        event_validator = Schema({
            Required('name'): unicode,
            Required('lat'): float,
            Required('lng'): float,
            Required('address'): unicode,
            Required('date'): toolbox.create_date(),
            'time': unicode,
            'details': unicode
        }, extra = True)

        try:
            data = event_validator(data)
        except MultipleInvalid as e:
            print str(e)
            return self.json_resp(500, {
                'error': True,
                'message': 'Invalid data'
            })
