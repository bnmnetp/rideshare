from app.model import *
from google.appengine.ext import db
import datetime
from datetime import date
from app.base_handler import BaseHandler

# Grab recurring rides
rides = Rides.all().filter('recurring !=', None).fetch(100)
today = datetime.today().date()

for ride in rides:
	if ride.date < today:
		if ride.recurring == 'daily':
			ride.date = ride.date + datetime.timedelta(days=1)
		if ride.recurring == 'weekly':
			ride.date = ride.date + datetime.timedelta(days=7)

		ride.put()