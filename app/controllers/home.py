from app.common.toolbox import doRender, grab_json, split_address, date_display
from google.appengine.ext import db
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json
from app.model import *
import datetime
from datetime import date
from app.common.email_sys import sender
from app.common.noti import Notifications

class Home(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        circles = Circle().all().fetch(None)

        n = Notifications()

        notifications = n.get_all(None, user)

        for circle in circles:
            if circle.key() in user.circles:
                circle.user = True
            else:
                circle.user = False

        doRender(self, 'home.html', { 
            'site_notis': notifications,
            'user': user,
            'circles': circles
        })