from app.common.toolbox import doRender, split_address, grab_json
from google.appengine.ext import db
from app.model import *
import datetime
from datetime import date
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json
import re

class EditCircle(BaseHandler):
    def get(self, circle_id):
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            self.redirect('/circles')

        properties = ['name', 'description', 'privacy', 'permission', 'color']

        circle_json = grab_json(circle, properties)
        
        doRender(self, 'edit_circle.html', {
            'user': user,
            'circle': circle,
            'circle_json': circle_json
        })
    def post (self, circle_id):
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            self.resp_json(500, {
                'message': 'Circle not found.'
            })

        circle_schema = Schema({
            Required('name'): All(unicode, Length(min=3)),
            Required('description', default=""): unicode,
            Required('privacy', default="public"): unicode,
            Required('color', default="#607d8b"): unicode,
            Required('permission'): unicode
        })

        json_str = self.request.body
        data = json.loads(json_str)

        try:
            circle_schema(data)
        except MultipleInvalid as e:
            print str(e)
            self.response.set_status(500)
            self.response.write(json.dumps({
                    'error': str(e),
                    'message': 'Data could not be validated'
                }))
            return None

        circle.name = data['name']
        circle.description = data['description']
        circle.privacy = data['privacy']
        circle.color = data['color']
        circle.permission = data['permission']

        circle.put()

        self.response.write(json.dumps({
            'message': 'Circle edited!',
            'id': circle.key().id()
        }))

class GetCircleHandler(BaseHandler):
    def get(self, circle_id):
        self.auth()

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            self.redirect('/circles')
            return None

        user = self.current_user()

        # Grabs members
        members = User.all().filter('circles = ', circle.key()).fetch(100)

        # Grabs rides
        rides = Ride.all().filter('circle = ',  circle.key()).fetch(100)

        # Grabs events
        events = Event.all().filter('circle = ', circle.key()).fetch(100)

        if circle.key() in user.circles:
            has_permission = True
        else:
            has_permission = False

        invite = Invite.all().filter('circle = ', circle.key()).filter('user = ', user.key()).get()

        if invite:
            has_permission = True

        if not has_permission:
            self.redirect('/circles')
            return None

        for ride in rides:
            ride.dest = split_address(ride.dest_add)
            ride.orig = split_address(ride.origin_add)
            if ride.driver:
                if ride.driver.key().id() == user.key().id():
                    ride.is_driver = True
                else:
                    ride.is_driver = False
            if user.key() in ride.passengers:
                ride.is_passenger = True
            else:
                ride.is_passenger = False

        if user.key() in circle.admins:
            is_admin = True
        else:
            is_admin = False

        doRender(self, 'view_circle.html', {
            'circle': circle,
            'user': user,
            'members': members,
            'rides': rides,
            'events': events,
            'invite': invite,
            'is_admin': is_admin
        })

class GetCircleInvite(BaseHandler):
    def get(self, circle_id):
        self.auth()

        circle = Circle.get_by_id(int(circle_id))

        user = self.current_user()

        doRender(self, 'view_circle_invite.html', {
            'circle': circle
        })

class CircleHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        circles = Circle.all().fetch(100)

        invites = Invite.all().filter('user = ', user.key())

        for circle in circles:
            if circle.key() in user.circles:
                circle.user = True
            else:
                circle.user = False

        doRender(self, 'circles.html', {
            'circles': circles,
            'user': user,
            'invites': invites
        })
    def post(self):
        self.auth()

        user = self.current_user()

        circle = Circle()

        circle_schema = Schema({
            Required('name'): All(unicode, Length(min=3)),
            Required('description', default=""): unicode,
            Required('privacy', default="public"): unicode,
            Required('color', default="#607d8b"): unicode,
            Required('permission'): unicode
        })

        json_str = self.request.body
        data = json.loads(json_str)

        try:
            circle_schema(data)
        except MultipleInvalid as e:
            print str(e)
            self.response.set_status(500)
            self.response.write(json.dumps({
                    'error': str(e),
                    'message': 'Data could not be validated'
                }))
            return None

        circle.name = data['name']
        circle.description = data['description']
        circle.privacy = data['privacy']
        circle.color = data['color']
        circle.permission = data['permission']
        circle.admins.append(user.key())

        circle.put()

        user.circles.append(circle.key())

        user.put()

        self.response.write(json.dumps({
            'message': 'Circle created!',
            'id': circle.key().id()
        }))

class JoinCircle(BaseHandler):
    def post(self):
        self.auth()

        user = self.current_user()

        json_str = self.request.body
        data = json.loads(json_str)

        if user:
            circle_id = int(data['circle'])
            circle_key = Circle.get_by_id(circle_id).key()
            if data['action'] == 'add':
                if circle_key not in user.circles:
                    user.circles.append(circle_key)
            elif data['action'] == 'remove':
                if circle_key in user.circles:
                    user.circles.remove(circle_key)

            user.put()
        else:
            self.response.set_status(500)

class NewCircleHandler(BaseHandler): # actual page
    def get(self):
        self.auth()

        user = self.current_user()

        doRender(self, "newCircle.html", {
            "user": user
        })

class ChangeCircle(BaseHandler):
    def get(self, circle_id):
        self.auth()

        user = self.current_user()

        if circle_id != '0':
            circle = Circle.get_by_id(int(circle_id))
        else:
            circle = None

        if not circle:
            self.session['circle'] = None
        else:
            self.session['circle'] = circle.key().id()

        self.redirect(self.request.referer)