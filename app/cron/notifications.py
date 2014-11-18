from app.model import *
from google.appengine.ext import db
import datetime
from app.base_handler import BaseHandler

class CheckNotifications(BaseHandler):
    def get(self):
        # Grab recurring rides
        users = User.all().filter('noti_time !=', 0).fetch(None)
        print(users)
        today = datetime.datetime.today()

        for user in users:
            where_passenger = Passenger.all().filter('user =', user.key()).fetch(None)

            for passenger in where_passenger:
                # parses time string to object
                time = datetime.datetime.strptime(passenger.ride.time, '%I:%M %p').time()
                print('time in AM/PM', time)
                full_date_time = datetime.datetime.combine(passenger.ride.date, time)
                print('full date time', full_date_time)

            where_driver = Ride.all().filter('driver =', user.key()).fetch(None)

            for ride in where_driver:
                # parses time string to object
                time = datetime.datetime.strptime(ride.time, '%I:%M %p').time()
                print('time in AM/PM', str(time))
                full_date_time = datetime.datetime.combine(ride.date, time)
                print('full date time', str(full_date_time))
                print('today', today)
                time_diff = today - full_date_time
                hours_diff = time_diff.seconds / 3600
                if hours_diff <= user.noti_time:
                    print('notify user and store a field so we do not notify again')
