from app.common.toolbox import doRender
from google.appengine.ext import db
from google.appengine.api import files, images
from google.appengine.ext.webapp import blobstore_handlers
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

class GetImage(BaseHandler):
	def get(self, user_id):
		user = User.get_by_id(int(user_id))
		self.redirect(images.get_serving_url(user.photo))
		# blobstore_handlers.BlobstoreDownloadHandler.send_blob(user.photo)

class NotificationUserHandler(BaseHandler):
	def get(self, user_id):
		self.auth()
		user = self.current_user()

		doRender(self, 'notification_user.html', {
			'user': user
		})

	def post(self, user_id):
		self.auth()

		json_str = self.request.body
		data = json.loads(json_str)

		user = self.current_user()

		if not user.key().id() == int(user_id):
			self.redirect('/user/' + user_id)
			return None
		else:
			user.noti_type = data['type']
			user.noti_time = int(data['time'])
			user.put()

			resp = {
				'message': 'Updated!'
			}

			self.response.write(json.dumps(resp))

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
		user.name = data['name']
		user.email = data['email']
		user.phone = data['phone']

		if not user.key().id() == int(user_id):
			self.redirect('/user/' + user_id)
			return None
		else:
			if 'photo' in data and len(data['photo']) > 0:
				d64 = re.search(r'base64,(.*)', data['photo']).group(1)
				decoded = d64.decode('base64')

				# decoded = data['photo'].decode('base64')

				file_name = files.blobstore.create(mime_type='image/png')

				with files.open(file_name, 'a') as f:
					f.write(decoded)

				files.finalize(file_name)

				key = files.blobstore.get_blob_key(file_name)
				user.photo = str(key)
				print key

		user.put()

		resp = {
			'message': 'Edited!'
		}

		self.response.write(json.dumps(resp))

class UserHandler(BaseHandler):
	def get(self):
		self.auth()
		user = self.current_user()

		user.created_str = user.created.strftime('%B %dth, %Y')

		doRender(self, 'view_user.html', {
			'user': user
		})