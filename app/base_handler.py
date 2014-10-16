import webapp2
from webapp2_extras import sessions
from app.model import *
import urllib
import json

class BaseHandler(webapp2.RequestHandler):
    def auth(self):
        id = self.session.get('user')
        self.session['redirect'] = self.request.path
        if id and id != None:
            user = User.get_by_id(id)
            if not user:
                return webapp2.redirect('/', False, True)
        else:
            return webapp2.redirect('/', False, True)

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
        return self.session_store.get_session()

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
            redirect_str = redirect
            self.session['redirect'] = None
        else:
            if user.phone == None or user.email == None or user.zip == None:
                redirect_str = '/user/edit/' + str(user.key().id())
        return redirect_str