from app.common.toolbox import doRender, split_address, grab_json, create_date, set_properties
from app.model import *
from google.appengine.ext import db
import datetime
from datetime import date
import json
from app.base_handler import BaseHandler
from app.common.notification import push_noti
from app.common.voluptuous import *
import urllib, urllib2

def is_pass_similar_ride(user, ride):
    matches = []
    passengers_match_user = Passenger.all().filter('user = ', user.key()).fetch(None)
    for p in passengers_match_user:

        if p.ride.event.key() == ride.event.key():
            if p.ride.key() != ride.key():
                matches.append(p)

    formatted_matches = []
    if matches:
        for match in matches:
            formatted_matches.append(str(match.ride.key().id()))
        return formatted_matches
    else:
        return None

class RideHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        doRender(self, 'rides.html', {
            'user': user,
            'circle': self.circle()
        })

    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        rides = Ride.all()

        today = date.today()
        rides.filter('date >=', today)

        if data['circle'] != False:
            circle = Circle.get_by_id(int(data['circle']))
            rides.filter('circle = ', circle.key())

        results = json.dumps([r.to_dict() for r in rides])
        self.response.write(results)

class FilterRides(BaseHandler):
    def post(self):
        self.auth()

        user = self.current_user()

        json_str = self.request.body
        data = json.loads(json_str)

        rides = Ride.all()

        if data['circle']:
            circle = Circle.get_by_id(int(data['circle']))
            rides.filter('circle =', circle.key())

        if data['filter'] == 'no_driver':
            rides.filter('driver = ', None)
        if data['filter'] == 'driver':
            rides.filter('driver != ', None)
        if data['filter'] == 'user_passenger':
            rides.filter('passengers =', user.key())
        if data['filter'] == 'user_driver':
            rides.filter('driver =', user.key())
        if data['filter'] == 'current':
            today = date.today()
            rides.filter('date >=', today)
        if data['filter'] == 'past':
            print 'test'

        results = []
        for ride in rides:
            d = {}
            d['dest'] = split_address(ride.dest_add)
            d['orig'] = split_address(ride.origin_add)
            d['id'] = ride.key().id()
            d['date'] = str(ride.date)
            results.append(d)

        self.response.write(json.dumps(results))

class EditRide(BaseHandler):

    properties = ['passengers_max', 'date', 'time', 'details', 'driven_by']

    def get(self, ride_id):
        self.auth()

        user = self.current_user()

        ride = Ride.get_by_id(int(ride_id))

        if not ride or ride.driver == None:
            self.redirect('/rides')
            return None

        ride_json = grab_json(ride, self.properties)

        ride_json['date'] = ride.date_picker

        doRender(self, 'edit_ride.html', {
            'user': user,
            'ride': ride,
            'ride_json': ride_json
        })

    def post(self, ride_id):
        self.auth()

        user = self.current_user()

        ride = Ride.get_by_id(int(ride_id))

        if not ride or ride.driver == None:
             return self.json_resp(500, {
                'error': 'Message'
            })

        json_str = self.request.body
        data = json.loads(json_str)

        ride_validator = Schema({
            Required('passengers_max', default=1): Coerce(int),
            Required('date'): create_date(),
            Required('time'): unicode,
            'details': unicode,
            'driven_by': unicode
        })

        try:
            data = ride_validator(data)
        except MultipleInvalid as e:
            return self.json_resp(500, {
                'error': True,
                'message': str(e)
            })

        set_properties(ride, self.properties, data)

        ride.put()

        passengers = ride.passengers
        for p in passengers:
            push_noti('edited', p, ride.key())

        self.response.write(json.dumps({
            'message': 'Edited.',
            'id': ride.key().id()
        }))

class JoinDriver(BaseHandler):
    def post(self, ride_id):
        self.auth()
        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        ride_validator = Schema({
            Required('passengers_max', default=1): Coerce(int),
            Required('date'): create_date(),
            'time': unicode,
            'details': unicode
        })

        try:
            data = ride_validator(data)
        except MultipleInvalid as e:
            print str(e)
            return self.json_resp(500, {
                'error': True,
                'message': 'Invalid data'
            })

        ride = Ride.get_by_id(int(ride_id))

        ride.passengers_max = data['passengers_max']
        ride.driver = user.key()
        ride.time = data['time']
        ride.details = data['details']
        ride.put()

        for passenger in ride.passengers:
            push_noti('driver_join', passenger, ride.key())

        resp = {
            'message': 'Success.'
        }
        self.response.write(json.dumps(resp))

class JoinPassenger(BaseHandler):
    def post(self, ride_id):
        self.auth()
        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        join_validator = Schema({
            Required('seats_claimed', default=1): Coerce(int),
            'message': unicode
        })

        try:
            data = join_validator(data)
        except MultipleInvalid as e:
            return self.json_resp(500, {
                'error': True,
                'message': str(e)
            })

        ride = Ride.get_by_id(int(ride_id))

        all_passengers = ride.passengers

        if (ride.passengers_total + data['seats_claimed']) > ride.passengers_max:
            return self.json_resp(500, {
                'error': True,
                'message': 'There are not enough seats for you.'
            })

        p = Passenger()
        p.ride = ride.key()
        p.user = user.key()
        p.seats = data['seats_claimed']
        p.message = data['message']
        p.put()

        return self.json_resp(200, {
            'message': 'You have been added to this ride.'
        })

class GetRide(BaseHandler):
    def post(self, ride_id):
        self.auth()

        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        ride = Ride.get_by_id(int(ride_id))

        if data['type'] == 'passenger':
            if data['action'] == 'leave':
                passenger = Passenger.all().filter('ride =', ride.key()).filter('user =', user.key()).get()
                passenger.delete()
                if passenger:
                    if ride.driver:
                        push_noti('pass_leave', ride.driver.key(), ride.key())
                resp = {
                        'strong': 'Left the ride!',
                        'message': 'You are no longer a passenger.'
                    }
                self.response.write(json.dumps(resp))

        if data['type'] == 'driver':
            if data['action'] == 'leave':
                if ride.driver:
                    for passenger in ride.passengers:
                        push_noti('driver_leave', passenger.user.key(), ride.key())
                    ride.driver = None
                    resp = {
                        'strong': 'Left the ride!',
                        'message': 'You are no longer the driver.'
                    }
                    self.response.write(json.dumps(resp))
            ride.put()


    def get(self, ride_id):
        self.auth()

        ride = Ride.get_by_id(int(ride_id))

        if not ride:
            return self.redirect('/rides')

        user = self.current_user()
        availible_seats = 8

        if ride.driver and ride.passengers_max:
            availible_seats = ride.passengers_max - ride.passengers_total

        passengers = Passenger.all().filter('ride = ', ride.key()).fetch(None)

        # For view conditionals
        if ride.driver:
            if ride.driver.key().id() == user.key().id():
                ride.is_driver = True
                ride.need_driver = False
            else:
                ride.is_driver = False
                ride.need_driver = False
        else:
            ride.is_driver = False
            ride.need_driver = True

        if ride.creator == user.key():
            ride.can_edit = True

        if ride.is_passenger(user.key()):
            ride.is_pass = True
            ride.can_pass = False
        elif not ride.is_driver:
            ride.is_pass = False
            ride.can_pass = True
        else:
            ride.is_pass = False
            ride.can_pass = False
        # End view conditionals

        if is_pass_similar_ride(user, ride):
            similar_rides = is_pass_similar_ride(user, ride)
        else:
            similar_rides = None

        print 'SIMILAR RIDES'
        print similar_rides

        if ride:
            doRender(self, 'view_ride.html', {
                'ride': ride,
                'passengers': passengers,
                'seats': availible_seats,
                'user': user,
                'circle': self.circle(),
                'similar_rides': similar_rides
            })
        else:
            self.response.write('No ride found.')
    
class NewRideHandler(BaseHandler):
    def post(self):
        ride = Ride()
        
        json_str = self.request.body
        data = json.loads(json_str)

        ride_validator = Schema({
            'passengers_max': Coerce(int),
            Required('date'): create_date(),
            'time': unicode,
            'details': unicode,
            'driver': bool,
            'driven_by': unicode,
            Required('dest'): {
                'lat': Coerce(float),
                'lng': Coerce(float),
                'address': unicode
            },
            Required('orig'): {
                'lat': Coerce(float),
                'lng': Coerce(float),
                'address': unicode
            },
            'recurring': unicode,
            'circle': Coerce(long)
        })

        try:
            data = ride_validator(data)
        except MultipleInvalid as e:
            return self.json_resp(500, {
                'error': True,
                'message': str(e)
            })

        user = self.current_user()

        # Refer to model.py for structure of data
        # class Ride
        ride.dest_add = data['dest']['address']
        ride.dest_lat = data['dest']['lat']
        ride.dest_lng = data['dest']['lng']
        ride.origin_add = data['orig']['address']
        ride.origin_lat = data['orig']['lat']
        ride.origin_lng = data['orig']['lng']
        ride.date = data['date']
        ride.time = data['time']
        ride.creator = user

        if data['driver'] == True:
            ride.passengers_max = int(data['passengers_max'])
            ride.driver = user.key()
            if ride.recurring == 'false' or ride.recurring == 'none':
                ride.recurring = None
            else:
                ride.recurring = data['recurring']
            ride.driven_by = data['driven_by']


        if data['circle'] != '':
            circle = Circle.get_by_id(int(data['circle']))
            if circle:
                ride.circle = circle.key()
        else:
            ride.circle = None

        ride.put()

        if data['driver'] != True:
            p = Passenger()
            p.ride = ride.key()
            p.user = user
            p.seats = 1
            p.message = ''
            p.put()

        return self.json_resp(200, {
            'message': 'Ride added!',
            'id': ride.key().id()
        })

class RideEvent(BaseHandler):
    def post(self, event_id, join_type):
        self.auth()
        json_str = self.request.body
        data = json.loads(json_str)

        if not (join_type == 'passenger' or join_type == 'driver'):
            print join_type
            return self.json_resp(500, {
                'message': 'Invalid type'
            })

        user = self.current_user()

        ride_validator = Schema({
            'passengers_max': Coerce(int),
            Required('date'): create_date(),
            Required('address'): unicode,
            'time': unicode,
            'details': unicode,
            'driver': bool,
            'circle': unicode,
            'lat': Coerce(float),
            'lng': Coerce(float)
        })

        try:
            data = ride_validator(data)
        except MultipleInvalid as e:
            print str(e)
            return self.json_resp(500, {
                'error': True,
                'message': 'Invalid data'
            })

        event = Event.get_by_id(int(event_id))

        ride = Ride()

        ride.dest_add = event.address
        ride.dest_lat = event.lat
        ride.dest_lng = event.lng
        ride.origin_add = data['address']
        ride.origin_lat = data['lat']
        ride.origin_lng = data['lng']
        ride.date = data['date']
        ride.time = data['time']
        ride.circle = self.circle().key()
        
        ride.event = event.key()

        if join_type == 'driver':
            ride.passengers_max = int(data['passengers_max'])
            ride.driver = user.key()

        ride.put()

        if join_type == 'passenger':
            p = Passenger()
            p.ride = ride.key()
            p.user = user
            p.seats = 1
            p.message = ''
            p.put()

        response = {
            'message': 'Ride added!',
            'id': ride.key().id()
        }
        self.response.write(json.dumps(response))