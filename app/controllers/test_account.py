from google.appengine.ext import db

class FBUser(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    email = db.EmailProperty()
    drivercomments = db.StringListProperty()
    public_link = db.StringProperty()
    rating = db.FloatProperty()
    numrates= db.IntegerProperty(default=0)
    loginType= db.StringProperty()
    circles = db.ListProperty(str)
    

    def nickname(self):
       return self.name

def create_user(BaseHandler):
    user = FBUser(
        key_name=str(123),
        id="123",
        name="Gus",
        access_token=" ",
        profile_url="123",
        email="bananagus@gmail.com",
        public_link="123",
        loginType="google"
    )
    user.put()