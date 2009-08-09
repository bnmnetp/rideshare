    function initialize() 
    {
      if (GBrowserIsCompatible()) 
      {
        map = new GMap2(document.getElementById("map_canvas"), {draggableCursor: 'crosshair'});
        map.setCenter(new GLatLng(43.313059,-91.799501), 6);
        map.addControl(new GLargeMapControl());
        //map.setUIToDefault();
        geocoder = new GClientGeocoder();
        GEvent.addListener(marker, "click", function()
          { marker.openInfoWindowHtml("Luther College<br />Decorah, Iowa"); });
        map.addOverlay(marker);

        var r;
        for(r in rides)
        {
          addRideToMap(rides[r], r);
        }
        GEvent.addListener(map, "click", getAddress);
      }
/*
      GEvent.addListener(map, "click", function(overlay, point)
        {
          var fpoint = point;
          var newRide = new GMarker(point, gmarkerOptions);
          var html = ("<b>Create a new Ride</b>" + getNewRidePopupHTML(fpoint));
          map.openInfoWindowHtml(point, html);
        });
*/

    }

    function getAddress(overlay, latlng)
    {
      if (latlng != null) 
      {
        address2 = latlng;
        geocoder.getLocations(latlng, showAddressClick);
      }
    }


    function showAddressClick(response) 
    {
      if (!response || response.Status.code != 200) 
      {
        alert("Status Code:" + response.Status.code);
      } 
      else 
      {
        place = response.Placemark[0];
        point = new GLatLng(place.Point.coordinates[1],
                            place.Point.coordinates[0]);
        //marker = new GMarker(point);
        //map.addOverlay(marker);
        map.openInfoWindowHtml(point, 
        // '<b>latlng: </b>' + place.Point.coordinates[1] + "," + place.Point.coordinates[0] + '<br>' +
        getNewRidePopupHTML(place.Point.coordinates[1], place.Point.coordinates[0], place.address));
      }
    }

// Returns the form used in the HTML popup to build a new ride
    function getNewRidePopupHTML(lat, lng, address3)
    {
			var line0="<b>Create a New Ride</b>";

			var line1="<form><p style=\"text-align: center;\">";
			var line2="<br />"+address3+"<br />";
			var line3="<input onclick=\"newRidePopupHTMLPart2("+lat+", "+lng+", '"+address3+"', true);\" type=\"radio\" name=\"rideType\" value=\"0\" id=\"rideType\""+"/>To or";
			var line4="<input onclick=\"newRidePopupHTMLPart2("+lat+", "+lng+", '"+address3+"', false);\" type=\"radio\" name=\"rideType\" value=\"1\" id=\"rideType\"/>From<br />Luther Campus?</p></form>";

			var full = line0 + line1 + line2 + line3 + line4;
			return full;
		}

		function newRidePopupHTMLPart2(lat, lng, address4, to)
		{
			map.closeInfoWindow();
			var htmlText = getNewRidePopupHTML2(lat, lng, address4, to);
			map.openInfoWindowHtml(new GLatLng(lat, lng), htmlText);
		}

		function getNewRidePopupHTML2(lat, lng, address5, to)
		{
			var line5="<b>Create a new Ride</b> <form onsubmit=\"verifyNewRidePopup("+lat+", "+lng+", '"+address5+"'); return false;\" id=\"newride\"><div id=\"textToAll\">Please ensure that your address is as specific as possible<br />(<i>37</i> Main Street, not <i>30-50</i> Main Street)<br />From <input type=\"text\" id=\"textFrom\" name='textFrom' size=\"50\"";
			if (to == true)
			{
				line5 = line5 + "value='"+address5+"'";
			}
			else
			{
				line5 = line5 + "value='Luther College, Decorah, Iowa' readonly='readonly'";
			}
			line5 = line5 + "></div>";
			var line6="<div id=\"textFromAll\">To <input type=\"text\" id=\"textTo\" name='textTo' size=\"50\"";
			if (to == false)
			{
				line6 = line6 + "value='"+address5+"'";
			}
			else
			{
				line6 = line6 + "value='Luther College, Decorah, Iowa' readonly='readonly'";
			}
			line6 = line6 + "><br /></div><br />";
			var line7="<div id=\"maxpdiv\">";
			var line8="Maximum number of passengers: <input type=\"text\" name=\"maxp\" id=\"maxp\" maxLength=\"3\" size=\"3\" value=\"2\"><br />";
			var line9="How can you be contacted by phone? <input type=\"text\" name=\"number\" id=\"number\" maxlength=\"12\" size=\"10\" value=\"563-555-1212\" onclick=\"this.value=''\"></div>";
			var line10="<div id=\"toddiv\">";
			var line11="Time of Departure: <select name=\"earlylate\" id=\"earlylate\"><option value=\"0\" selected=\"selected\">Early</option><option value=\"1\">Late</option></select>";
			var line12="<select name=\"partofday\" id=\"partofday\"><option value=\"0\" selected=\"selected\">Morning</option><option value=\"1\">Afternoon</option><option value=\"2\">Evening</option></select>";
			var line13="<select name=\"month\" id='month' onChange=\"changeDays(document.getElementById('day'), this); return false;\"><option value=\"0\" selected=\"selected\">January</option><option value=\"1\">February</option><option value=\"2\">March</option><option value=\"3\">April</option><option value=\"4\">May</option><option value=\"5\">June</option><option value=\"6\">July</option><option value=\"7\">August</option><option value=\"8\">September</option><option value=\"9\">October</ption><option value=\"10\">November</option><option value=\"11\">December</option></select>";
			var line14="<select name=\"day\" id=\"day\">";
			for (var i = 1; i < 32; i++)
			{
        if (i == 1)
        {
          line14 += "<option value=\""+i+"\" selected=\"selected\">"+i+"</option>";
        }
        else
        {
				  line14 = line14 + "<option value=\""+i+"\">"+i+"</option>";
        }
			}
			line14 = line14 + "</select>";
			var line15="<select name=\"year\" id='year'>";
      var yr = (new Date()).getFullYear();
      var line16 = "";
      for (var i = yr-1; i < yr+4; i++)
      {
        line16 +="<option value=\""+i+"\"";
        if (i == yr)
        {
          line16 += "selected=\"selected\"";
        }
        line16 += ">"+i+"</option>";
      }
			line16 = line16 + "</select></div>";
			var line17="<div id=\"buttons\"><input type=\"submit\" id=\"submit\" name=\"submit\" value=\"Okay\"><input type=\"button\" id=\"cancel\" name='cancel' value='Cancel' onclick='map.closeInfoWindow();'></div></form>";
			var full = line5+line6+line7+line8+line9+line10+line11+line12+line13+line14+line15+line16+line17;
      return full;
    }

    function verifyNewRidePopup(lat, lng, address6)
    {
      var from = document.getElementById("textFrom").value;
      var to = document.getElementById("textTo").value;
      var earlylate = document.getElementById("earlylate").value;
      var partofday = document.getElementById("partofday").value;
      var month = document.getElementById("month").value;
      var day = document.getElementById("day").value;
      var year = document.getElementById("year").value;

      // Check for valid number
      var number = document.getElementById("number").value;
      var maxp = document.getElementById("maxp").value;
      var incorrect = false;
      var alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
      for (n in number)
      {
        for (a in alpha)
        {
          if (number[n] == alpha[a])
          {
            incorrect = true;
          }
        }
      }
      var badmaxp = false;
      for (o in maxp)
      {
        for (a in alpha)
        {
          if (maxp[o] == alpha[a])
          {
            badmaxp = true;
          }
        }
      }
      // Ensure valid number is supplied
      if (number.length < 10 || number.length == 11 || incorrect)
      {
        alert("Please supply a valid ten-digit contact number.");
      }
      // Ensure an original number is supplied
      else if (number == '563-555-1212')
      {
        alert("Please supply an original contact number.");
      }
      // Ensure maxp is filled
      else if (maxp == '' || badmaxp)
      {
        alert("Please supply a valid maximum number of passengers.");
      }
      // Bring up confirm window
      else
      {
        number = number.slice(0, 3) + '-' + number.slice(3, 6) + '-' + number.slice(6);
        map.closeInfoWindow();
        var htmlText = getNewRidePopupHTML3(lat, lng, from, to, maxp, number, earlylate, partofday, month, day, year);
        map.openInfoWindowHtml(new GLatLng(lat, lng), htmlText);
      }  
    }

		function getNewRidePopupHTML3(lat, lng, from, to, maxp, number, earlylate, partofday, month, day, year)
    {/*
      alert("lat = "+lat);
      alert("lng = "+lng);
      alert("from = "+from);
      alert("to = "+to);
      alert("maxp = "+maxp);
      alert("number = "+number);
      alert("earlylate = "+earlylate);
      alert("partofday = "+partofday);
      alert("month = "+month);
      alert("day = "+day);
      alert("year = "+year); */
      var full;
      full = "<b>Is the following information correct?</b><br />";
      full += "From <i>"+from+"</i><br />";
      full += "To <i>"+to+"</i><br />";
      full += "Departing <i>";
      if (earlylate == 0) {
        full += "Early ";
        }
      else {
        full += "Late ";
        }
      if (partofday == 0) {
        full += "Morning, ";
        }
      else if (partofday == 1) {
        full += "Afternoon, ";
        }
      else {
        full += "Evening, ";
        }
      full += numToTextMonth(month) + " " + day + ", " + year + "</i><br />";
      full += "Maximum of <i>" + maxp + "</i> passengers<br />";
      full += "Contact Number: <i>" + number + "</i><br />";
      number = number.slice(0,3) + number.slice(4,7) + number.slice(8);
      full += "<form method='post' action=\"/newride?lat="+lat+"&amp;lng="+lng+"&amp;checked=";
      if (from == "Luther College, Decorah, Iowa") {
        full += "false&amp;to="+to;
        }
      else {
        full += "true&amp;from="+from;
        }
      full += "&amp;maxp="+maxp+"&amp;earlylate="+earlylate+"&amp;";
      full += "partofday="+partofday+"&amp;year="+year+"&amp;";
      full += "month="+month+"&amp;day="+day+"&amp;contact="+number+"\" ";
      full += "><input type='submit' id='submit' name='submit' value='Submit' />";
      full += "<input type='button' id='cancel' name='cancel' value='Back' onclick=\"newRidePopupHTMLPart2(";
      full += lat+", "+lng+", '";
      var checked;
      if (from == "Luther College, Decorah, Iowa") {
        full += to;
        checked = false;
        }
      else {
        full += from;
        checked = true;
        }
      full +="', "+checked.toString()+");\"/></form>";
      return full;
    }

// Adds a popup to the GoogleMap that fits 'ride'
    function addRideToMap(ride, rideNum)
    {
      if (ride.destination.title == "Luther College, Decorah, IA")
      {
        gmarkerOptions['title'] = ride.driver;
        var amarker = new GMarker(new GLatLng(ride.start_point.latitude, ride.start_point.longitude), gmarkerOptions);
        GEvent.addListener(amarker, "click", function()
        {
          amarker.openInfoWindowHtml(getPopupWindowMessage(ride, rideNum));
        });
        ride.marker = amarker;
        map.addOverlay(amarker);
      }
      else if (ride.start_point.title == "Luther College, Decorah, IA")
      {
        rmarkerOptions['title'] = ride.driver;
        var bmarker = new GMarker(new GLatLng(ride.destination.latitude, ride.destination.longitude), rmarkerOptions);
        GEvent.addListener(bmarker, "click", function()
        {
          bmarker.openInfoWindowHtml(getPopupWindowMessage(ride, rideNum));
        });
        ride.marker = bmarker;
        map.addOverlay(bmarker);
      }
      return ride.marker;
    }

// Returns the HTML to be contained in a popup window in the GMap
    function getPopupWindowMessage(ride, rideNum)
    {
      var msg;
      var space_left = ride.max_passengers - ride.num_passengers;
      if (space_left < 1)
      {
        msg = "This ride is full";
      }
      else
      {
        if (space_left == 1)
        {
          msg = "Can take "+space_left+" more person";
        }
        else
        {
          msg = "Can take "+space_left+" more people";
        }
      }
      var disabled;
      var today = new Date();
      if (ride.ToD < new Date(today.getFullYear(), today.getMonth(), today.getDate() + 2))
      {
        disabled = "disabled=\"disabled\"";
        msg = "It is too late to join this ride";
      }
      else if (ride.max_passengers <= ride.num_passengers)
      {
        disabled = "disabled=\"disabled\"";
      }
      else
      {
        disabled = "";
      }
      var text1 = ("Driver: "+ride.driver+"<br><i>"+ride.start_point.title+"</i> --> <i>"+ride.destination.title+"</i><br>Date: "+numToTextMonth(ride.ToD.getMonth())+" "+ride.ToD.getDate()+", "+ride.ToD.getFullYear()+"<br>"+msg);
      var text2 = ("<br /><form method=\"post\" id=\"addPass\" action=\"/addpass?user_name=John%20Doe&ride_key="+ride.key+"\"><input type=\"submit\" value=\"Join this Ride\""+disabled+"/></form>");
      var result = text1 + text2;
      return result;
    }

// Changes a numerical month returned from a Date object to a String
    function numToTextMonth(num)
    {
      if (num==0) {return "January";}
      else if (num==1) {return "February";}
      else if (num==2) {return "March";}
      else if (num==3) {return "April";}
      else if (num==4) {return "May";}
      else if (num==5) {return "June";}
      else if (num==6) {return "July";}
      else if (num==7) {return "August";}
      else if (num==8) {return "September";}
      else if (num==9) {return "October";}
      else if (num==10) {return "November";}
      else if (num==11) {return "December";}
    }
    
    function showAddress(address1) 
    {
      if (geocoder) 
      {
        geocoder.getLatLng(
          address1,
          function(point) 
          {
            if (!point) 
            {
              alert(address1 + " not found");
            }
            else 
            {
              //map.setCenter(point, 13);
              //var marker = new GMarker(point);
              //map.addOverlay(marker);
              map.openInfoWindowHtml(point, getNewRidePopupHTML(point.lat(), point.lng(), address1));
            }
          }
        );
      }
    }

// Class that holds all information for a ride: Maximum passengers, # Passengers already, Start Point, Destination, and Time of Departure
   function Ride(max_passengers, driver, start_point_title, start_point_lat, start_point_long, destination_title, destination_lat, destination_long, ToD, part_of_day, passengers, contact, key)
   {
      this.max_passengers = max_passengers;
      this.num_passengers = passengers.length;
      this.driver = driver;
      this.start_point = new Location(start_point_title, start_point_lat, start_point_long);
      this.destination = new Location(destination_title, destination_lat, destination_long);
      this.ToD = new Date(ToD);
//      this.marker = new GMarker(new GLatLng(this.start_point.latitude, this.start_point.longitude), gmarkerOptions);
      this.part_of_day = part_of_day;
      this.marker = null;
      this.passengers = passengers;
      this.contact = contact;
      this.key = key;
   }

// Class that stores information for a location
   function Location(title, latitude, longitude)
   {
      this.title = title;
      this.latitude = latitude;
      this.longitude = longitude;
   }

// Used to add all months to a drop-down list
   function monthOptions()
   {
      document.write("<option value=\"0\" selected=\"selected\">January</option><option value=\"1\">February</option><option value=\"2\">March</option><option value=\"3\">April</option><option value=\"4\">May</option><option value=\"5\">June</option><option value=\"6\">July</option><option value=\"7\">August</option><option value=\"8\">September</option><option value=\"9\">October</option><option value=\"10\">November</option><option value=\"11\">December</option>");
   }

// Populates the pull-down list for years.  Uses previous year and the following 3
   function yearOptions()
   {
      var today = new Date();
      var yr = today.getFullYear();
      for (var i = yr-1; i < yr+4; i++)
      {
        document.write("<option value=\""+i+"\">"+i+"</option>");
      }
   }

// Modifies the pull-down list for idays according to what is selected for the month
   function changeDays(day, month)
   {
      removeAllOptions(day);
      for(var i = 1; i < 29; i++)
      {
        addOption(day, i.toString(), i.toString());
      }
      if(month.options.valueOf().selectedIndex == 0 || month.options.valueOf().selectedIndex == 2 || month.options.valueOf().selectedIndex == 4 || month.options.valueOf().selectedIndex == 6 || month.options.valueOf().selectedIndex == 7 || month.options.valueOf().selectedIndex == 9 || month.options.valueOf().selectedIndex == 11)
      {
        addOption(day, "29", "29");
        addOption(day, "30", "30");
        addOption(day, "31", "31");
      }
      else if(month.options.valueOf().selectedIndex == "3" || month.options.valueOf().selectedIndex == "5" || month.options.valueOf().selectedIndex == "8" || month.options.valueOf().selectedIndex == "10")
      {
        addOption(day, "29", "29");
        addOption(day, "30", "30");
      } 
   }

// Removes all overlays on the GoogleMap, adds only the popups that fit between the selected years
   function changeDates(imonth, iday, iyear, fmonth, fday, fyear)
   {
      map.clearOverlays();
      map.addOverlay(marker);
      // Change the data from pull-downs to accurate dates
      var today = new Date();
      var yr = today.getFullYear() - 1;
      iyear = iyear + yr;
      fyear = fyear + yr;
      iday = iday + 1;
      fday = fday + 1;

      fDate = new Date(fyear, fmonth, fday);
      iDate = new Date(iyear, imonth, iday);
      var y
      for(y in rides)
      {
        if (rides[y].ToD >= iDate && rides[y].ToD <= fDate)
        {
          map.addOverlay(rides[y].marker);
        }
      }
   }

// Adds the current logged-in person to a Ride
  function addPassengerFromPopup(login, rideNum)
  {
    var ride = rides[rideNum];
    var pass = ride.passengers;
    var addable = true;
    // Check if the logged in person has been added as a passenger already
    for (var num in pass)
    {
      var nam = pass[num].toString();
      if (nam == login)
      { addable = false; }
    }
    // Check if the logged in person is the driver
    if (ride.driver == login)
      { addable = false; }
    if (addable)
    {
      if (ride.max_passengers > ride.num_passengers)
      {
        // Change Ride object
        ride.passengers[ride.num_passengers] = login;
        ride.num_passengers += 1;
    
        // Change table
        var table = document.getElementById("rideTable");
        table.rows[rideNum + 1].cells[2].innerHTML = ride.num_passengers; // Add one for table header
    
        // Change popups
        map.removeOverlay(rides[rideNum].marker);
        var marker = addRideToMap(rides[rideNum], rideNum);

        marker.openInfoWindowHtml("You have been added<br />to this ride!");
      }
      else
      {
        alert("This ride is full.\nNo more passengers can be added.");
      }
    }
    else
    {
      alert("You are already in this ride!");
    }
  }

// Clears a drop-down list
  function removeAllOptions(selectbox)
  {
  	var i;
  	for(i=selectbox.options.length-1;i>=0;i--)
  	{
  		//selectbox.options.remove(i);
  		selectbox.remove(i);
	  }
  }

// Adds an option to a list
  function addOption(selectbox, value, text)
  {
  	var optn = document.createElement("option");
  	optn.text = text;
  	optn.value = value;

  	selectbox.options.add(optn);
  }
