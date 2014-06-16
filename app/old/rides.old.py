def get(self):
        """
        Called when a new ride needs to be added to the database.
        Probably with all of this data it should be done as a form post.
        
        Arguments:
        - `self`:
        Web Arguments:
        - max_passengers
        - num_passengers
        - driver
        - start_point_title
        - start_point_lat
        - start_point_long
        - destination_title
        - destination_lat
        - destination_long
        - part_of_day
        - ToD
        - contact
        - ridecomments
        - driver
        """
        user = self.current_user
        newRide = Ride()
        maxp = self.request.get("maxp")
        inumber = self.request.get("contact")
        if not "-" in inumber:
            number = inumber[0:3]+'-'+inumber[3:6]+'-'+inumber[6:]
        else:
            number = inumber
        newRide.contact = number

        isDriver = self.request.get("isDriver")
        if isDriver.lower() == "false":
            isDriver = False
        else:
            isDriver = True
        
        aquery = db.Query(College)
        mycollege= aquery.get()
        """ # For testing
        latlng = ['41.517658', '-95.452065']
        lat = float(latlng[0])
        lng = float(latlng[1])
        """
        lat = float(self.request.get("lat")) * (random.random() * (1.000001-.999999) + 1.000001)
        lng = float(self.request.get("lng")) * (random.random() * (1.000001-.999999) + 1.000001)
        checked = self.request.get("toLuther")
        if checked == 'true':
          newRide.start_point_title = self.request.get("from")
          newRide.start_point_lat = lat
          newRide.start_point_long = lng
          newRide.destination_title = mycollege.name
          newRide.destination_lat = mycollege.lat
          newRide.destination_long = mycollege.lng
        elif checked == 'false':
          newRide.start_point_title = mycollege.name
          newRide.start_point_lat = mycollege.lat
          newRide.start_point_long = mycollege.lng
          newRide.destination_title = self.request.get("to")
          newRide.destination_lat = lat
          newRide.destination_long = lng             
        y = int(self.request.get("year"))
        m = int(self.request.get("month")) + 1
        d = int(self.request.get("day"))
        early_late_value = int(self.request.get("earlylate"))
        part_of_day_value = int(self.request.get("partofday"))
        # TODO:  replace this logic with the global dictionaries.
        part_of_day = ''
        if early_late_value == 0:
          part_of_day += 'Early '
        else:
          part_of_day += 'Late '
        if part_of_day_value == 0:
          part_of_day += 'Morning'
        elif part_of_day_value == 1:
          part_of_day += 'Afternoon'
        else:
          part_of_day += 'Evening'
        newRide.part_of_day = part_of_day
        newRide.ToD = datetime.date(int(y),int(m),int(d))

        newRide.max_passengers = int(maxp)
        newRide.num_passengers = 0
        newRide.passengers = []


        if isDriver:
            newRide.driver = user.id
            newRide.drivername = FBUser.get_by_key_name(user.id).nickname()
        else:
            user_name = user.id
            passenger = Passenger()
            passenger.name = user_name
            passenger.fullname = FBUser.get_by_key_name(user.id).nickname()
            logging.debug(FBUser.get_by_key_name(user.id).nickname())
            passenger.contact = number
            passenger.location = newRide.destination_title
            passenger.lat = lat
            passenger.lng = lng
            pass_key = passenger.put()
            newRide.passengers.append(pass_key)
            newRide.num_passengers = 1

        newRide.comment = self.request.get("comment")
        newRide.circle = self.request.get("circleType")
        ride_key = newRide.put()
        if not isDriver:
            passenger.ride = ride_key
            passenger.put()

        query = db.Query(Ride)
        query.filter("ToD > ", datetime.date.today())
        query.filter("circle = ",self.request.get("circle"))
        ride_list = query.fetch(limit=100)
        self.sendRideEmail(newRide)
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = 'Your ride has been created!'
        #doRender(self, 'map.html',{
        #    'ride_list': ride_list, 
        #    'greeting': greeting,
        #    'message': message,
        #    'mapkey' : MAP_APIKEY,
        #   })
        self.redirect("/map?circle="+str(self.request.get("circleType")))

class AddPassengerHandler(BaseHandler): 
    """
    Handles addition of passengers
    """
    def get(self):
      """
      Called when adding a passenger to a ride
      
      Arguments:
      - 'self'
      
      Web Arguments:
      - user_name
      - ride_key
      """
      # The current user can add himself to the ride.  No need for this in the form.
      aquery = db.Query(College)
      mycollege= aquery.get()
      user_name = self.current_user.id
      
      ride_key = self.request.get('ride_key')
      contact = self.request.get('contact')
      address = self.request.get('address')
      lat = float(self.request.get('lat'))
      lng = float(self.request.get('lng'))
      ride = db.get(db.Key(ride_key))
      if ride == None: # Check if the ride was found
        temp = os.path.join(os.path.dirname(__file__), 'templates/error.html')
        outstr = template.render(temp, {'error_message': 'Error in ride matching'})
        self.response.out.write(outstr)
      # Check if the current user is the driver
      elif ride.max_passengers == ride.num_passengers:
        doRender(self, 'error.html', {'error_message': 'This ride is full'})
      # Check if the current user is already on the ride
      already = False
      for p in ride.passengers:
        if db.get(p).name== user_name:
          already = True
      if already:
        temp = os.path.join(os.path.dirname(__file__), 'templates/error.html')
        outstr = template.render(temp, {'error_message': 'You are already registered for this ride!'})
        self.response.out.write(outstr)
      # Check if the current user is already the driver for the ride
      elif user_name == ride.driver:
        doRender(self, 'error.html', {'error_message': 'You can\'t be a passenger for a ride which you a driving.'})
      else:
        passenger = Passenger()
        passenger.name = user_name
        passenger.fullname = FBUser.get_by_key_name(user_name).nickname()
        passenger.contact = contact
        passenger.location = address
        passenger.lat = lat
        passenger.lng = lng
        passenger.ride = db.Key(ride_key)
        pass_key = passenger.put()
        ride.num_passengers = ride.num_passengers + 1
        ride.passengers.append(pass_key)
        ride.put()

        if ride.num_passengers == ride.max_passengers:
          capacity_message = 'is now full.'
        else:
          num_left = ride.max_passengers - ride.num_passengers
          capacity_message = 'can hold ' + str(num_left) + ' more passengers.'
        query = db.Query(Ride)
        query.filter("ToD > ", datetime.date.today())
        ride_list = query.fetch(limit=100)
        user = self.current_user
        greeting = ''
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>) Go to your <a href='/home'>Home Page</a>" %
                  (user.nickname(), users.create_logout_url("/")))
        message = 'You have been added to %s ride.' % (ride.driver)
        self.sendDriverEmail(ride)
        path = os.path.join(os.path.dirname(__file__), 'templates/map.html')
        self.response.out.write(template.render(path, {
            'ride_list': ride_list, 
            'greeting': greeting,
            'message': message,
            'mapkey':MAP_APIKEY, 
            'college':mycollege           
            }))

    def sendDriverEmail(self,ride):
        logging.debug(ride.driver)
        driver = FBUser.get_by_key_name(ride.driver)
        logging.debug(driver)
        if not ride.driver:
            return
        if driver.loginType == "google":
           to = driver
        else:
           logging.debug(ride.driver)
           to = FBUser.get_by_key_name(ride.driver)
           logging.debug(to)
        sender = FROM_EMAIL_ADDR
        subject = "New Passenger for your ride"
        p = db.get(ride.passengers[-1])
        user = FBUser.get_by_key_name(p.name)
        body = """
Dear %s,
We wanted to let you know that %s has been added to your ride
from %s to %s on %s.  If you need to contact %s you can do so at %s.

Thanks for being a driver!

Sincerely,

The Rideshare Team
""" % (to.nickname(), user.nickname(), ride.start_point_title, ride.destination_title,
       ride.ToD, user.nickname(), p.contact)

        if driver.loginType == "google":
          logging.debug(body)
          mail.send_mail(sender,to.email,subject,body)
        else:
          graph = facebook.GraphAPI(to.access_token)
          logging.debug(graph)
          graph.put_object("me", "feed", message=body)