from app.model import *
import datetime
from datetime import date

class Notifications:
	def __init__(self):
		self.templates = {
			'new_event': { # /
				'symbol': 'location-arrow',
				'template': '<a href="/event/{}">{}</a> has been added to <a href="/circle/{}">{}</a>',
				'title': 'New Event'
			},
			'request_circle': { # /
				'symbol': 'question',
				'template': '<a href="/user/{}">{}</a> and {} other people have requested to join <a href="/circle/{}">{}</a>',
				'title': 'Request for Circle'
			},
			'invite_circle': { # X
				'symbol': 'plus-square-o',
				'template': '<a href="/user/{}">{}</a> has invited you to join <a href="/circle/{}">{}</a>',
				'title': 'Invite to Circle'
			},
			'passenger_joined': { # /
				'symbol': 'users',
				'template': '<a href="/user/{}">{}</a> and {} other people have joined your ride <a href="/ride/{}">from {} to {}</a> as a passenger',
				'title': 'Passenger Joined'
			},
			'driver_joined': { # /
				'symbol': 'thumbs-up',
				'template': '<a href="/user/{}">{}</a> has joined your ride <a href="/ride/{}">from {} to {}</a> as a driver',
				'title': 'Driver Joined'
			},
			'ride_offered': { # X
				'symbol': 'thumbs-up',
				'template': '{} ride(s) are offered to <a href="/event/{}">{}</a>.',
				'title': 'Ride Offered'
			},
			'ride_updated': { # /
				'symbol': 'exclamation',
				'template': '<a href="/ride/{}">from {} to {}</a> has been updated',
				'title': 'Ride Updated'
			},
			'circle_message': {
				'symbol': 'envelope',
				'template': '<a href="/circle/{}">{}</a> says {}',
				'title': 'New Circle Message'
			}
		}
	def get_all(self, circle=None, user=None):
		today = date.today()
		notifications = []

		if circle == None:
			events = Event.all().filter('circle in', user.circles) \
			.filter('date >=', today).fetch(10)
		else:
			events = Event.all().filter('circle =', circle) \
			.filter('date >=', today).fetch(10)


		for e in events:
			if e.key() not in user.notis:
				t = 'new_event'
				notifications.append({
					'id': e.key(),
					'type': t,
					'message': self.templates[t]['template'].format(
						e.key().id(),
						e.name,
						e.circle.key().id(),
						e.circle.name
					)
				})

		if circle == None:
			driving = Ride.all().filter('driver =', user.key()) \
			.filter('date >=', today).fetch(10)
		else:
			driving = Ride.all().filter('driver =', user.key()) \
			.filter('date >=', today).filter('circle =', circle).fetch(10)

		pass_join = Passenger.all().filter('ride in', driving).fetch(10)

		for p in pass_join:
			if p.key() not in user.notis:
				if circle and p.ride.circle.key() == circle:
					t = 'passenger_joined'
					notifications.append({
						'id': p.key(),
						'type': t,
						'message': self.templates[t]['template'].format(
							p.user.key().id(),
							p.user.name,
							0,
							p.ride.key().id(),
							p.ride.origin_add,
							p.ride.dest_add
						)
					})

		requests = Requester.all().filter('user = ', user.key()).fetch(10)

		for r in requests:
			if r.key() not in user.notis:
				if circle and r.event.circle.key() == circle:
					t = 'ride_offered'
					today = date.today()
					rides_offered = Ride.all().filter('event =', r.event).fetch(None)
					if r.event.date >= today and len(rides_offered):
						notifications.append({
							'id': r.key(),
							'type': t,
							'message': self.templates[t]['template'].format(
								len(rides_offered),
								r.event.key().id(),
								r.event.name
							)
						})

		circle_owned = Circle.all().filter('admins =', user.key()).fetch(10)

		for e in circle_owned:
			if e.key() not in user.notis:
				if circle and e.key() == circle:
					t = 'request_circle'
					if e.requests:
						first = User.get(e.requests[0])
						plus_more = len(e.requests) - 1
						notifications.append({
							'id': e.key(),
							'type': t,
							'message': self.templates[t]['template'].format(
								first.key().id(),
								first.name,
								plus_more,
								e.key().id(),
								e.name
							)
						})

		if circle:
			messages = Messages.all().filter('circle =', circle).fetch(10)
		else:
			messages = Messages.all().filter('circle in', user.circles).fetch(10)

		for e in messages:
			if e.key() not in user.notis:
				t = 'circle_message'
				notifications.append({
					'id': e.key(),
					'type': t,
					'message': self.templates[t]['template'].format(
						e.circle.key().id(),
						e.circle.name,
						e.message
					)
				})

		for n in notifications:
			n['title'] = self.templates[n['type']]['title']
			n['symbol'] = self.templates[n['type']]['symbol']

		return notifications