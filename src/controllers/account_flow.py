class LoginPageHandler(BaseHandler):
    def get(self):
        aquery = db.Query(College)
        mycollege= aquery.get()
        user = self.current_user
        if user:
            self.redirect("/main")
        else:
            doRender(self, 'loginPage.html', {"name": mycollege.name, "college": mycollege})

class SignOutHandler(BaseHandler):
    def get(self):
      aquery = db.Query(College)
      mycollege= aquery.get()
      doRender(self, 'logout.html', { 'logout_message': "Thanks for using the "+ mycollege.name + " Rideshare Website!","college":mycollege})