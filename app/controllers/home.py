from app.common.toolbox import doRender, grab_json, split_address
from google.appengine.ext import db
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json
from app.model import *
import datetime
from datetime import date

class HomeHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        notis = Notification.all().filter('user = ', user.key()).fetch(100)

        invites = Invite.all().filter('user = ', user.key()).fetch(100)

        today = datetime.date.today()
        upcoming_pass = Ride.all().filter('date > ', today).filter('passengers =', user.key()).fetch(20)
        upcoming_drive = Ride.all().filter('date > ', today).filter('driver =', user.key()).fetch(20)
        upcoming = upcoming_pass + upcoming_drive

        site_notifications = []
        ride_alerts = []

        # Format data
        for up in upcoming:
            up.orig = split_address(up.origin_add)
            up.dest = split_address(up.dest_add)
            up.is_pass = False
            if user.key() in up.passengers:
                up.is_pass = True

            up.is_driver = False
            if up.driver:
                if user.key() == up.driver.key():
                    up.is_driver = True

            up.date_str = up.date.strftime('%B %dth, %Y')

        for up in upcoming:
            obj = {
                'message': '<a href="/ride/' + str(up.key().id()) + '">' + up.orig + ' to ' + up.dest + '</a>',
                'date': up.date_str,
                'details': False,
                'driver': up.is_driver,
                'pass': up.is_pass,
                'type': 'Upcoming Ride',
            }
            if up.circle:
                obj['circle'] = {
                    'name': up.circle.name,
                    'id': up.circle.key().id()
                }
            ride_alerts.append(obj)

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
            elif noti.type == 'request':
                noti.message = 'A person has requested to join this circle.'
            elif noti.type == 'circle_message':
                noti.message = noti.text
            if noti.ride:
                noti.ride.orig = split_address(noti.ride.origin_add)
                noti.ride.dest = split_address(noti.ride.dest_add)

            noti.created_str = noti.created.strftime('%B %dth, %Y')

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
            else:
                obj = {
                    'message': noti.message,
                    'date': noti.created_str,
                    'details': {
                        'message': noti.ride.orig + ' to ' + noti.ride.dest,
                        'id': noti.ride.key().id()
                    },
                    'driver': False,
                    'pass': False,
                    'type': 'Notification'
                }
                ride_alerts.append(obj)

        circles = Circle.all().fetch(100)

        for circle in circles:
            if circle.key() in user.circles:
                circle.user = True
            else:
                circle.user = False

        print site_notifications
        doRender(self, 'home.html', { 
            'user': user,
            'circles': circles,
            'ride_alerts': ride_alerts,
            'site_notis': site_notifications
        })