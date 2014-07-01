from app.common.toolbox import doRender
from google.appengine.ext import db
from google.appengine.api import search
from app.model import *
import datetime
from datetime import date
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json
import re

class SendInvite(BaseHandler):
    def post(self, circle_id):
        self.auth()

        user = self.current_user()

        json_str = self.request.body
        data = json.loads(json_str)

        print data['emails']

        email_list = data['emails'].split(',')

        email_regex = re.compile(r'[^@]+@[^@]+\.[^@]+')
        resp = {
            'invalid': [],
            'valid': []
        }
        for email in email_list:
            if email_regex.match(email):
                resp['valid'].append(email)
            else:
                resp['invalid'].append(email)

        for email in resp['valid']:
            print email

        self.response.write(json.dumps(resp))

class GetNames(BaseHandler):
	def get(self):
		self.auth()

		name = self.request.get('q')

		index = search.Index(name='User')

		users = index.search(name)

		user_dict = [u.to_dict() for u in users]

		self.response.write(json.dumps(user_dict))