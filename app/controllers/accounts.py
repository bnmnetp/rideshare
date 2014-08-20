from app.common.toolbox import doRender, grab_json
from google.appengine.ext import db
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json

from app.common.encryption import bcrypt

class LoginHandler(BaseHandler):
    def get(self):
        if self.current_user():
            self.redirect('/home')
        else:
            redirect = self.request.get('redirect', default_value='')
            doRender(self, 'loginPage.html', {
                'redirect': redirect
            })
    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        login_validator = Schema({
            Required('email'): unicode,
            Required('password'): unicode
        })

        user = User.filter('email_account = ', data['email']).get()

        if not user:
            return self.json_resp(200, {
                'message': 'Email/password is wrong.'
            })

        if bcrypt.hashpw(data['password'], user.password) == user.password:
            self.session['user'] = user.key().id()
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
            Required('password'): unicode
        })

        hashed = bcrypt.hashpw(data['password'], bcrypt.gensalt())

        user = User()
        user.email_account = data['email']
        user.email = data['email']
        user.password = hashed
        user.put()

        return self.json_resp(200, {
            'message': 'Account created',
            'redirect': self.login_redirect(user)
        })



