def get(self):
    aquery = db.Query(College)
    mycollege = aquery.get()
    user = self.current_user
    newEvent = Event()
    newEvent.name = self.request.get("name")
    newEvent.lat = float(self.request.get("lat"))
    newEvent.lng = float(self.request.get("lng"))
    newEvent.address = self.request.get("address")
    newEvent.circle = self.request.get("circle")
    newEvent.time = self.request.get("time")
    newEvent.creator = self.current_user.id
    newEvent.ToD = datetime.date(int(self.request.get("year")),int(self.request.get("month")),int(self.request.get("day")))
    newEvent.put()

    query = db.Query(Ride)
    query.filter("ToD > ", datetime.date.today())
    query.filter("circle = ",self.request.get("circle"))
    ride_list = query.fetch(limit=100)
    greeting = ''
    if user:
          greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                (user.nickname(), users.create_logout_url("/")))
    message = 'Your ride has been created!'
    path = os.path.join(os.path.dirname(__file__), 'templates/map.html')
    self.response.out.write(str(template.render(path, {
        'ride_list': ride_list, 
        'greeting': greeting,
        'message': message,
        'mapkey' : MAP_APIKEY,
        })))