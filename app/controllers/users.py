from app.common.toolbox import doRender, grab_json
from google.appengine.ext import db
from google.appengine.api import files, images
from google.appengine.ext.webapp import blobstore_handlers
from app.model import *
import datetime
from datetime import date
from app.base_handler import BaseHandler
from app.common.voluptuous import *
import json

import base64
import re

import csv

class GetUserHandler(BaseHandler):
    def get(self, user_id):
        current_user = self.current_user()

        self.auth()
        user = User.get_by_id(int(user_id))

        user.created_str = user.created.strftime('%B %dth, %Y')

        if user_id == current_user.key().id():
            is_user = True
        else:
            is_user = False

        doRender(self, 'view_user.html', {
            'user': user,
            'is_user': is_user
        })

class GetImage(BaseHandler):
    def get(self, user_id):
        user = User.get_by_id(int(user_id))
        if user.photo:
            self.redirect(images.get_serving_url(user.photo))
        else:
            self.redirect('/static/img/default_user.png')
        # blobstore_handlers.BlobstoreDownloadHandler.send_blob(user.photo)

class NotificationUserHandler(BaseHandler):
    def get(self, user_id):
        self.auth()
        user = self.current_user()

        doRender(self, 'notification_user.html', {
            'user': user
        })

    def post(self, user_id):
        self.auth()

        json_str = self.request.body
        data = json.loads(json_str)

        user = self.current_user()

        if not user.key().id() == int(user_id):
            self.redirect('/user/' + user_id)
            return None
        else:
            user.noti_type = data['type']
            user.noti_time = int(data['time'])
            user.put()

            resp = {
                'message': 'Updated!'
            }

            self.response.write(json.dumps(resp))

class DeleteUser(BaseHandler):
    def post(self, user_id):
        self.auth()

        user = self.current_user()

        requested_user = User.get_by_id(int(user_id))

        if user.key() == requested_user.key():

            all_circles = Circle.all().fetch(None)
            for circle in all_circles:
                if user.key() in circle.admins:
                    circle.admins.remove(user.key())
                    circle.put()

            rides = Ride.all().filter('driver =', user.key()).fetch(None)
            for ride in rides:
                ride.driver = None
                ride.put()

            passengers = Passenger.all().filter('user =', user.key()).fetch(None)

            for passenger in passengers:
                passenger.delete()

            user.delete()

            return self.json_resp(200, {
                'message': 'User removed.'
            })

        else:
            return self.json_resp(500, {
                'message': 'You do not have permission to delete this user.'
            })

class EditPrefHandler(BaseHandler):
    def get(self, user_id):
        self.auth()
        user = self.current_user()
        if not user.key().id() == int(user_id):
            self.redirect('/user/' + user_id)
            return None

        preferences = {
            'join_requested': True,
            'event_created': True,
            'ride_edited': True,
            'passenger_joined': True,
            'new_ride': True,
            'circle_message': True
        }

        for p in preferences:
            if p in user.email_pref:
                preferences[p] = False

        doRender(self, 'user_email_pref.html', {
            'user': user,
            'preferences': json.dumps(preferences)
        })

    def post(self, user_id):
        self.auth()
        user = self.current_user()
        if not user.key().id() == int(user_id):
            return self.json_resp(500, {
                'message': 'You do not have permission'
            })

        json_str = self.request.body
        data = json.loads(json_str)

        preferences = []
        for d in data:
            if data[d] == False:
                preferences.append(d)

        user.email_pref = preferences
        user.put()

        return self.json_resp(200, {
            'message': 'Preferences updated!'
        })

class EditUserHandler(BaseHandler):
    def get(self, user_id):
        self.auth()

        user = self.current_user()

        properties = ['name', 'email', 'phone', 'zip', 'address', 'lat', 'lng']

        user_json = grab_json(user, properties)

        if not user.key().id() == int(user_id):
            self.redirect('/user/' + user_id)
            return None
        else:
            doRender(self, 'edit_user.html', {
                'user': user,
                'user_json': user_json
            })

    def post(self, user_id):
        data_pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')

        json_str = self.request.body
        data = json.loads(json_str)

        print data

        user_validator = Schema({
            Required('zip'): Coerce(int),
            Required('email'): unicode,
            Required('phone'): unicode,
            Required('name'): unicode,
            'photo': unicode,
            'ql_add': unicode,
            'ql_lat': Coerce(float),
            'ql_lng': Coerce(float),
            'lat': unicode,
            'lng': unicode,
            'address': unicode
        })

        try:
            data = user_validator(data)
        except MultipleInvalid as e:
            return self.json_resp(500, {
                'error': str(e),
                'message': 'Data could not be validated!'
            })

        self.auth()

        user = self.current_user()
        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.zip = data['zip']
        user.address = data['ql_add']
        user.lat = data['ql_lat']
        user.lng = data['ql_lng']

        if not user.key().id() == int(user_id):
            self.redirect('/user/' + user_id)
            return None
        else:
            if 'photo' in data and len(data['photo']) > 0:
                d64 = re.search(r'base64,(.*)', data['photo']).group(1)
                decoded = d64.decode('base64')

                # decoded = data['photo'].decode('base64')

                file_name = files.blobstore.create(mime_type='image/png')

                with files.open(file_name, 'a') as f:
                    f.write(decoded)

                files.finalize(file_name)

                key = files.blobstore.get_blob_key(file_name)
                user.photo = str(key)
                print key

        user.put()

        self.json_resp(200, {
            'message': 'Edited!'
        })

class UserHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        user.created_str = user.created.strftime('%B %dth, %Y')

        doRender(self, 'view_user.html', {
            'user': user,
            'is_user': True
        })

class DetailHandler(BaseHandler):
    def get(self):
        self.auth()
        user = self.current_user()

        properties = ['name', 'email', 'phone', 'zip']

        user_json = grab_json(user, properties)

        doRender(self, 'details.html', {
            'user': user,
            'user_json': user_json
        })
    def post(self):
        json_str = self.request.body
        data = json.loads(json_str)

        self.auth()
        user = self.current_user()

        detail_validator = Schema({
            Required('zip'): Coerce(int),
            Required('email'): unicode,
            Required('phone'): unicode,
            Required('name'): unicode,
            'address': unicode,
            'lat': float,
            'lng': float
        })

        try:
            data = detail_validator(data)
        except MultipleInvalid as e:
            return self.json_resp(500, {
                'error': str(e),
                'message': 'Data could not be validated'
            })

        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.zip = data['zip']
        user.add = data['address']
        user.lat = data['lat']
        user.lng = data['lng']

        circle_match = Circle.all().filter('zip =', data['zip']).get()

        if circle_match != None and circle_match.key() not in user.circles:
            user.circles.append(circle_match.key())
        else:
            zip_row = None
            with open('./app/common/zip_db.csv') as zip_db:
                zip_data = csv.reader(zip_db, delimiter=',')
                for row in zip_data:
                    # Must use string to search
                    if str(data['zip']) in row:
                        zip_row = row
                        break
            if zip_row:
                city = zip_row[2]
                circle = Circle()
                circle.name = 'Open ' + city + ' Circle'
                circle.description = 'An open circle for residents of ' + city + '.'
                circle.permission = 'public'
                circle.zip = data['zip']
                circle.color = '#607d8b'
                circle.privacy = 'public'
                circle.put()
                user.circles.append(circle.key())

        user.put()

        return self.json_resp(200, {
            'message': 'Information updated'
        })