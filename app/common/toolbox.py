import os.path
from google.appengine.ext.webapp import template

def doRender(handler, name='map.html', value={}):
    temp = os.path.join(os.path.dirname(__file__), '../templates/' + name)
    outstr = template.render(temp, value)
    handler.response.out.write(str(outstr))