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
				d64 = re.search(r'base64,(.*)', data).group(1)
				decoded = d64.decode('base64')

				file_name = files.blobstore.create(mime_type='image/png')

				with files.open(file_name, 'a') as f:
					f.write(decoded)

				files.finalize(file_name)

				key = files.blobstore.get_blob_key(file_name)
				user.photo = key
				print key

		user.put()

class UserHandler(BaseHandler):
	def get(self):
		self.auth()
		user = self.current_user()

		doRender(self, 'view_user.html', {
			'user': user
		})