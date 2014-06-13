import json
from google.appengine.ext import db
from app.model import *
import datetime
from app.base_handler import BaseHandler
from app.common import voluptuous

def get_key(id, type):
	key = ''
	if type == 'ride':
		ride = Ride.get_by_id(id)
		key = ride.key()
	elif type == 'event':
		event = Event.get_by_id(id)
		key = event.key()
	elif type == 'circle':
		circle = Circle.get_by_id(id)
		key = circle.key()
	elif type == 'profile':
		user = User.get_by_id(id)
		key = user.key()
	return key

class CommentHandler(BaseHandler):
	def post(self):
		self.auth()

		user = self.current_user()

		json_str = self.request.body
		data = json.loads(json_str)

		d = datetime.date.today()

		comment = Comment()
		comment.user = user.key()
		comment.date = d
		comment.text = data['comment']
		if data['type'] == 'ride':
			ride = Ride.get_by_id(data['id'])
			comment.ride = ride.key()
		elif data['type'] == 'event':
			event = Event.get_by_id(data['id'])
			comment.event = event.key()
		elif data['type'] == 'circle':
			circle = Circle.get_by_id(data['id'])
			comment.circle = circle.key()
		elif data['type'] == 'profile':
			user = User.get_by_id(data['id'])
			comment.profile = user.key()
		comment.put()

		self.response.write(json.dumps({
			'message': 'Success',
			'name': user.name,
			'date': str(d),
			'comment': comment.text
		}))

class FetchComments(BaseHandler):
	def post(self):
		self.auth()

		user = self.current_user()

		json_str = self.request.body
		data = json.loads(json_str)

		key = get_key(data['id'], data['type'])

		comments = Comment.all().filter(data['type'] + " = ", key).order('-date').fetch(25)

		for comment in comments:
			if comment.user == user.key():
				comment.is_owner = True
			else:
				comment.is_owner = False

		resp = json.dumps([c.to_dict() for c in comments])

		self.response.write(resp)

