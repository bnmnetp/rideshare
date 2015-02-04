from google.appengine.api import mail
import jinja2

env = jinja2.Environment(
    loader=jinja2.PackageLoader('app', 'templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

def sender(d):
	'''
	d {
		template,
		data,
		subject,
		users
	}
	'''
	template = env.get_template(d['template'])
	html = template.render(d['data'])

	message = mail.EmailMessage(
		sender='Ridecircle Team <hello@decorahrideshare-live.appspotmail.com>',
		subject=d['subject']
	)

	message.html = html

	for u in users:
		if u.email:
			message.to = u.name + '<' + u.email + '>'
			message.send()


