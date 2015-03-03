from app.common.toolbox import doRender
from google.appengine.ext import db
from app.model import *
import datetime
from datetime import date
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json
import re

class DismissAlert(BaseHandler):
	def post(self):
		self.auth()

		json_str = self.request.body
		data = json.loads(json_str)

		user = self.current_user()

		obj = db.get(str(data['id']))

		user.notis.append(obj.key())

		user.put()

		return self.json_resp(200, {
			'message': 'Notification dismissed.'
		})