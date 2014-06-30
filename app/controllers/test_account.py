from google.appengine.ext import db
from app.base_handler import BaseHandler

from app.common.email import send_email

class email_test(BaseHandler):
    def get(self):
        user = self.current_user()
        message = 'Test Message'
        user.email = 'bananagus@gmail.com'
        send_email(user, 'Subject', 'emails/notification.html', {
            'message': message,
            'name': user.name,
            'community': {}
        })
        self.response.write('Sent')