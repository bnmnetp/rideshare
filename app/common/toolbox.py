import os.path
import jinja2
from app.model import *
from app.base_handler import BaseHandler
from datetime import datetime
import json

# from google.appengine.tools.devappserver2.python import sandbox
# sandbox._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']


env = jinja2.Environment(
    loader=jinja2.PackageLoader('app', 'templates'),
    trim_blocks=True
)

env.filters['js'] = json.dumps

def doRender(handler, name = 'home.html', value = {}):
	b = BaseHandler()
	if b != None:
		user = b.current_user()

	value['active_circle'] = None

	if user:
		value['invite_badge'] = Invite.all().filter('user = ', user.key()).count()
		value['alert_badge'] = Notification.all().filter('user = ', user.key()).count()
		circle_keys = user.circles
		value['circle_list'] = Circle.all().filter('__key__ in', circle_keys).fetch(20)
		value['active_circle'] = handler.circle()
		if value['active_circle']:
			if user.key() in value['active_circle'].admins:
				value['is_admin'] = True

	value['current_page'] = handler.request.path
	template = env.get_template(name)
	handler.response.write(template.render(value))

def render(handler, name = 'home.html', value = {}):
	b = BaseHandler()
	if b != None:
		user = b.current_user()

	value['active_circle'] = None

	if user:
		value['invite_badge'] = Invite.all().filter('user = ', user.key()).count()
		value['alert_badge'] = Notification.all().filter('user = ', user.key()).count()
		circle_keys = user.circles
		value['circle_list'] = Circle.all().filter('__key__ in', circle_keys).fetch(20)
		value['active_circle'] = handler.circle()
		if value['active_circle']:
			if user.key() in value['active_circle'].admins:
				value['is_admin'] = True

	value['current_page'] = handler.request.path
	template = env.get_template(name)
	handler.response.write(template.render(value))

def split_address(address):
	parts = address.split(',')
	print parts
	if len(parts) == 3:
		state = parts[1].split(' ')
		return parts[0] + ', ' + state[1]
	elif len(parts) == 4:
		state = parts[2].split(' ')
		return parts[1] + ', ' + state[1]
	else:
		return address

def city_state(address):
	parts = address.split(',')
	for p in parts:
		if p == ' ':
			p = p[1:]
	if len(parts) == 4:
		state = parts[1].split(' ')
		return parts[0] + ', ' + state[0]
	elif len(parts) == 5:
		state = parts[2].split(' ')
		return parts[1] + ', ' + state[0]
	else:
		return address

def format_address(address):
	return split_address(address)

def grab_json(obj, prop):
	resp = {}
	for p in prop:
		if p in obj._properties:
			resp[p] = str(getattr(obj, p))
	return resp

# returns date obj from format
def create_date(fmt='%m/%d/%Y'):
	return lambda v: datetime.strptime(v, fmt).date()

def set_properties(db_obj, arr, data):
	for a in arr:
		setattr(db_obj, a, data[a])

def date_display(date):
	return date.strftime('%B %dth, %Y')
	
def date_picker(date):
	return date.strftime("%m/%d/%Y")
	