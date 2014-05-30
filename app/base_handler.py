import webapp2
from webapp2_extras import sessions
from app.model import *

class BaseHandler(webapp2.RequestHandler):
    @property
    def current_user(self):
        id = self.session.get('user')
        if id:
            user = User.gql('WHERE id = :id', id = id).get()
            return user
        else:
            return None

    def create_context(self):
        cd = {}

        if self.current_user:
            cd['nickname'] = self.current_user.name
            cd['public_link'] = self.current_user.public_link
            cd['logout_url'] = "/auth/logout"
            cd['isuser'] = True
        else:
            cd['login_url'] = "/auth/login"
            cd['isuser'] = False
        return cd

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()