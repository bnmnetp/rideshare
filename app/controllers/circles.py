from app.common.toolbox import doRender
from app.nateusers import BaseHandler, FBUser
from google.appengine.ext import db
from app.model import *
import datetime
from datetime import date

class ChangeCirclesHandler(BaseHandler): #actual page for changing circles
    def get(self):
        aquery = db.Query(College)
        mycollege = aquery.get()
        allCircles = Circle.all()
        user = FBUser.get_by_key_name(self.current_user.id)
        doRender(self, "changecircles.html", {"circles": allCircles, "userCircles": user.circles, "college": mycollege})

class NewCircleHandler(BaseHandler): # actual page
    def get(self):
        aquery = db.Query(College)
        mycollege = aquery.get()  
        doRender(self, "newCircle.html", {"college": mycollege})


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