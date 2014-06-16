from google.appengine.ext import db
from app.model import *

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