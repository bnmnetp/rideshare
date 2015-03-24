from app.common import toolbox
from google.appengine.ext import db
from app.model import *
from google.appengine.api import mail
import datetime
from datetime import date
import json
from app.base_handler import BaseHandler
from app.common.voluptuous import *
from app.common.email_sys import sender

class GetEventHandler(BaseHandler):
    def get(self, id):
        self.auth()

        user = self.current_user()

        event = Event.get_by_id(int(id))

        event.date_str = event.date.strftime('%B %dth, %Y')
        event.date_picker = event.date.strftime("%m/%d/%Y")
        event.date_parse = event.date.strftime('%b %d, %Y')

        offered = Ride.all().filter('event = ', event.key()).filter('driver != ', None).fetch(None)
        requested = Ride.all().filter('event = ', event.key()).filter('driver = ', None).fetch(None)

        requesters = Requester.all().filter('event = ', event.key()).fetch(None)

        has_request = False
        if user in requesters:
            has_request = True

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

        toolbox.render(self, 'view_event.html', {
            'event': event,
            'offered': offered,
            'requesters': requesters,
            'user': user,
            'circle': self.circle(),
            'has_request': has_request
        })

class EventRequest(BaseHandler):
    def post(self, event_id):
        self.auth()

        user = self.current_user()

        e = Event().get_by_id(int(event_id))

        r = Requester()

        r.user = user
        r.event = e
        r.seats = 1

        r.put()

        self.json_resp(200, {
            'id': e.key().id()
        })

class EventUnrequest(BaseHandler):
    def post(self, event_id):
        self.auth()

        user = self.current_user()

        json_str = self.request.body
        data = json.loads(json_str)

        e = Event().get_by_id(int(event_id))

        request = Requester.get_by_id(int(data['id']))

        if request:
            request.delete()

            self.json_resp(200, {
                'id': e.key().id()
            })

        else:
            self.json_resp(500, {
                'message': 'No request exists.'
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
            Required('lat'): Coerce(float),
            Required('lng'): Coerce(float),
            Required('address'): unicode,
            Required('date'): toolbox.create_date(),
            'time': unicode,
            'details': unicode,
            'location': unicode
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
        event.location = data['location']
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
                event.circle = circle
        else:
            event.circle = None

        event.put()

        # NEW NOTIFICATION
        n = Noti()
        n.relation = event.key()
        n.type = 'new_event'
        n.user = user.key()
        n.status = 'new'
        n.put()

        # EMAIL NOTIFICATION
        if event.circle:
            c_members = User.all().filter('circles =', event.circle.key()).fetch(None)
            d = {
                'template': 'event_created',
                'data': {
                    'circle_name': event.circle.name,
                    'circle_id': event.circle.key().id(),
                    'event_name': event.name,
                    'event_id': event.key().id()
                },
                'subject': 'Ridecircles - An event was created in ' + event.circle.name,
                'users': c_members
            }

            sender(d)

        return self.json_resp(200, {
            'message': 'Event added!',
            'id': event.key().id()
        })

class EditEvent(BaseHandler):
    def get(self, event_id):
        self.auth()

        user = self.current_user()

        event = Event.get_by_id(int(event_id))

        properties = ['name', 'date', 'time', 'details', 'location']

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


        event_validator = Schema({
            Required('name'): unicode,
            'location': unicode,
            'ql_lat': Coerce(float),
            'ql_lng': Coerce(float),
            'ql_add': unicode,
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

        user = self.current_user()

        event = Event.get_by_id(int(event_id))

        event.name = data['name']
        event.location = data['location']
        event.data = data['date']
        event.time = data['time']
        event.details = data['details']
        event.address = data['ql_add']
        event.lat = data['ql_lat']
        event.lng = data['ql_lng']
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

        if not event:
            return self.json_resp(500, {
                'message': 'This event does not exists.'
            })

        if user.key() != event.creator.key():
            return self.json_resp(500, {
                'message': 'You do not have permission to delete this event.'
            })

        connected_rides = Ride.all().filter('event =', event.key()).fetch(None)

        for ride in connected_rides:
            ride.delete()

        event.delete()

        return self.json_resp(200, {
            'message': 'Deleted event and all associated rides.'
        })
