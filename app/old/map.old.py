    def get(self):
        query = db.Query(Ride)
        query.filter("ToD > ", datetime.date.today())
        logging.debug(self.request.get("circle"))
        query.filter("circle = ",self.request.get("circle"))
        ride_list = query.fetch(limit=100)
        
        aquery = db.Query(College)
        mycollege= aquery.get()
        user = self.current_user
        logging.debug(users.create_logout_url("/"))
        greeting = ''
        logout = ''
        #if user:
        #    greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
        #          (user.nickname(), users.create_logout_url("/")))
        #    logout = users.create_logout_url("/")
        #    logging.debug(logout)
        #else:
        #    self.redirect('/auth/login')
        #    return
        
        logging.debug(mycollege.address)
        doRender(self, 'map.html', {
            'ride_list': ride_list, 
            'greeting' : greeting,
            'college': mycollege,
            'address': mycollege.address,
            'nick' : user.nickname(),
            'user':user.id,
            'logout':'/auth/logout',
            'mapkey':MAP_APIKEY,
            })
