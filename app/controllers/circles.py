from app.common.toolbox import doRender, split_address, grab_json
from google.appengine.ext import db
from app.model import *
import datetime
from datetime import date
from app.base_handler import BaseHandler
from app.common.voluptuous import *
from app.common.notification import push_noti
import json
import re
from app.common.email_sys import sender
import time
from app.common.noti import Notifications

class DeleteCircle(BaseHandler):
    def post(self, circle_id):
        self.auth()
        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if user.key() in circle.admins:
            rides = Ride.all().filter('circle', circle.key()).fetch(None)

            events = Event.all().filter('circle', circle.key()).fetch(None)

            passengers = Passenger.all().filter('ride in', rides).fetch(None)

            for p in passengers:
                p.delete()

            for p in rides:
                p.delete()

            for p in events:
                p.delete()

            users = User.all().fetch(None)

            for u in users:
                if circle.key()in u.circles:
                    u.circles.remove(circle.key())
                    u.put()

            circle.delete()

            self.json_resp(200, {
                'message': 'Success! Circle has been removed.'
            })

        else:
            self.json_resp(500, {
                'message': 'You do not have permission to do that.'
            })


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
            Required('permission'): unicode,
            'ql_add': unicode,
            'ql_lat': Coerce(float),
            'ql_lng': Coerce(float)
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
        circle.address = data['ql_add']
        circle.lat = data['ql_lat']
        circle.lng = data['ql_lng']

        circle.put()

        self.json_resp(200, {
            'message': 'Circle edited!',
            'id': circle.key().id()
        })

class GetCircleHandler(BaseHandler):
    def get(self, circle_id):
        self.auth()

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            self.session['circle'] = None
            self.redirect('/circles')
            return None

        self.session['circle'] = circle.key().id()

        user = self.current_user()

        today = date.today()

        n = Notifications()
        notifications = n.get_all(circle, user)

        requests = User.all().filter('__key__ in', circle.requests).fetch(100)

        notis = Notification.all().filter('circle = ', circle.key()).filter('type = ', 'circle_message').filter('created >', today).fetch(100)

        members = User.all().filter('circles =', circle.key()).fetch(None)
        admins = User.all().filter('__key__ in', circle.admins).fetch(None)

        for noti in notis:
            noti.date_str = noti.created.strftime('%B %dth, %Y')

        if circle.key() in user.circles:
            has_permission = True
        else:
            has_permission = False

        invite = Invite.all().filter('circle = ', circle.key()).filter('user = ', user.key()).get()

        if invite:
            has_permission = True

        if user.key() in circle.admins:
            is_admin = True
        else:
            is_admin = False

        if not has_permission and not is_admin:
            return self.redirect('/circles')

        today = date.today()

        events_all = Event.all().filter('circle =', circle).filter('date >=', today).fetch(100)

        for event in events_all:
            event.date_str = event.date.strftime('%B %dth, %Y')

        doRender(self, 'view_circle.html', {
            'circle': circle,
            'user': user,
            'invite': invite,
            'is_admin': is_admin,
            'requests': requests,
            'notis': notis,
            'events_all': events_all,
            'members': members,
            'admins': admins,
            'total_members': len(members),
            'site_notis': notifications
        })

class CircleInvited(BaseHandler):
    def get(self, circle_id):
        self.session['invited'] = str(circle_id)
        
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if user:
            previous = Invite.all().filter('circle =', circle).filter('user =', user).fetch(None)
            in_circle = True if circle.key() in user.circles else False
            if not previous and not in_circle:
                inv = Invite()
                inv.circle = circle
                inv.email = ''
                inv.user = user
                inv.put()
            time.sleep(2)
            self.redirect('/invites')
        else:
            self.redirect('/')

class GetCircleInvite(BaseHandler):
    def get(self, circle_id):
        self.auth()

        circle = Circle.get_by_id(int(circle_id))

        user = self.current_user()

        url = self.request.host_url

        doRender(self, 'view_circle_invite.html', {
            'circle': circle,
            'user': user,
            'url': url
        })

class CircleHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        circles = Circle.all().filter('privacy !=', 'invisible').fetch(100)

        for circle in circles:
            if circle.key() in user.circles:
                circle.user = True
            else:
                circle.user = False

        doRender(self, 'circles.html', {
            'circles': circles,
            'user': user
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
            Required('permission'): unicode,
            'ql_add': unicode,
            'ql_lat': Coerce(float),
            'ql_lng': Coerce(float)
        })

        json_str = self.request.body
        data = json.loads(json_str)

        try:
            circle_schema(data)
        except MultipleInvalid as e:
            return self.json_resp(500, {
                'error': str(e),
                'message': 'Data could not be validated'
            })

        circle.name = data['name']
        circle.description = data['description']
        circle.privacy = data['privacy']
        circle.color = data['color']
        circle.permission = data['permission']
        circle.admins.append(user.key())
        circle.address = data['ql_add']
        circle.lat = data['ql_lat']
        circle.lng = data['ql_lng']

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

            self.json_resp(200, {
                'message': 'Circle action completed'
            })
        else:
            self.json_resp(500, {
                'message': 'User does not exist.'
            })

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

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            self.session['circle'] = None
        else:
            self.session['circle'] = circle.key().id()

        self.redirect('/circle/' + str(circle.key().id()))

class KickMember(BaseHandler):
    def post(self, circle_id):
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            return self.json_resp(500, {
                'message': 'Circle does not exist'
            })

        json_str = self.request.body
        data = json.loads(json_str)

        user = User.get_by_id(data['user'])

        if not user:
            return self.json_resp(500, {
                'message': 'User does not exist'
            })

        if circle.key().id() in user.circles:
            user.circles.remove(circle.key().id())

        user.put()

        return self.json_resp(200, {
            'message': 'Member kicked'
        })

class PromoteMember(BaseHandler):
    def post(self, circle_id):
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            return self.json_resp(500, {
                'message': 'Circle does not exist'
            })

        json_str = self.request.body
        data = json.loads(json_str)

        user = User.get_by_id(int(data['user']))

        if not user:
            return self.json_resp(500, {
                'message': 'User does not exist'
            })

        if user.key().id() not in circle.admins:
            circle.admins.append(user.key())

        circle.put()

        return self.json_resp(200, {
            'message': 'Member promoted'
        })

class RequestJoin(BaseHandler):
    def post(self, circle_id):
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            return self.json_resp(500, {
                'message': 'Circle does not exist'
            })

        circle.requests.append(user.key())

        circle.put()

        # EMAIL NOTIFICATION
        if circle.admins:
            admins = User.all().filter('__key__ in', circle.admins).fetch(None)

            # NEW NOTIFICATION
            for admin in admins:
                n = Noti()
                n.relation = circle.key()
                n.type = 'request_circle'
                n.user = admin.key()
                n.status = 'new'
                n.put()

            d = {
                'template': 'join_requested',
                'data': {
                    'circle_name': circle.name,
                    'circle_id': circle.key().id(),
                    'requester_name': user.name_x,
                    'requester_id': user.key().id()
                },
                'subject': 'Ridecircles - ' + user.name_x + ' has requested to join your circle',
                'users': admins
            }

            sender(d)

        return self.json_resp(200, {
            'message': 'Request sent'
        })

class RequestAccept(BaseHandler):
    def post(self, circle_id):
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if user.key() not in circle.admins:
            return self.json_resp(500, {
                'message': 'You do not have permission for this.'
            })

        if not circle:
            return self.json_resp(500, {
                'message': 'Circle does not exist'
            })

        json_str = self.request.body
        data = json.loads(json_str)

        requester = User.get_by_id(int(data['user']))

        if circle.key() not in requester.circles:
            requester.circles.append(circle.key())
            requester.put()

        if requester.key() in circle.requests:
            circle.requests.remove(requester.key())
            circle.put()

        return self.json_resp(200, {
            'message': 'Request accepted'
        })

class CircleMessage(BaseHandler):
    def get(self, circle_id):
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if user.key() not in circle.admins:
            print "Unintended Access"

        if not circle:
            print "Circle DNE"

        doRender(self, 'circle_message.html', {
            'user': user,
            'circle': circle
        })

    def post(self, circle_id):
        self.auth()

        user = self.current_user()

        circle = Circle.get_by_id(int(circle_id))

        if user.key() not in circle.admins:
            return self.json_resp(500, {
                'message': 'You do not have permission for this.'
            })

        if not circle:
            return self.json_resp(500, {
                'message': 'Circle does not exist'
            })

        json_str = self.request.body
        data = json.loads(json_str)

        message = Messages()
        message.sender = user.key()
        message.circle = circle
        message.message = data['message']
        message.put()

        # EMAIL NOTIFICATION
        circle_members = User.all().filter('circles =', circle.key()).fetch(None)
        
        d = {
            'template': 'circle_message',
            'data': {
                'circle_name': circle.name,
                'circle_id': circle.key().id(),
                'circle_message': data['message']
            },
            'subject': 'Ridecircles - ' + circle.name + ' has sent you a message',
            'users': circle_members
        }

        sender(d)

        return self.json_resp(200, {
            'message': 'Message sent to all users'
        })

class CircleMembers(BaseHandler):
    def get(self, circle_id):
        self.auth()

        circle = Circle.get_by_id(int(circle_id))

        user = self.current_user()

        # Grabs members
        members = User.all().filter('circles =', circle.key()).fetch(None)
        members += User.all().filter('__key__ in', circle.admins).fetch(None)

        if circle.key() in user.circles:
            has_permission = True
        else:
            has_permission = False

        if user.key() in circle.admins:
            is_admin = True
        else:
            is_admin = False

        if not has_permission and not is_admin:
            return self.redirect('/circles')

        doRender(self, 'circle_members.html', {
            'circle': circle,
            'user': user,
            'members': members,
            'is_admin': is_admin
        })

class CircleRequests(BaseHandler):
    def get(self, circle_id):
        self.auth()

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            self.redirect('/circles')
            return None

        user = self.current_user()

        if user.key() not in circle.admins:
            self.redirect('/circles')
            return None

        requests = User.all().filter('__key__ in', circle.requests).fetch(None)

        doRender(self, 'circle_request.html', {
            'requests': requests,
            'circle': circle,
            'user': user
        })

class CircleRides(BaseHandler):
    def get(self, circle_id):
        self.auth()

        circle = Circle.get_by_id(int(circle_id))

        if not circle:
            self.redirect('/circles')
            return None

        user = self.current_user()