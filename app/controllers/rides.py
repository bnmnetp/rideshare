from app.common.toolbox import doRender, split_address, grab_json
from app.model import *
from google.appengine.ext import db
import datetime
from datetime import date
import datetime
import json
from app.base_handler import BaseHandler
from app.common.notification import push_noti
from app.common.voluptuous import *

class RideHandler(BaseHandler):
    def get(self):
        # if driver.key().id() == user.key().id()
        # if user.key().id() in ride.passengers
        self.auth()
        user = self.current_user()

        rides_user_1 = Ride.all().filter('passengers =', user.key()).fetch(100)
        rides_user_2 = Ride.all().filter('driver = ', user.key()).fetch(100)

        rides_user = rides_user_1 + rides_user_2

        rides_all = Ride.all().fetch(100)

        # Grabs the city and state from the addresses
        # Comes in format: Address, City, State Zip
        if rides_all:
            for ride in rides_all:
                ride.dest = split_address(ride.dest_add)
                ride.orig = split_address(ride.origin_add)
                if ride.driver:
                    if ride.driver.key().id() == user.key().id():
                        ride.is_driver = True
                    else:
                        ride.is_driver = False
                if user.key() in ride.passengers:
                    ride.is_passenger = True
                else:
                    ride.is_passenger = False

        if rides_user:
            for ride in rides_user:
                ride.dest = split_address(ride.dest_add)
                ride.orig = split_address(ride.origin_add)
                if ride.driver:
                    if ride.driver.key().id() == user.key().id():
                        ride.is_driver = True
                    else:
                        ride.is_driver = False
                if user.key() in ride.passengers:
                    ride.is_passenger = True
                else:
                    ride.is_passenger = False

        doRender(self, 'rides.html', {
            'rides_user': rides_user,
            'rides_all': rides_all,
            'user': user
        })

    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        rides = Ride.all()

        if data['circle'] != '':
            rides.filter('circle = ', data['circle'])

        results = json.dumps([r.to_dict() for r in rides])
        self.response.write(results)

class FilterRides(BaseHandler):
    def post(self):
        self.auth()

        user = self.current_user()

        json_str = self.request_body
        data = json.loads(json_str)

        rides = Ride.all()

        if data['filter'] == 'no_driver':
            rides.filter('driver = ', None)
        if data['filter'] == 'driver':
            rides.filter('driver != ', None)
        if data['filter'] == 'user_passenger':
            rides.filter('passengers in', user.key())
        if data['filter'] == 'current':
            today = date.today()
            rides.filter('date >=', today)
        if data['filter'] == 'past':
            print 'test'

        for ride in rides:
            ride.dest = split_address(ride.dest_add)
            ride.orig = split_address(ride.origin_add)

        results = json.dumps([r.to_dict() for r in rides])
        self.response.write(results)


class EditRide(BaseHandler):
    def get(self, ride_id):
        self.auth()

        user = self.current_user()

        ride = Ride.get_by_id(int(ride_id))

        if not ride or ride.driver == None:
            self.redirect('/rides')
            return None

        properties = ['passengers_max', 'date', 'time', 'details']

        ride_json = grab_json(ride, properties)

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
            Required('date'): unicode,
            Required('time'): unicode,
            'details': unicode
        })

        try:
            data = ride_validator(data)
        except MultipleInvalid as e:
            print str(e)
            self.response.set_status(500)
            self.response.write(json.dumps({
                'error': 'Invalid data'
            }))
            return None

        ride.passengers_max = data['passengers_max']
        # ride.date = data['date'].date
        ride.time = data['time']
        ride.details = data['details']

        ride.put()

        for p in ride.passengers:
            push_noti('edited', p, ride.key())

        self.response.write(json.dumps({
            'message': 'Edited.'
        }))

    def Date(self, fmt='%Y-%m-%d'):
        return lambda v: datetime.strptime(v, fmt)


class GetRideHandler(BaseHandler):
    def post(self, ride_id):
        self.auth()

        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        ride = Ride.get_by_id(int(ride_id))

        if data['type'] == 'passenger':
            if data['action'] == 'leave':
                if user.key() in ride.passengers:
                    if ride.driver:
                        push_noti('pass_leave', ride.driver.key(), ride.key())
                    ride.passengers.remove(user.key())
                    resp = {
                        'strong': 'Left the ride!',
                        'message': 'You are no longer a passenger.'
                    }
                    self.response.write(json.dumps(resp))
            if data['action'] == 'join':
                if user.key() not in ride.passengers:
                    if ride.passengers_total < ride.passengers_max:
                        if ride.driver:
                            push_noti('pass_join', ride.driver.key(), ride.key())
                        ride.passengers.append(user.key())
                        resp = {
                            'strong': 'Joined the ride!',
                            'message': 'You are now a passenger'
                        }
                        self.response.write(json.dumps(resp))
                    else:
                        self.response.set_status(500)
                        resp = {
                            'strong': 'This ride is full.',
                            'message': 'Please try another ride.'
                        }
                        self.response.write(json.dumps(resp))

            ride.put()
        if data['type'] == 'driver':
            if data['action'] == 'leave':
                if ride.has_driver:
                    for passenger in ride.passengers:
                        push_noti('driver_leave', passenger, ride.key())
                    ride.has_driver = False
                    ride.driver = None
                    resp = {
                        'strong': 'Left the ride!',
                        'message': 'You are no longer the driver.'
                    }
                    self.response.write(json.dumps(resp))
            if data['action'] == 'join':
                if not ride.has_driver:
                    for passenger in ride.passengers:
                        push_noti('driver_join', passenger, ride.key())
                    ride.has_driver = True
                    ride.driver = user.key()
                    resp = {
                        'strong': 'Joined the ride!',
                        'message': 'You are the driver of this ride.'
                    }
                    self.response.write(json.dumps(resp))
                else:
                    self.response.set_status(500)
                    resp = {
                        'strong': 'This ride already has a driver',
                        'message': 'Thanks for your offer.'
                    }
                    self.response.write(json.dumps(resp))
            ride.put()


    def get(self, ride_id):
        self.auth()

        ride = Ride.get_by_id(int(ride_id))

        user = self.current_user()
        availible_seats = 0

        if ride.driver:
            availible_seats = ride.passengers_max - ride.passengers_total;

        passengers = []
        for passenger in ride.passengers:
            passengers.append(User.get(passenger))

        # For view conditionals
        if ride.has_driver:
            if ride.driver.key().id() == user.key().id():
                ride.is_driver = True
                ride.need_driver = False
            else:
                ride.is_driver = False
                ride.need_driver = False
        else:
            ride.is_driver = False
            ride.need_driver = True

        if user.key() in ride.passengers:
            ride.is_pass = True
            ride.can_pass = False
        elif not ride.is_driver:
            ride.is_pass = False
            ride.can_pass = True
        else:
            ride.is_pass = False
            ride.can_pass = False
        # End view conditionals

        comments = Comment.all().filter('ride = ', ride.key()).order('-date')

        if ride:
            doRender(self, 'view_ride.html', {
                'ride': ride,
                'passengers': passengers,
                'seats': availible_seats,
                'user': user
            })
        else:
            self.response.write('No ride found.')

class RideJoinHandler(BaseHandler):
    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        ride = Ride.get_by_id(int(data['id']))

        if ride:
            # Possible input for data['type']: ['passenger', 'driver']
            if data['type'] == 'passenger':
                ride.passengers.append(user.key())
            elif data['type'] == 'driver':
                ride.passengers_max = 1
                ride.passengers_total = 0
                ride.has_driver = True
                ride.driver = user.key()
                # Replace
                ride.driver_name = user.name
                ride.contact = user.email

            ride.put()

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
    
class NewRideHandler(BaseHandler):
    def post(self):
        ride = Ride()
        
        json_str = self.request.body
        data = json.loads(json_str)

        # Creates date object from Month/Day/Year format
        d_arr = data['date'].split('/')
        d_obj = datetime.date(int(d_arr[2]), int(d_arr[0]), int(d_arr[1]))

        user = self.current_user()

        # Refer to model.py for structure of data
        # class Ride
        if 'event' in data:
            event = Event.get_by_id(int(data['event']))
            ride.dest_add = event.address
            ride.dest_lat = event.lat
            ride.dest_lng = event.lng
            ride.event = event.key()
        else:
            ride.dest_add = data['dest']['address']
            ride.dest_lat = data['dest']['lat']
            ride.dest_lng = data['dest']['lng']

        ride.origin_add = data['orig']['address']
        ride.origin_lat = data['orig']['lat']
        ride.origin_lng = data['orig']['lng']

        ride.date = d_obj
        ride.time = data['time']
        ride.passengers = []

        if data['driver'] == True:
            ride.passengers_max = int(data['max_passengers'])
            ride.passengers_total = 0
            ride.driver = user.key()
            ride.has_driver = data['driver']
            ride.driver_name = "Replace"
            ride.contact = "Replace"
        else:
            ride.passengers.append(user.key())

        if data['circle'] != '':
            circle = Circle.get_by_id(int(data['circle']))
            if circle:
                ride.circle = circle.key()
        else:
            ride.circle = None

        ride_key = ride.put()

        # self.send_email()
        response = {
            'message': 'Ride added!'
        }
        self.response.write(json.dumps(response))