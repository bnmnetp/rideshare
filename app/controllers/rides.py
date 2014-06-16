from app.common.toolbox import doRender, split_address
from app.model import *
from google.appengine.ext import db
import datetime
from datetime import date
import json
from app.base_handler import BaseHandler
from app.common.notification import push_noti

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

        if data['circle']:
            rides.filter('circle = ', data['circle'])

        results = json.dumps([r.to_dict() for r in rides])
        self.response.write(results)

class GetRideHandler(BaseHandler):
    def post(self, ride_id):
        self.auth()

        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        ride = Ride.get_by_id(int(ride_id))

        if not ride:
            print 'error'

        if data['type'] == 'passenger':
            if data['action'] == 'leave':
                if user.key() in ride.passengers:
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
            driver = db.get(ride.driver.key())
            availible_seats = ride.passengers_max - ride.passengers_total;
        else:
            driver = {}

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
                'driver': driver,
                'passengers': passengers,
                'seats': availible_seats,
                'circle': ride.circle,
                'event': ride.event,
                'user': user,
                'comments': comments
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
            ride.dest_add = data['destination']['address']
            ride.dest_lat = data['destination']['lat']
            ride.dest_lng = data['destination']['lng']

        ride.origin_add = data['origin']['address']
        ride.origin_lat = data['origin']['lat']
        ride.origin_lng = data['origin']['lng']

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

        ride.circle = ""

        ride_key = ride.put()

        # self.send_email()
        response = {
            'message': 'Ride added!'
        }
        self.response.write(json.dumps(response))