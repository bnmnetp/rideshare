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

class ViewInvites(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        invites = Invite.all().filter('user = ', user.key()).fetch(100)

        doRender(self, 'view_invites.html', {
            'invites': invites,
            'user': user
        })

    def post(self):
        self.auth()

        user = self.current_user()

        invite = Invite.all().filter('user = ', user.key()).get()

        if not invite:
            self.response.status(500)
            self.response.write(json.dumps({
                'error': 'You have no pending invites'
            }))
            return None

        user.circles.append(invite.circle.key())

        invite.delete()

        self.response.write(json.dumps({
            'message': 'You have joined the circle'
        }))

class SendInvite(BaseHandler):
    def get(self, invite_id):
        invite = Invite.get_by_id(int(invite_id))

        doRender(self, 'view_invite.html', {
            'invite': invite
        })
    def post(self, circle_id):
        self.auth()

        user = self.current_user()

        json_str = self.request.body
        data = json.loads(json_str)

        circle = Circle.get_by_id(int(circle_id))

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
            invite = Invite()
            invite.circle = circle.key()
            invite.email = email
            invite.sender = user.key()
            invite.put()

        self.response.write(json.dumps(resp))

class SendInviteName(BaseHandler):
    def post(self, circle_id):
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        json_str = self.request.body
        ids = json.loads(json_str)

        print ids

        for id in ids:
            user_send = User.get_by_id(int(id))

            if user_send:

                invite = Invite()
                invite.circle = circle.key()
                invite.user = user_send
                invite.sender = user.key()
                invite.put()

            if user_send.email:
                print 'Email Sent!'

        self.response.write(json.dumps({
            'message': 'Success'
        }))

class JoinCircleInvite(BaseHandler):
    def post(self):
        print 'temp'

class GetNames(BaseHandler):
	def get(self):
		self.auth()

		users = User.all().fetch(100)

		user_dict = [u.to_dict() for u in users]

		self.response.write(json.dumps(user_dict))