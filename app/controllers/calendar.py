from app.common import toolbox
from google.appengine.ext import db
from app.model import *
from google.appengine.api import mail
import datetime
from datetime import date
import json
from app.base_handler import BaseHandler
from app.common.voluptuous import *
from app.common.email_sys import sender

class GetCalendar(BaseHandler):
	def get(self):
		self.auth()

		today = date.today()

		rides = []

		user = self.current_user()

		driving = Ride.all().filter('driver =', user.key()).fetch(None)
		for d in driving:
			check_for_passengers = Passenger.all().filter('ride =', d).fetch(1)
			if check_for_passengers:
				border = '#1565C0'
			else:
				border = '#90CAF9'
			rides.append({
				'title': d.event.name + ' - Driver',
				'start': str(d.date),
				'url': '/ride/' + str(d.key().id()),
				'color': border
			})

		requester = Requester.all().filter('user =', user.key()).fetch(None)
		for r in requester:

			rides.append({
				'title': r.event.name + ' - Requested',
				'start': str(r.event.date),
				'url': '/event/' + str(r.event.key().id()),
				'color': '#81c784'
			})

		passengers = Passenger.all().filter('user =', user.key()).fetch(None)
		for p in passengers:
			if p.ride.date >= today:
				if p.ride.driver:
					border = '#2e7d32'
				else:
					border = '#81c784'
				rides.append({
					'title': p.ride.event.name + ' - Passenger',
					'start': str(p.ride.date),
					'url': '/ride/' + str(p.ride.key().id()),
					'color': border
				})

		toolbox.render(self, 'calendar.html', {
			'user': user,
			'rides': json.dumps(rides)
		})