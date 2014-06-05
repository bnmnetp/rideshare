import json
from google.appengine.ext import db
from app.model import *
import datetime

class CommentHandler(BaseHandler):
	def post(self):
		self.auth()

		user = self.current_user()

		json_str = self.request.body
		data = json.loads(json_str)

		comment = Comment()
		comment.user = user.key()
		comment.date = datetime.date()
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

		self.response.write(json.dump({
			'message': 'Success'
		}))
