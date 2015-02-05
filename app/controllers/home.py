from app.common.toolbox import doRender, grab_json, split_address, date_display
from google.appengine.ext import db
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json
from app.model import *
import datetime
from datetime import date

noti = {
    'new_event': {
        'symbol': 'location-arrow',
        'template': '<a href="/event/{}">{}</a> has been added to <a href="/circle/{}">{}</a>',
        'title': 'New Event'
    },
    'request_circle': {
        'symbol': 'question',
        'template': '<a href="/user/{}">{}</a> and {} other people have requested to join <a href="/circle/{}">{}</a>',
        'title': 'Request for Circle'
    },
    'invite_circle': {
        'symbol': 'plus-square-o',
        'template': '<a href="/user/{}">{}</a> has invited you to join <a href="/circle/{}">{}</a>',
        'title': 'Invite to Circle'
    },
    'passenger_joined': {
        'symbol': 'users',
        'template': '<a href="/user/{}">{}</a> and {} other people have joined your ride <a href="/ride/{}">from {} to {}</a> as a passenger',
        'title': 'Passenger Joined'
    },
    'driver_joined': {
        'symbol': 'thumbs-up',
        'template': '<a href="/user/{}">{}</a> has joined your ride <a href="/ride/{}">from {} to {}</a> as a driver',
        'title': 'Driver Joined'
    },
    'ride_offered': {
        'symbol': 'thumbs-up',
        'template': '{} ride(s) are offered to <a href="/event/{}">{}</a>.',
        'title': 'Ride Offered'
    },
    'ride_updated': {
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
        # is_pass = Passenger.all().filter('user =', user.key()).fetch(10)
        requests = Requester.all().filter('user = ', user.key()).fetch(10)

        circle_owned = Circle.all().filter('admins =', user.key()).fetch(10)

        notifications = []

        for e in circle_owned:
            t = 'request_circle'
            if e.requests:
                first = User.get(e.requests[0])
                plus_more = len(e.requests) - 1
                notifications.append({
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
            t = 'new_event'
            notifications.append({
                'type': t,
                'message': noti[t]['template'].format(
                    e.key().id(),
                    e.name,
                    e.circle.key().id(),
                    e.circle.name
                )
            })

        for p in pass_join:
            t = 'passenger_joined'
            notifications.append({
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
            t = 'ride_offered'
            today = date.today()
            rides_offered = Ride.all().filter('event =', r.event).fetch(None)
            if r.event.date >= today and len(rides_offered):
                notifications.append({
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

class HomeHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        user.created_str = user.created.strftime('%B %dth, %Y')

        today = datetime.date.today()

        notis = Notification.all().filter('created >= ', today).filter('user = ', user.key()).fetch(10)

        invites = Invite.all().filter('user = ', user.key()).fetch(10)

        
        upcoming_pass = Passenger.all().filter('created >= ', today).filter('user =', user.key()).fetch(10)
        upcoming = Ride.all().filter('date >= ', today).filter('driver =', user.key()).fetch(10)

        rides_driving = Ride.all().filter('date >= ', today).filter('driver =', user.key()).fetch(10)
        
        passenger_joined = Passenger.all().filter('created >= ', today).filter('ride in', rides_driving).fetch(10)

        site_notifications = []
        ride_alerts = []

        # Create object
        for up in upcoming:
            up.orig = split_address(up.origin_add)
            up.dest = split_address(up.dest_add)
            obj = {
                'message': '<strong>Driver of</strong>: <a href="/ride/' + str(up.key().id()) + '">' + up.orig + ' to ' + up.dest + '</a>',
                'date': up.date_str,
                'details': False,
                'driver': True,
                'type': 'Upcoming Ride'
            }
            if up.circle:
                obj['circle'] = {
                    'name': up.circle.name,
                    'id': up.circle.key().id()
                }
            ride_alerts.append(obj)

        for upp in upcoming_pass:
            upp.ride.orig = split_address(upp.ride.origin_add)
            upp.ride.dest = split_address(upp.ride.dest_add)
            obj = {
                'message': '<strong>Passenger of</strong>: <a href="/ride/' + str(upp.ride.key().id()) + '">' + upp.ride.orig + ' to ' + upp.ride.dest + '</a>',
                'date': upp.ride.date_str,
                'passenger': True,
                'type': 'Upcoming Ride'          
            }
            if upp.ride.circle:
                obj['circle'] = {
                    'name': upp.ride.circle.name,
                    'id': upp.ride.circle.key().id()
                }
            ride_alerts.append(obj)

        # Format data
        for noti in notis:
            if noti.type == 'driver_leave':
                noti.message = """
                The driver has left this ride.
                """
            elif noti.type == 'driver_join':
                noti.message = """
                A driver has joined this ride.
                """
            elif noti.type == 'pass_leave':
                noti.message = """
                A passenger has left this ride.
                """
            elif noti.type == 'pass_join':
                noti.message = """
                A passenger has joined this ride.
                """
            elif noti.type == 'edited':
                noti.message = """
                Your ride has been edited.
                """
            elif noti.type == 'circle_message':
                noti.message = noti.text

            if noti.ride:
                noti.ride.orig = split_address(noti.ride.origin_add)
                noti.ride.dest = split_address(noti.ride.dest_add)

            noti.created_str = noti.created.strftime('%B %dth, %Y')

        # Create object
        for noti in notis:
            if noti.type in ['request', 'circle_message']:
                mtype = None
                if noti.type == 'circle_message':
                    mtype = 'Message from Admin'
                obj = {
                    'message': noti.message,
                    'date': noti.created_str,
                    'circle': {
                        'name': noti.circle.name,
                        'id': noti.circle.key().id()
                    },
                    'type': mtype
                }

                site_notifications.append(obj)
            elif noti.type == 'request':
                pass
            else:
                obj = {
                    'message': noti.message,
                    'date': noti.ride.date_str,
                    'details': {
                        'message': noti.ride.orig + ' to ' + noti.ride.dest,
                        'id': noti.ride.key().id()
                    },
                    'driver': False,
                    'pass': False,
                    'type': 'Notification'
                }
                ride_alerts.append(obj)

        for invite in invites:
            obj = {
                'message': """
                    You have been invited to <a href='/circle/{}'>{} circle</a>.
                """ % (invite.circle.key().id(), invite.circle.name),
                'circle': {
                    'name': invite.circle.name,
                    'id': invite.circle.key().id()
                },
                'invited_by': {
                    'name': invite.sender.name,
                    'id': invite.sender.key().id()
                }
            }

        for p in passenger_joined:
            if p.ride:
                p.ride.orig = split_address(p.ride.origin_add)
                p.ride.dest = split_address(p.ride.dest_add)

            obj = {
                'message': """
                <a href='/user/{}'>{}</a> has joined this ride.
                """ % (p.user.key().id(), p.user.name),
                'submessage': p.message,
                'date': None,
                'details': {
                    'message': p.ride.orig + ' to ' + p.ride.dest,
                    'id': p.ride.key().id()
                },
                'type': 'Notification'
            }

            ride_alerts.append(obj)

        circles = Circle.all().fetch(None)

        for circle in circles:
            if circle.key() in user.circles:
                circle.user = True
            else:
                circle.user = False

        # ride_alerts.sort(key=lambda x:x['date'])
        # site_notifications.sort(key=lambda x:x['date'])

        doRender(self, 'home.html', { 
            'user': user,
            'circles': circles,
            'ride_alerts': ride_alerts,
            'site_notis': site_notifications
        })