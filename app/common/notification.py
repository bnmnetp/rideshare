from google.appengine.ext import db
from app.model import *

def NotificationSet(self, user_key, ride_key, type):
	if type == 'driver_left':
		message = 'The driver has left this ride.'
	elif type == 'driver_join':
		message = 'A driver has joined this ride.'
	elif type == 'pass_left':
		message = 'X is no longer a passenger.'
	elif type == 'pass_join':
		message = 'X is now a passenger of this ride.'
	noti = Notification()
	noti.message = message
	noti.ride = ride_key
	noti.user = user_key
	noti.put()