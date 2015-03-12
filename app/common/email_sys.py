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
	template = env.get_template('emails/' + d['template'] + '.html')
	

	message = mail.EmailMessage(
		sender='Ridecircle Team <hello@decorahrideshare-live.appspotmail.com>',
		subject=d['subject']
	)

	for u in d['users']:
		if u.email and d['template'] not in u.email_pref:
			d['data']['user_name'] = u.name_x
			d['data']['user_id'] = u.key().id()
			html = template.render(d['data'])
			message.html = html
			message.to = u.name + '<' + u.email + '>'
			message.send()