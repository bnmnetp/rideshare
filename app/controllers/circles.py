from app.common.toolbox import doRender
from google.appengine.ext import db
from app.model import *
import datetime
from datetime import date
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json

class GetCircleHandler(BaseHandler):
    def get(self, circle_id):
        self.auth()
        circle = Circle.get_by_id(int(circle_id))

        user = self.current_user()

        comments = Comment.all().filter('circle = ', circle.key()).order('-date').fetch(100)

        members = User.all().filter('circles = ', circle.key())

        doRender(self, 'view_circle.html', {
            'circle': circle,
            'comments': comments,
            'user': user,
            'members': members
        })


class CircleHandler(BaseHandler):
    def get(self):
        self.auth()
        community = db.Query(Community).get()
        circles = Circle.all()
        user = self.current_user()

        doRender(self, 'join_circles.html', {
            'community': community,
            'circles': circles,
            'user': user
        })
    def post(self):
        self.auth()
        
        circle = Circle()

        circle_schema = Schema({
            Required('name'): All(unicode, Length(min=3)),
            Required('description', default=""): unicode
        })

        json_str = self.request.body
        data = json.loads(json_str)

        try:
            circle_schema(data)
        except MultipleInvalid as e:
            print str(e)
            self.response.set_status(500)
            self.response.write(json.dumps({
                    'error': True,
                    'message': 'Data could not be validated'
                }))
            return

        circle.name = data['name']
        circle.description = data['description']

        circle.put()

        self.response.write(json.dumps({
            'message': 'Circle created!'
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
        aquery = db.Query(Community)
        community = aquery.get()  
        doRender(self, "newCircle.html", {"community": community})


class AddCircleHandler(BaseHandler): #add Circle Processing
    def post(self):
        aquery = db.Query(College)
        mycollege = aquery.get()
        circleName = self.request.get("name")
        circleDesc = self.request.get("description")
        newCircle = Circle()
        newCircle.name = circleName
        newCircle.description = circleDesc
        newCircle.put()
        self.redirect("/")