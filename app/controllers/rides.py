from app.common.toolbox import doRender, split_address, grab_json, create_date, set_properties
from app.common import toolbox
from app.model import *
from google.appengine.ext import db
import datetime
from datetime import date
import json
from app.base_handler import BaseHandler
from app.common.notification import push_noti
from app.common.voluptuous import *
from app.common.email_sys import sender
import urllib, urllib2

class GetRides(BaseHandler):
    def get(self):
        self.auth()

        user = self.current_user()

        today = date.today()

        rides_driven = Ride.all()
        rides_driven.filter('driver =', user.key())
        rides_driven.filter('date >', today)
        rides_driven.fetch(100)

        passengers = Passenger.all().filter('user =', user.key()).fetch(100)

        rides_passenger = []
        for p in passengers:
            p.ride.orig = split_address(p.ride.origin_add)
            p.ride.dest = split_address(p.ride.dest_add)
            if p.ride.date >= today:
                rides_passenger.append(p.ride)


        print(rides_passenger, 'INFOXXX')
        print(rides_driven, 'INFOXXX')


        doRender(self, 'rides.html', {
                'user': user,
                'rides_driven': rides_driven,
                'rides_passenger': rides_passenger
            })

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
        today = date.today()
        rides.filter('date >=', today)

        # if data['circle']:
        #     circle = Circle.get_by_id(int(data['circle']))
        #     rides.filter('circle =', circle.key())

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
        rides.fetch(None)
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
        ride_json['date'] = toolbox.date_picker(ride.date)

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
            'driven_by': unicode,
            'ql_add': unicode,
            'ql_lat': Coerce(float),
            'ql_lng': Coerce(float)
        })

        try:
            data = ride_validator(data)
        except MultipleInvalid as e:
            return self.json_resp(500, {
                'error': True,
                'message': str(e)
            })

        set_properties(ride, self.properties, data)

        ride.origin_add = data['ql_add']
        ride.origin_lat = data['ql_lat']
        ride.origin_lng = data['ql_lng']

        ride.put()

        # EMAIL NOTIFICATION
        passengers = Passenger.all().filter('ride =', ride.key()).fetch(None)

        notifications = Noti.all().filter('relation =', ride.key()).fetch(None)
        for n in notifications:
            n.status = 'new'
            n.put()

        user_have_noti = [n.user for n in notifications]
        for p in passengers:
            if p.user.key() not in user_have_noti:
                n = Noti()
                n.relation = ride.key()
                n.type = 'ride_updated'
                n.user = p.user.key()
                n.status = 'new'
                n.put()

        if passengers and ride.event and ride.event.circle:
            
            d = {
                'template': 'ride_edited',
                'data': {
                    'driver_name': ride.driver.name_x,
                    'driver_id': ride.driver.key().id(),
                    'circle_name': ride.event.circle.name,
                    'circle_id': ride.event.circle.key().id(),
                    'event_name': ride.event.name,
                    'event_id': ride.event.key().id(),
                    'ride_id': ride.key().id()
                },
                'subject': 'Ridecircles - Ride details updated',
                'users': [r.user for r in passengers]
            }

            sender(d)

        return self.json_resp(200, {
            'message': 'Edited.',
            'id': ride.key().id()
        })

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

        check_requester = Requester.all().filter('user =', user).filter('ride =', ride).fetch(None)

        if check_requester:
            for cr in check_requester:
                cr.delete()

        passengers = Passenger.all().filter('ride =', ride.key()).fetch(None)
        for passenger in passengers:
            # NEW NOTIFICATION
            n = Noti()
            n.relation = ride.key()
            n.type = 'driver_joined'
            n.user = passenger.user.key()
            n.status = 'new'
            n.put()

        return self.json_resp(200, {
            'message': 'Success'
        })

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

        # check_requests
        if ride.event:
            requests = Requester.all().filter('event =', ride.event.key()).filter('user =', user.key()).fetch(None)
            if requests:
                for r in requests:
                    r.delete()

        # EMAIL NOTIFICATION
        if ride.driver and ride.event:
            # NEW NOTIFICATION
            n = Noti()
            n.relation = ride.key()
            n.type = 'passenger_joined'
            n.user = ride.driver.key()
            n.status = 'new'
            n.put()

            d = {
                'template': 'passenger_joined',
                'data': {
                    'pass_name': p.user.name_x,
                    'pass_id': p.user.key().id(),
                    'circle_name': ride.event.circle.name,
                    'circle_id': ride.event.circle.key().id(),
                    'event_name': ride.event.name,
                    'event_id': ride.event.key().id(),
                    'ride_id': ride.key().id(),
                    'ride_name': ride.origin_add + ' to ' + ride.dest_add,
                    'seats': p.seats
                },
                'subject': 'Ridecircles - A passenger joined your ride.',
                'users': [ride.driver]
            }

            sender(d)

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

                other_passengers = Passenger.all().filter('ride =', ride.key()).fetch(None)
                if not ride.driver and not other_passengers:
                    ride.delete()

                resp = {
                    'strong': 'Left the ride!',
                    'message': 'You are no longer a passenger.'
                }

                self.json_resp(200, resp)

        if data['type'] == 'driver':
            if data['action'] == 'leave':
                if ride.driver:
                    ride.driver = None

                    any_passengers = Passenger.all().filter('ride =', ride.key()).fetch(None)

                    if not any_passengers:
                        ride.delete()
                    else:
                        ride.put()

                    resp = {
                        'strong': 'Left the ride!',
                        'message': 'You are no longer the driver.'
                    }
                    self.json_resp(200, resp)

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

        # print 'SIMILAR RIDES'
        # print similar_rides

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

class CreateRide(BaseHandler):
    # EMAIL NOTIFICATION
    def alert_requesters(self, event, circle, ride):
        requesters = Requester().all().filter('event = ', event.key()).fetch(None)

        d = {
            'template': 'new_ride',
            'data': {
                'circle_name': circle.name,
                'circle_id': circle.key().id(),
                'event_name': event.name,
                'event_id': event.key().id(),
                'ride_id': ride.key().id()
            },
            'subject': 'New Ride offered for ' + event.name,
            'users': [r.user for r in requesters]
        }

        sender(d)

    def post(self):
        self.auth()

        user = self.current_user()

        json_str = self.request.body
        data = json.loads(json_str)

        ride_validator = Schema({
            'passengers_max': Coerce(int),
            Required('date'): create_date(),
            'time': unicode,
            'details': unicode,
            'driver': bool,
            'driven_by': unicode,
            'dest_lat': Coerce(float),
            'dest_lng': Coerce(float),
            'dest_address': unicode,
            'ql_lat': Coerce(float),
            'ql_lng': Coerce(float),
            'ql_add': unicode,
            'recurring': unicode,
            'circle': Coerce(long),
            'event': unicode
        })

        try:
            data = ride_validator(data)
        except MultipleInvalid as e:
            return self.json_resp(500, {
                'error': True,
                'message': str(e)
            })

        ride = Ride()

        if data['event'] != '':
            event = Event.get_by_id(int(data['event']))
            if event:
                ride.dest_add = event.address
                ride.dest_lat = event.lat
                ride.dest_lng = event.lng
                ride.event = event.key()
            else:
                return self.json_resp(500, {
                    'message': 'Event does not exist'
                })
        else:
            event = None
            ride.dest_add = data['dest_address']
            ride.dest_lat = data['dest_lat']
            ride.dest_lng = data['dest_lng']

        ride.origin_add = data['ql_add']
        ride.origin_lat = data['ql_lat']
        ride.origin_lng = data['ql_lng']
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
                return self.json_resp(500, {
                    'message': 'Circle does not exist'
                })
        else:
            circle = None
            ride.circle = None

        ride.put()

        if data['driver'] != True:
            p = Passenger()
            p.ride = ride.key()
            p.user = user
            p.seats = 1
            p.message = data['details']
            p.put()

        if event and circle:
            self.alert_requesters(event, circle, ride)

        return self.json_resp(200, {
            'message': 'Ride added!',
            'id': ride.key().id()
        })

class DeleteRide(BaseHandler):
    def post(self, ride_id):
        self.auth()

        ride = Ride.get_by_id(int(ride_id))

        user = self.current_user()

        if not ride:
            return self.json_resp(500, {
                'message': 'No ride found'
            })

        if ride.creator and ride.creator.key() != user.key():
            return self.json_resp(500, {
                'message': 'Cannot delete. You did not create this ride.'
            })            

        ride.delete()

        return self.json_resp(200, {
            'message': 'Ride deleted.'
        })