from app.common.toolbox import doRender, grab_json
from google.appengine.ext import db
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json
from app.model import *
from app.common.email_sys import sender
from app.common.encryption import bcrypt
from app.common.email import send_invite, send_email

import uuid

class OrgLogin(BaseHandler):
    def get(self, slug):
        print slug
        org = Org.all().filter('slug =', slug).get()
        if not org:
            return self.redirect('/')

        doRender(self, 'accounts/orglogin.html', {
            'org': org
        })

class LoginHandler(BaseHandler):
    def get(self):
        if self.current_user():
            self.redirect('/home')
        else:
            if 'redirect' in self.session:
                redirect = self.session['redirect']
            else:
                redirect = None
            doRender(self, 'loginPage.html', {
                'redirect': redirect
            })
    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        login_validator = Schema({
            Required('email'): unicode,
            Required('password'): unicode,
            'org': unicode
        })

        user = User.all().filter('email_account = ', data['email']).get()

        if not user:
            return self.json_resp(500, {
                'message': 'Email/password is wrong.'
            })

        if data['org'] != '':
            org = Org.get_by_id(int(data['org']))
            if not org.email in data['email']:
                return self.json_resp(500, {
                    'message': 'Email/password is wrong.'
                })

        if bcrypt.hashpw(data['password'], user.password) == user.password:
            self.session['user'] = user.key().id()
            # check_for_invite(self, user)
            return self.json_resp(200, {
                'message': 'You have logged in.',
                'redirect': self.login_redirect(user)
            })
        else:
            return self.json_resp(500, {
                'message': 'Email/password is wrong.'
            })

class RegisterHandler(BaseHandler):
    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        login_validator = Schema({
            Required('email'): unicode,
            Required('password'): unicode,
            'org': unicode
        })

        has_org = False
        if data['org'] != '':
            org = Org.get_by_id(int(data['org']))
            if not org.email in data['email']:
                return self.json_resp(500, {
                    'message': 'Your email is not apart of this organization!'
                })
            else:
                has_org = True

        hashed = bcrypt.hashpw(data['password'], bcrypt.gensalt())

        user = User()
        user.email_account = data['email']
        user.email = data['email']
        user.name = data['name']
        user.password = hashed
        user.put()

        if has_org:
            user.circles.append(org.circle.key())
            user.put()

        self.session['user'] = user.key().id()
        # check_for_invite(self, user)
        return self.json_resp(200, {
            'message': 'Account created',
            'redirect': self.login_redirect(user)
        })

class PasswordReset(BaseHandler):
    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        reset_validator = Schema({
            Required('email'): unicode
        })

        try:
            data = reset_validator(data)
        except MultipleInvalid as e:
            return self.json_resp(500, {
                'error': str(e),
                'message': 'Email could not be validated'
            })

        user = User.all().filter('email =', data['email']).get()
        user.hash = str(uuid.uuid4()).replace('-', '')
        user.put()
        print(user.hash)
        if user != None:
            send_email(user, 'Password Reset', 'emails/password_reset.html', {
                'reset_hash': user.hash
            })
            return self.json_resp(200, {
                'message': 'Reset email sent!'
            })
        else:
            # Security measure
            return self.json_resp(200, {
                'message': 'Reset email sent!'
            })

class NewPassword(BaseHandler):
    def get(self, hash):
        pass
    def post(self, hash):
        pass