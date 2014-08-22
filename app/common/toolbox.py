import os.path
import jinja2
from app.model import *
from app.base_handler import BaseHandler
from datetime import datetime

env = jinja2.Environment(
    loader=jinja2.PackageLoader('app', 'templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

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

		value['active_circle'] = b.circle()

	value['current_page'] = handler.request.path
	template = env.get_template(name)
	handler.response.write(template.render(value))

def split_address(add):
	temp = add.split(',')
	return temp[1][1:] + ', ' + temp[2][1:3]

def grab_json(obj, prop):
	resp = {}
	for p in prop:
		if p in obj._properties:
			resp[p] = str(getattr(obj, p))
	return resp

# returns date obj from format
def create_date(fmt='%m/%d/%Y'):
	return lambda v: datetime.strptime(v, fmt).date()