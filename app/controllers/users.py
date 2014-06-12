from app.common.toolbox import doRender
from google.appengine.ext import db
from app.model import *
import datetime
from datetime import date
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json

class GetUserHandler(BaseHandler):
	def get(self, user_id):
		self.auth()
		user = User.get_by_id(int(user_id))
		comments = Comment.all().filter('profile = ', user.key()).order('-date').fetch(100)

		doRender(self, 'view_user.html', {
			'user': user,
			'comments': comments
		})

class UserHandler(BaseHandler):
	def get(self):
		self.auth()
		user = self.current_user()
		comments = Comment.all().filter('profile = ', user.key()).order('-date').fetch(100)

		doRender(self, 'view_user.html', {
			'user': user,
			'comments': comments
		})