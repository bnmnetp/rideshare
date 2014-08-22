from google.appengine.ext import db
from app.model import *
from app.common.email import send_email

from datetime import timedelta, datetime

def push_noti(type, user_key, ride_key = None, circle_key = None):
	if type == 'driver_leave':
		message = """
		The driver has left this ride.
		"""
	elif type == 'driver_join':
		message = """
		A driver has joined this ride.
		"""
	elif type == 'pass_leave':
		message = """
		<a href='/user/%s'>%s</a> is no longer a passenger.
		""" % (user.key().id(), user.name)
	elif type == 'pass_join':
		message = """
		<a href='/user/%s'>%s</a> is now a passenger of this ride.
		""" % (user.key().id(), user.name)
	elif type =='edited':
		message = """
		Your ride has been edited.
		"""

	noti = Notification()
	noti.ride = ride_key
	noti.user = user_key
	noti.circle = circle_key
	noti.type = type
	noti.put()

	if user.noti_time != 0:
		today = datetime.today().date()
		days_until = (ride.date - today).days
		if days_until <= user.noti_time:
			if user.noti_type == 'email' and user.email:
				send_email(
					user,
					'Notification from Rideshare',
					'emails/notification.html',
					{
						'message': message,
						'user_name': user.name,
						'community_name': '',
						'rideshare_url': 'http://rideshare-dev.appspot.com'
					}
				)