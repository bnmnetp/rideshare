import emails
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

	message = emails.html(
		subject=subject,
		html=html,
		mail_from=('Rideshare', 'team@rideshare.com')
	)

	message.send(to=(user.name, user.email))