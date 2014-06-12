import os.path
import jinja2
from app.model import *

env = jinja2.Environment(
    loader=jinja2.PackageLoader('app', 'templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

env.globals['community'] = db.Query(Community).get()

def doRender(handler, name = 'map.html', value = {}):
	template = env.get_template(name)
	handler.response.write(template.render(value))

def split_address(add):
	temp = add.split(',')
	return temp[1][1:] + ', ' + temp[2][1:3]