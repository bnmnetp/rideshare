from app.common.toolbox import doRender
from google.appengine.ext import db
from app.model import *
import datetime
from datetime import date
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json

import base64
import re

class GetUserHandler(BaseHandler):
	def get(self, user_id):
		self.auth()
		user = User.get_by_id(int(user_id))

		user.created_str = user.created.strftime('%B %dth, %Y')

		doRender(self, 'view_user.html', {
			'user': user
		})

class EditUserHandler(BaseHandler):
	def get(self, user_id):
		self.auth()

		user = self.current_user()

		if not user.key().id() == int(user_id):
			self.redirect('/user/' + user_id)
			return None
		else:
			doRender(self, 'edit_user.html', {
				'user': user
			})

	def post(self, user_id):
		data_pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')

		json_str = self.request.body
		data = json.loads(json_str)

		self.auth()

		user = self.current_user()

		if not user.key().id() == int(user_id):
			self.redirect('/user/' + user_id)
			return None
		else:
			if data['photo'] is not None and len(data['photo']) > 0:
				user.photo = db.Blob(base64.b64decode(data['photo']))

		user.put()
class UserHandler(BaseHandler):
	def get(self):
		self.auth()
		user = self.current_user()

		doRender(self, 'view_user.html', {
			'user': user
		})