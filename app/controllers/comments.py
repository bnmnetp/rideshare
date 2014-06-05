import json
from google.appengine.ext import db
from app.model import *
import datetime
from app.base_handler import BaseHandler

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

		comment.put()

		self.response.write(json.dumps({
			'message': 'Success',
			'name': user.name,
			'date': str(d),
			'comment': comment.text
		}))