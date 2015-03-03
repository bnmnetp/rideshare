import webapp2
from webapp2_extras import sessions
from webapp2_extras import sessions_memcache
from app.model import *
import urllib
import json

class BaseHandler(webapp2.RequestHandler):
    def auth(self):
        id = self.session.get('user')
        if id:
            user = User.get_by_id(int(id))
        else:
            user = None

        if user:
            return None
        else:
            if self.request.method == 'GET':
                self.session['redirect'] = self.request.path
            redirect_str = '/login?'
            if 'invited' in self.session:
                redirect_str += 'invited=' + self.session['invited']
            return webapp2.redirect(redirect_str, False, True)

    def current_user(self):
        id = self.session.get('user')
        if id and id != None:
            return User.get_by_id(id)
        else:
            return None

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    def json_resp(self, code, ctx):
        self.response.set_status(code)
        self.response.write(json.dumps(ctx))
        return None

    @webapp2.cached_property
    def session(self):
        self.session_store = sessions.get_store(request=self.request)
        # Returns a session using the default cookie key.
        return self.session_store.get_session(name='mc_session',
        factory=sessions_memcache.MemcacheSessionFactory)

    def circle(self):
        user = self.current_user()
        if 'circle' in self.session and self.session['circle'] != None:
            circle = Circle.get_by_id(int(self.session['circle']))
            if not circle:
                if user.circles:
                    circle_key = user.circles[0]
                    circle = Circle.get(circle_key)
                    self.session['circle'] = circle.key().id()
                else:
                    circle = None
        else:
            if user.circles:
                circle_key = user.circles[0]
                circle = Circle.get(circle_key)
                self.session['circle'] = circle.key().id()
            else:
                circle = None
        return circle

    def login_redirect(self, user):
        redirect_str = '/home'
        redirect = self.session.get('redirect')
        if redirect:
            redirect_str = str(redirect)
            self.session['redirect'] = None
        else:
            if user.email == '' or user.name == '':
                redirect_str = '/user/edit/' + str(user.key().id())

        return redirect_str