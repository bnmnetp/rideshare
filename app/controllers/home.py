from app.common.toolbox import doRender, grab_json, split_address, date_display
from google.appengine.ext import db
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json
from app.model import *
import datetime
from datetime import date
from app.common.email_sys import sender

noti = {
    'new_event': { # /
        'symbol': 'location-arrow',
        'template': '<a href="/event/{}">{}</a> has been added to <a href="/circle/{}">{}</a>',
        'title': 'New Event'
    },
    'request_circle': { # /
        'symbol': 'question',
        'template': '<a href="/user/{}">{}</a> and {} other people have requested to join <a href="/circle/{}">{}</a>',
        'title': 'Request for Circle'
    },
    'invite_circle': { # X
        'symbol': 'plus-square-o',
        'template': '<a href="/user/{}">{}</a> has invited you to join <a href="/circle/{}">{}</a>',
        'title': 'Invite to Circle'
    },
    'passenger_joined': { # /
        'symbol': 'users',
        'template': '<a href="/user/{}">{}</a> and {} other people have joined your ride <a href="/ride/{}">from {} to {}</a> as a passenger',
        'title': 'Passenger Joined'
    },
    'driver_joined': { # /
        'symbol': 'thumbs-up',
        'template': '<a href="/user/{}">{}</a> has joined your ride <a href="/ride/{}">from {} to {}</a> as a driver',
        'title': 'Driver Joined'
    },
    'ride_offered': { # X
        'symbol': 'thumbs-up',
        'template': '{} ride(s) are offered to <a href="/event/{}">{}</a>.',
        'title': 'Ride Offered'
    },
    'ride_updated': { # /
        'symbol': 'exclamation',
        'template': '<a href="/ride/{}">from {} to {}</a> has been updated',
        'title': 'Ride Updated'
    }
}

class Home2(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()
        today = date.today()
        # events !
        # requests !
        # invites
        # passengers !
        # drivers !
        # updates
        events = Event.all().filter('circle in', user.circles).filter('date >=', today).fetch(10)
        driving = Ride.all().filter('driver =', user.key()).filter('date >=', today).fetch(10)
        pass_join = Passenger.all().filter('ride in', driving).fetch(10)
        requests = Requester.all().filter('user = ', user.key()).fetch(10)
        circle_owned = Circle.all().filter('admins =', user.key()).fetch(10)

        notifications = []

        for e in circle_owned:
            if e.key() not in user.notis:
                t = 'request_circle'
                if e.requests:
                    first = User.get(e.requests[0])
                    plus_more = len(e.requests) - 1
                    notifications.append({
                        'id': e.key(),
                        'type': t,
                        'message': noti[t]['template'].format(
                            first.key().id(),
                            first.name,
                            plus_more,
                            e.key().id(),
                            e.name
                        )
                    })

        for e in events:
            if e.key() not in user.notis:
                t = 'new_event'
                notifications.append({
                    'id': e.key(),
                    'type': t,
                    'message': noti[t]['template'].format(
                        e.key().id(),
                        e.name,
                        e.circle.key().id(),
                        e.circle.name
                    )
                })

        for p in pass_join:
            if p.key() not in user.notis:
                t = 'passenger_joined'
                notifications.append({
                    'id': p.key(),
                    'type': t,
                    'message': noti[t]['template'].format(
                        p.user.key().id(),
                        p.user.name,
                        0,
                        p.ride.key().id(),
                        p.ride.origin_add,
                        p.ride.dest_add
                    )
                })

        for r in requests:
            if r.key() not in user.notis:
                t = 'ride_offered'
                today = date.today()
                rides_offered = Ride.all().filter('event =', r.event).fetch(None)
                if r.event.date >= today and len(rides_offered):
                    notifications.append({
                        'id': r.key(),
                        'type': t,
                        'message': noti[t]['template'].format(
                            len(rides_offered),
                            r.event.key().id(),
                            r.event.name
                        )
                    })
        # for d in is_pass:
        #     t = 'driver_joined'
        #     if d.ride.driver:
        #         notifications.append({
        #             'type': t,
        #             'message': noti[t]['template'].format(
        #                 d.ride.driver.key().id(),
        #                 d.ride.driver.name,
        #                 d.ride.key().id(),
        #                 d.ride.origin_add,
        #                 d.ride.dest_add
        #             )
        #         })

        for n in notifications:
            n['title'] = noti[n['type']]['title']
            n['symbol'] = noti[n['type']]['symbol']

        circles = Circle.all().fetch(None)

        for circle in circles:
            if circle.key() in user.circles:
                circle.user = True
            else:
                circle.user = False

        doRender(self, 'home2.html', { 
            'site_notis': notifications,
            'user': user,
            'circles': circles
        })

# class ClearNotification(BaseHandler):
#     def post(self):
#         self.auth()

#         user = self.current_user()