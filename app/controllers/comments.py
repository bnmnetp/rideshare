import json
from google.appengine.ext import db
from app.model import *
import datetime
from app.base_handler import BaseHandler
from app.common.voluptuous import *
from app.common.toolbox import doRender

def get_key(id, type):
    key = ''
    if type == 'ride':
        ride = Ride.get_by_id(id)
        key = ride.key()
    elif type == 'event':
        event = Event.get_by_id(id)
        key = event.key()
    elif type == 'circle':
        circle = Circle.get_by_id(id)
        key = circle.key()
    elif type == 'profile':
        user = User.get_by_id(id)
        key = user.key()
    return key

def comment_type():
    def f(v):
        type = v
        if type in ['ride', 'event', 'circle', 'profile']:
            return type
        else:
            raise Invalid('Not a valid type')
    return f

class CommentHandler(BaseHandler):
    def get(self):
        return self.redirect('/home')
    def post(self):
        self.auth()

        user = self.current_user()

        json_str = self.request.body
        data = json.loads(json_str)

        comment_validator = Schema({
            'comment': unicode,
            'type': unicode,
            'id': Coerce(int),
            'is_owner': bool
        })

        try:
            data = comment_validator(data)
        except MultipleInvalid as e:
            print str(e)
            return self.json_resp(500, {
                'error': True,
                'message': str(e)
            })

        d = datetime.date.today()

        comment = Comment()
        comment.user = user.key()
        comment.date = d
        comment.text = data['comment']
        if data['type'] == 'ride':
            ride = Ride.get_by_id(data['id'])
            comment.ride = ride.key()
        elif data['type'] == 'event':
            event = Event.get_by_id(data['id'])
            comment.event = event.key()
        elif data['type'] == 'circle':
            circle = Circle.get_by_id(data['id'])
            comment.circle = circle.key()
        elif data['type'] == 'profile':
            user = User.get_by_id(data['id'])
            comment.profile = user.key()
        comment.put()

        self.response.write(json.dumps({
            'user': {
                'name': user.name,
                'id': user.key().id()
            },
            'message': 'Success',
            'name': user.name,
            'date': str(d),
            'text': comment.text,
            'id': comment.key().id()
        }))

class FetchComments(BaseHandler):
    def get(self):
        return self.redirect('/home')
    def post(self):
        self.auth()

        user = self.current_user()

        json_str = self.request.body
        data = json.loads(json_str)

        key = get_key(data['id'], data['type'])

        comments = Comment.all().filter(data['type'] + " = ", key).order('-date').fetch(25)

        resp = [c.to_dict() for c in comments]

        for res in resp:
            if res['user']['id'] == user.key().id():
                res['is_owner'] = True
            else:
                res['is_owner'] = False

        self.response.write(json.dumps(resp))

class GetComment(BaseHandler):
    def get(self, comment_id):
        self.auth()

        user = self.current_user()

        comment = Comment.get_by_id(int(comment_id))

        doRender(self, 'edit_comment.html', {
            'comment': comment,
            'user': user
        })

    def post(self, comment_id):
        self.auth()

        user = self.current_user()

        json_str = self.request.body
        data = json.loads(json_str)

        comment = Comment.get_by_id(int(comment_id))

        comment.text = data['text']

        comment.put()

        resp = {
            'message': 'Success'
        }

        self.response.write(json.dumps(resp))

    def delete(self, comment_id):
        self.auth()

        user = self.current_user()

        comment = Comment.get_by_id(int(comment_id))

        if comment.user.key() == user.key():
            comment.delete()

            resp = {
                'message': 'Deleted'
            }

            self.response.write(json.dumps(resp))

        else:
            resp = {
                'message': 'Not deleted'
            }

            self.response.write(json.dumps(resp))


