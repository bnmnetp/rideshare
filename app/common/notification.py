from google.appengine.ext import db
from app.model import *

from datetime import timedelta, datetime

def push_noti(type, user_key, ride_key,):
	if type == 'driver_leave':
		message = 'The driver has left this ride.'
	elif type == 'driver_join':
		message = 'A driver has joined this ride.'
	elif type == 'pass_leave':
		message = 'X is no longer a passenger.'
	elif type == 'pass_join':
		message = 'X is now a passenger of this ride.'
	noti = Notification()
	noti.text = message
	noti.ride = ride_key
	noti.user = user_key
	noti.put()

	user = User.get(user_key)
	ride = Ride.get(ride_key)

	if user.noti_time != 0:
		today = datetime.today().date()
		day_until = (ride.date - today).days
		if days_until < user.noti_time:
			print 'send notificaiton'