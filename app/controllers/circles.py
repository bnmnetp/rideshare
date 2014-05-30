from app.common.toolbox import doRender
from google.appengine.ext import db
from app.model import *
import datetime
from datetime import date
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json

class CircleHandler(BaseHandler):
    def get(self):
        community = db.Query(Community).get()
        circles = Circle.all()
        user = self.current_user

        # Marks the circle.user property true if the user is in that circle
        for circle in circles:
            circle_id = circle.key().id()
            if circle_id in user.circles:
                circle.user = True
            else:
                circle.user = False

        doRender(self, 'join_circles.html', {
            'community': community,
            'circles': circles,
            'user': user
        })
    def post(self):
        circle = Circle()

        circle_schema = Schema({
            Required('name'): All(unicode, Length(min=3)),
            Required('description', default=""): unicode
        })

        json_str = self.request.body
        data = json.loads(json_str)
        print type(data['description'])
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
        json_str = self.request.body
        data = json.loads(json_str)

        user = User.get_by_id(data['user'])

        if user:
            if data['action'] == 'add':
                circle_id = int(data['circle'])
                if circle_id not in user.circles:
                    user.circles.append(circle_id)
            elif data['action'] == 'remove':
                if circle_id in user.circles:
                    user.circles.remove(circle_id)

            user.put()
        else:
            self.response.set_status(500)

class ChangeCirclesHandler(BaseHandler): #actual page for changing circles
    def get(self):
        aquery = db.Query(College)
        mycollege = aquery.get()
        allCircles = Circle.all()
        user = FBUser.get_by_key_name(self.current_user.id)
        doRender(self, "changecircles.html", {"circles": allCircles, "userCircles": user.circles, "college": mycollege})

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

class UpdateCirclesHandler(BaseHandler):  #handles processing
    def post(self):
        user = FBUser.get_by_key_name(self.current_user.id)
        user.circles = self.request.str_params.getall("circle")
        user.put()
        self.redirect("/main")