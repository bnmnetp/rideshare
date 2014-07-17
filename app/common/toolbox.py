import os.path
import jinja2
from app.model import *
from app.base_handler import BaseHandler

env = jinja2.Environment(
    loader=jinja2.PackageLoader('app', 'templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

def doRender(handler, name = 'map.html', value = {}):
	value['community'] = db.Query(Community).get()

	b = BaseHandler()
	user = b.current_user()

	if user:
		value['invite_badge'] = Invite.all().filter('user = ', user.key()).count()
		value['alert_badge'] = Notification.all().filter('user = ', user.key()).count()

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