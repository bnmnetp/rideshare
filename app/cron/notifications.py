from app.model import *
from google.appengine.ext import db
import datetime
from datetime import date

# Grab recurring rides
users = User.all().filter('time !=', 0).fetch(None)
today = datetime.today().date()

for user in users:
	where_passenger = Passenger.all().filter('user =', user.key()).fetch(None)

	for passenger in where_passenger:
		ride.time
