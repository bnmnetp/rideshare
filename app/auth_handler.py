import webapp2
from simpleauth import SimpleAuthHandler
from app import secrets

class AuthHandler(webapp2.RequestHandler, SimpleAuthHandler):
    def _on_signin(self,  data, auth_info, provider):
        auth_id = '%s:%s' % (provider, data['id'])
        user = User.get_auth_id(
            'auth_id',
        )

        if user:
            self.auth.set_session(user.id)
        else:
            user = User()
            user.auth_id = auth_id
            user.put()
    def logout(self):
        self.auth.unset_session()
        self.redirect('/')
    def _callback_uri_for(self, provider):
        return self.uri_for('auth_callback', provider = provider, _full = True)
    def _get_consumer_info_for(self, provider):
        return secrets.AUTH_CONFIG[provider]