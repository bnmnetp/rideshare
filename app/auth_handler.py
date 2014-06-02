import webapp2
from simpleauth import SimpleAuthHandler
from app import secrets
from app.model import *

from app.base_handler import BaseHandler

class AuthHandler(BaseHandler, SimpleAuthHandler):
    def _on_signin(self,  data, auth_info, provider):
        auth_id = '%s:%s' % (provider, data['id'])
        user_D = User.gql('WHERE auth_id = :id', id = auth_id).get()

        if user_D:
            self.session['user'] = user_D.key().id()
        else:
            user = User()
            user.auth_id = auth_id
            user.name = 'Replace'
            user.id = '123'
            user.put()
        self.redirect('/map')
    def logout(self):
        self.session['user'] = None
        self.redirect('/')
    def _callback_uri_for(self, provider):
        return self.uri_for('auth_callback', provider = provider, _full = True)
    def _get_consumer_info_for(self, provider):
        return secrets.AUTH_CONFIG[provider]