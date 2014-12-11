from app.common.toolbox import doRender, grab_json, split_address, date_display
from google.appengine.ext import db
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json
from app.model import *
import datetime
from datetime import date

# class HomeHandler(BaseHandler):
#     def get(self):
#         self.auth()
#         user = self.current_user()

#         today = datetime.date.today()

#         # What do we need to grab
#         # upcoming rides, driver or passenger
#         # if a passenger joins your ride
#         # if you are passenger: ride has or does not have driver
#         # message sent to circle, display for one week

#         upcoming_pass = Passenger.all()'created >= ', today).filter('user = ', user.key()).fetch(10)
#         upcoming_ride = Ride.all().filter('date >= ', today).filter('driver =', user.key()).fetch(10)

#         joined_pass = Passenger.all().filter('created >= ', today).filter('ride in', upcoming_ride).fetch(10)

#         site_notifications = []
#         ride_alerts = []

#         for u in upcoming_ride:
#             u.orig = split_address(u.origin_add)
#             u.dest = split_address(u.dest_add)
#             obj = {
#                 'message': '<strong>Driver of</strong>: <a href="/ride/' + str(u.key().id()) + '">' + u.orig + ' to ' + u.dest + '</a>',
#                 'date': date_display(u.date),
#                 'details': False,
#                 'driver': True,
#                 'type': 'Upcoming Ride'
#             }
#             if u.circle:
#                 obj['circle'] = {
#                     'name': u.circle.name,
#                     'id': u.circle.key().id()
#                 }
#             ride_alerts.append(obj)

#         for u in upcoming_pass:
#             u.ride.orig = split_address(u.ride.origin_add)
#             u.ride.dest = split_address(u.ride.dest_add)
#             obj = {
#                 'message': '<strong>Passenger of</strong>: <a href="/ride/' + str(u.ride.key().id()) + '">' + u.ride.orig + ' to ' + u.ride.dest + '</a>',
#                 'date': date_display(u.ride.date),
#                 'passenger': True,
#                 'type': 'Upcoming Ride'          
#             }
#             if upp.ride.circle:
#                 obj['circle'] = {
#                     'name': u.ride.circle.name,
#                     'id': u.ride.circle.key().id()
#                 }
#             ride_alerts.append(obj)

class HomeHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        today = datetime.date.today()

        notis = Notification.all().filter('created >= ', today).filter('user = ', user.key()).fetch(10)

        invites = Invite.all().filter('user = ', user.key()).fetch(10)

        
        upcoming_pass = Passenger.all().filter('created >= ', today).filter('user =', user.key()).fetch(10)
        upcoming = Ride.all().filter('date >= ', today).filter('driver =', user.key()).fetch(10)

        rides_driving = Ride.all().filter('date >= ', today).filter('driver =', user.key()).fetch(10)
        
        passenger_joined = Passenger.all().filter('created >= ', today).filter('ride =', rides_driving).fetch(10)

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
                    You have been invited to <a href='/circle/%s'>%s circle</a>.
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
                <a href='/user/%s'>%s</a> has joined this ride.
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