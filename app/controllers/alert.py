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
	def post(self, alert_id):
		self.auth()

		alert = Notification.get_by_id(int(alert_id))

		if not alert:
			return self.json_resp(500, {
				'message': 'Notification does not exist'
			})
		else:
			alert.delete()
			
			return self.json_resp(200, {
				'message': 'Notification dismissed.'
			})