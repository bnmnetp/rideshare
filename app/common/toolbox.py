import os.path
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.PackageLoader('app', 'templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

def doRender(handler, name = 'map.html', value = {}):
	template = JINJA_ENVIRONMENT.get_template(name)
	handler.response.write(template.render(value))