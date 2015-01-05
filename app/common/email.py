from google.appengine.api import mail
import jinja2

env = jinja2.Environment(
    loader=jinja2.PackageLoader('app', 'templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

# user obj, subject, file for template, data for template
def send_email(user, subject, template_file, ctx):

	template = env.get_template(template_file)
	html = template.render(ctx)

	message = mail.EmailMessage(
		sender='Ridecircle Team <hello@decorahrideshare-live.appspotmail.com>',
		subject=subject
	)

	message.to = user.name + ' <' + user.email + '>'

	message.html = html

	message.send()

def send_invite(email, ctx):

	template = env.get_template('emails/invite.html')
	html = template.render(ctx)

	message = mail.EmailMessage(
		sender='Ridecircle Team <hello@decorahrideshare-live.appspotmail.com>',
		subject='You are invited to join Ridecircles'
	)

	message.to = ' <' + email + '>'

	message.html = html

	message.send()