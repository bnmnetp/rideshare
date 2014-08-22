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

        notis = Notification.all().filter('user = ', user.key()).fetch(10)

        today = datetime.date.today()
        upcoming = Ride.all().filter('date > ', today).fetch(20)

        for up in upcoming:
            up.dest_add = split_address(up.dest_add)
            if user.key() in up.passengers:
                up.is_pass = True
            else:
                up.is_pass = False

            up.is_driver = False
            if up.driver:
                if user.key() == up.driver.key():
                    up.is_driver = True

            up.date_str = up.date.strftime('%B %dth, %Y')

        for noti in notis:
            noti.ride.orig = split_address(noti.ride.origin_add)
            noti.ride.dest = split_address(noti.ride.dest_add)

        circles = Circle.all().fetch(100)

        for circle in circles:
            if circle.key() in user.circles:
                circle.user = True
            else:
                circle.user = False

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
            elif noti.type == 'circle message':
                noti.message = noti.text

            if noti.ride:
                noti.ride_details = Ride.get(noti.ride)
                noti.ride_details.orig = split_address(noti.ride_details.origin_add)
                noti.ride_details.dest = split_address(noti.ride_details.dest_add)

            if noti.circle:
                noti.circle_details = Circle.get(noti.circle)

        doRender(self, 'home.html', { 
            'user': user,
            'notis': notis,
            'upcoming': upcoming,
            'circles': circles
        })