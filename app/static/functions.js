// initalize rides array then plot them.
// The rides array is declared in index.html

//Present

var rides = new Array();
var overlays = new Array();
var windows = new Array();
var events = new Array();
var icons= {};
var map;
var geocoder;
var address2;
var clickListener;
var mc;
var clusterClick = false;
var directionsService;
var directionsDisplay;

var mycollege = new College("Luther College", "700 College Drive Decorah,IA", 43.313059, -91.799501);
//var mycollege = new College("UW-LaCrosse","1725 State Street, La Crosse, WI",43.812834,-91.229022);
//var mycollege = new College("Decorah","Decorah, IA",43.303306,-91.785709);


function initialize(mess) 
{
    
	var request = new XMLHttpRequest();
	var today = new Date();
	request.open("GET","/getrides?circle="+getParameterByName("circle")+"&after="+today.getFullYear()+"-"+(today.getMonth()+1)+"-"+today.getDate(),false);
	request.send(null);
	if (request.status == 200) {
	    // loop over all
	    rides = eval(request.responseText);
	    for (r in rides) {
		var tod = rides[r].ToD;
		rides[r].ToD = new Date(tod.substring(0,4),tod.substring(5,7)-1,tod.substring(8,10));
	    }

    var request2 = new XMLHttpRequest();
    request2.open("GET","/getevents?circle="+getParameterByName("circle")+"&after="+today.getFullYear()+"-"+(today.getMonth()+1)+"-"+today.getDate(),false);
    request2.send(null);
    if (request.status == 200) {
        // loop over all
        events = eval(request2.responseText);
        console.log(events)
        for (e in events) {
        var tod = events[e].ToD;

        events[e].ToD = new Date(tod.substring(0,4),tod.substring(5,7)-1,tod.substring(8,10));
        }
    }

	
	// Begin creation of Icons for Rides
    var eventIconMarker = new google.maps.MarkerImage('static/stargate.png',
            new google.maps.Size(30,40),
            null,
            new google.maps.Point(20,20));

        var shadow = new google.maps.MarkerImage("http://labs.google.com/ridefinder/images/mm_20_shadow.png",{
            size:new google.maps.Size(22,20)});

        var eventIcon ={
            icon: eventIconMarker
            };
        icons.event= eventIcon;

	var greenIconMarker = new google.maps.MarkerImage('static/carGreen.png',
            new google.maps.Size(30,40),
            null,
            new google.maps.Point(20,20));

        var shadow = new google.maps.MarkerImage("http://labs.google.com/ridefinder/images/mm_20_shadow.png",{
            size:new google.maps.Size(22,20)});

        var greenIcon ={
            icon: greenIconMarker
            };
        icons.green= greenIcon;

	gmarkerOptions = { icon:greenIcon };

        var redIconMarker = new google.maps.MarkerImage('static/carRed.png',
            null,
            null,
            null);

        var redIcon = {
            icon: redIconMarker
            };
        icons.red = redIcon;

	rmarkerOptions = { icon:redIcon };

	// Sample custom marker code created with Google Map Custom Marker Maker
	// http://www.powerhut.co.uk/googlemaps/custom_markers.php
	
	var myIconMarker = new google.maps.MarkerImage('static/image.png',
            new google.maps.Size(30,28), 
            null,
            new google.maps.Point(10,17));


        var myIcon ={
            icon: myIconMarker
            };
        icons.my = myIcon;

        var blueIconMarker = new google.maps.MarkerImage('static/person.png',
            new google.maps.Size(30,40),
            null,
            new google.maps.Point(20,20));

        var blueshadow = new google.maps.MarkerImage('static/shadow.png',
            new google.maps.Size(29,16));

        var blueIcon ={
            icon: blueIconMarker
            };

        icons.blue = blueIcon;

	var conMarker = new google.maps.MarkerImage('static/cross.png',
			new google.maps.Size(30,40),
			null,
			new google.maps.Point(20,20));
			
	var conIcon = {
			icon:conMarker
			};
	icons.con =conIcon;

	var mymarker = new google.maps.Marker(new google.maps.LatLng(43.313059,-91.799501));
        mymarker.setOptions(icons.my);
        

        reqMarkerOptions = {icon:blueIcon};

        var centerLL = new google.maps.LatLng(43.313059,-91.799501);
        var myOptions = {
	    draggableCursor: 'crosshair',
	    center: centerLL,
	    mapTypeId: google.maps.MapTypeId.ROADMAP,
	    zoom: 6
        };
        map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

        directionsService = new google.maps.DirectionsService();
        directionsDisplay = new google.maps.DirectionsRenderer({preserveViewport:false});
        

    // TODO
	mc = new MarkerClusterer(map);
	mc.setGridSize(30);
    google.maps.event.addListener(mc, "clusterclick", function(cluster){
	    clusterClick = true;
	});

        geocoder = new google.maps.Geocoder();
        google.maps.event.addListener(mymarker, "click", function()
			   { windowOpen(centerLL,"Luther College<br />Decorah, Iowa"); });


        var r;
        for(r in rides)
        {
            addRideToMap(rides[r], r);
        }
    }
    getRidesForConnection();
    clickListener = google.maps.event.addListener(map, "click", getAddress);

        var e;
        for (e in events)
        {
            addEventToMap(events[e],e);
            
        }
        
    makeRideTable();
    
    if (mess) {
	alert(mess);
    }

}


function makeRideTable() {


    var table = document.getElementById("rideTableBody");

    for(var i = table.rows.length; i > 1;i--) {
	table.deleteRow(i -1);
    }
    var r;
    for (r in rides)
    {
	var row = table.insertRow(table.rows.length);
	var c0 = row.insertCell(0);
        if (rides[r].drivername!=null){
	c0.innerHTML = '<a href="/driverrating?drivernum=' + rides[r].driver + '">'+ rides[r].drivername + '</a>';
        }
        else{
        c0.innerHTML= "needs driver";
        }
	var c1 = row.insertCell(1);
	c1.innerHTML = rides[r].max_passengers - rides[r].num_passengers;
	var c3 = row.insertCell(2);
	c3.innerHTML = rides[r].start_point_title;
	var c4 = row.insertCell(3);
	if (rides[r].driver == "needs driver") {
	c4.innerHTML = '<a href="#" onClick="addDriverToRideNumber(' + r + ')">' + rides[r].destination_title + '</a>';
	} else {
	c4.innerHTML = '<a href="#" onClick="joinRideByNumber(' + r + ')">' + rides[r].destination_title + '</a>';
	}
	var c5 = row.insertCell(4);
	var myToD = rides[r].ToD;
	c5.innerHTML = rides[r].part_of_day + " " + numToTextMonth(myToD.getMonth())+" "+myToD.getDate()+", "+myToD.getFullYear();
	var c6 = row.insertCell(5);
	c6.innerHTML = rides[r].comment;
    }
    $("#rideTable").dataTable();
}

function getAddress(event)
{ 
  setTimeout(function(){
    if (!clusterClick){
       if (event != null) 
       {
           address2 = event.latLng;
           geocoder.geocode({latLng:event.latLng}, showAddressClick);
       }
     }
    else{
       clusterClick = false;
     }
    },0);
}

function showAddress(address1) 
{
    if (geocoder) 
    {
        geocoder.geocode(
            {address:address1},
            function(results, status) 
            {
		if (status != google.maps.GeocoderStatus.OK) 
		{
		    alert(address1+" not found.");
		}
		else 
		{
		    
            var point = results[0].geometry.location;
            windowOpen(point,getEventOrRideHTML(point.lat(),point.lng(), results[0].formatted_address,getParameterByName("circle")));
		    //map.openInfoWindowHtml(point, getNewRidePopupHTML(point.lat(), point.lng(), address1)); 
		//// JUST ADDED ////
	    	//windowOpen(new google.maps.LatLng(point.lat(),point.lng()),getEventOrRideHTML(point.lat(), point.lng(), address1));  
		}
            }
        );
    }
}

function showAddressClick(results,status) 
{
    if (!status || status != google.maps.GeocoderStatus.OK) 
    {
        alert("Status:" + status);
    } 
    else 
    {
        google.maps.event.removeListener(clickListener);
        var point = results[0].geometry.location;
        windowOpen(point,getEventOrRideHTML(point.lat(),point.lng(), results[0].formatted_address,getParameterByName("circle")));
    	//windowOpen(point, getEventOrRide());
    }
}

function getEventOrRideHTML(lat, lng, address,circle){

    $('#to_loc').text("Create a ride from "+mycollege.name+" to "+address);
    $('#from_loc').text("Create a ride to "+mycollege.name+" from "+address);
    $('#dAddress').text(address);
    $('.dCollege').text(mycollege.name);

    $('#lat').val(lat);
    console.log($('#lat').val());
    $('#lng').val(lng);
    console.log($('#lng').val());
    $('#circleType').val(circle);
    $('#address').val(address);
    $('#collegeName').val(mycollege.name);

    //var html = "<b> Are you creating a new event or an individual ride?</b></br>";
    var html = "<b>Are you creating a new event or an individual ride?</b></br>";

	// CHANGED TO BUTTONS
	//html += "<input type=\"button\" value=\"Ride\" id=\"Ride\" /><br />";
    html += "<input onclick=\"$('#rideWrapper').modal({escClose: false, \
							onOpen: function(dialog) {\
								dialog.overlay.fadeIn('medium', function() {\
									dialog.container.show();\
									dialog.data.show();\
								});\
							},\
							onClose: function(dialog) {\
								dialog.data.fadeOut('medium', function() {\
									dialog.container.hide('medium', function() {\
										$.modal.close();\
										location.reload();\
									});\
								});\
							}\
						});\" type=\"button\" value=\"Ride\" id=\"Ride\" /><br />";
    html += "<input onclick=\"$('#eventWrapper').modal({escClose: false, \
							onOpen: function(dialog) {\
								dialog.overlay.fadeIn('medium', function() {\
									dialog.container.show();\
									dialog.data.show();\
								});\
							},\
							onClose: function(dialog) {\
								dialog.data.fadeOut('medium', function() {\
									dialog.container.hide('medium', function() {\
										$.modal.close();\
										location.reload();\
									});\
								});\
							}\
						});\" type=\"button\" value=\"Event\" id=\"Event\" /><br />";

    
	/* Try to incorporate recursive call to get dialog box back up??? getEventOrRideHTML("+lat+","+lng+","+address+") */

    return html;

}

// 
// function startEventCreationPopup(lat,lng, address){
// 
//     var html = "<b>Create a New Event</b></br>"
//     html+= "Event Name: <input type=\"text\" id=\"eventname\" name=\"eventname\" size=\"35\"></br>"
//     html+="<select name=\"month\" id='month' onChange=\"changeDays(document.getElementById('day'), this); return false;\">" + getMonthOptions() + "</select>";
//     html+="<select name=\"day\" id=\"day\">";
//     var today = (new Date()).getDate();
//     
//     for (var i = 1; i < 32; i++)
//     {
//         html+= "<option value=\""+i+"\" ";
//     if ( today+2 == i ) {
//         html+= "selected=\"selected\"";
//         }
//     html+= ">"+ i + "</option>";
//     }
//     html+= "</select>";
//     html+="<select name=\"year\" id='year'>";
//     var yr = (new Date()).getFullYear();
//     for (var i = yr-1; i < yr+4; i++)
//     {
//         html+="<option value=\""+i+"\"";
//         if (i == yr)
//             html+= "selected=\"selected\"";
//         {
//         }
//         html+= ">"+i+"</option>";
//     }
//     html+="</select></div>";
//     html+="Time:<input type='text' id='time' size=\"10\"/>"
//     html += "<div id=\"buttons\"><input type=\"submit\" id=\"submit\" name=\"submit\" value=\"Create Event\" onclick=\"saveEvent("+lat+", "+lng+", '"+address+"'); return false;\"'>"
//     windowOpen(new google.maps.LatLng(lat, lng),html);
// 
// }
// 
// function saveEvent(lat,lng,address){
//     var event = {};
//     event["name"] = document.getElementById("eventname").value;
//     event["month"] = document.getElementById("month").value;
//     event["day"] = document.getElementById("day").value;
//     event["year"]= document.getElementById("year").value;
//     event["lat"] = lat;
//     event["lng"] = lng;
//     event["address"] = address;
//     event["circle"] = getParameterByName("circle");
//     event["time"] = document.getElementById("time").value;
//     
//     var request = new XMLHttpRequest();
// 
//     var reqStr = '/newevent?';
// 
//   
//     for (var prop in event) {
//     reqStr += prop + "=" + event[prop] + "&";
//     }
//     request.open("GET",reqStr,false);
//     request.send(null);
//     clickListener = google.maps.event.addListener(map, "click", getAddress);
//     if (request.status == 200) {
//     initialize();
//     } else {
//     alert("An error occurred, check your responses and try again.");
//     }
//
// }


// Returns the Inital form used in the ride creation process...
// o From Luther to
//    address.....
// o To Luther
//
// 
// function  saveEventRide(vals) {
// 
//     var request = new XMLHttpRequest();
// 
//     var reqStr = '/neweventride?';
// 
//     console.log(vals);
//     for (var prop in vals) {
//     reqStr += prop + "=" + vals[prop] + "&";
//     }
// 
//     request.open("GET",reqStr,false);
//     request.send(null);
//     clickListener = google.maps.event.addListener(map, "click", getAddress);
//     if (request.status == 200) {
//     initialize();
//     } else {
//     alert("An error occurred, check your responses and try again.");
//     }
// 
// }
// 
// function saveRide(vals) {
// 
//     var request = new XMLHttpRequest();
// 
//     var reqStr = '/newride?';
// 
// 
//     for (var prop in vals) {
// 	reqStr += prop + "=" + vals[prop] + "&";
//     }
// 
//     request.open("GET",reqStr,false);
//     request.send(null);
//     clickListener = google.maps.event.addListener(map, "click", getAddress);
//     if (request.status == 200) {
// 	initialize();
//     } else {
// 	alert("An error occurred, check your responses and try again.");
//     }
// 
// }

function addEventToMap(event, eventnum)
{
    var amarker = new google.maps.Marker({position:new google.maps.LatLng(event.lat,event.lng)});
    amarker.name = event.name;
    amarker.id = event.id;
    amarker.setOptions(icons.event);
    amarker.setMap(map);
    //event.marker = amarker; 
    overlays.push(amarker);
    google.maps.event.addListener(amarker,"click",function(){
        var s = "ss";
        if (amarker.getPosition()){ 
            var request = new XMLHttpRequest();
            var today = new Date();
            request.open("GET","/getrides?circle="+getParameterByName("circle")+"&event="+event.id+ "&after="+today.getFullYear()+"-"+(today.getMonth()+1)+"-"+today.getDate(),false);
            request.send(null);

            var myrides = new Array();
            if (request.status == 200) {
        // loop over all
                console.log(eval(request.responseText));
                myrides = eval(request.responseText);
                if (myrides.length>0){
                var html = "<b> Event Rides</b></br>";
                html += "<table>"
                html += '<tr>';
                html +=    '<th>Driver</th>';
                html +=    '<th>Spots available</th>';
                html +=    '<th>Date</th>';
                html +=    '<th>Phone #</th>'
                html +=    '<th></th>'
                html +=    '</tr>'
                for (r in myrides) {
                    var ride = myrides[r];
                   
                    var tod = myrides[r].ToD;
                    myrides[r].ToD = tod.substring(5,7)-1+"-"+tod.substring(8,10)+"-"+tod.substring(0,4);
                     html +="<tr>"
                    if (ride.drivername != null){
                    html +=    '<td>'+ride.drivername+'</td>';
                    }
                    else{
                    html +=    '<td>No driver</td>';
                    }
                    html +=    '<td>'+(parseInt(ride.max_passengers) - parseInt(ride.num_passengers)).toString()+'</td>';
                    html +=    '<td>'+ride.ToD+'</td>';
                    html +=    '<td>'+ride.contact+'</td>'
                    if (ride.drivername == null){
                        var funcall = 'addDriverPopupforEvent('+JSON.stringify(ride)+','+JSON.stringify(event)+')';

                        html += "<td><input onclick='"+ funcall + "' type='button' value='Join' \>"
                    }
                    else{
                        var funcall = 'joinEventRideByNumber('+JSON.stringify(ride)+','+JSON.stringify(event)+')';

                        html += "<td><input onclick='"+funcall+"' type='button' value='Join' \>"

                    }
                    html+="</tr>"
                }
                html+="</table>"
                html += "<input onclick=\"startRideCreationPopup("+event.lat+", "+event.lng+", '" + event.address +"', '"+event.id+"')\" value=\"Create New Ride for Event\" type=\"button\" "+"/><br />";
            }
            else{
                console.log("sadz")
                html = "<p>There are no rides currently offered for " + event.name+"</p>"
                html += "<input onclick=\"startRideCreationPopup("+event.lat+", "+event.lng+", '" + event.address +"', '"+event.id+"')\" value=\"Create New Ride for Event\" type=\"button\" "+"/><br />";

            }

        }
        
            console.log(html);
            
            windowOpen(amarker.getPosition(), html);

        }

    })

}

// Adds a popup to the GoogleMap that fits 'ride'
function addRideToMap(ride, rideNum)
{
    if (ride.driver == "needs driver") {
	var tooltext = 'needs driver';
	reqMarkerOptions['title'] = tooltext;
	if (ride.destination_title == mycollege.name) {
            var amarker = new google.maps.Marker({position:new google.maps.LatLng(ride.start_point_lat, ride.start_point_long)});
            amarker.setOptions(icons.blue);
	} else {
            var amarker = new google.maps.Marker({position:new google.maps.LatLng(ride.destination_lat, ride.destination_long)});
            amarker.setOptions(icons.blue);
	}
        google.maps.event.addListener(amarker, "click", function()
			   {
			       if (amarker.getPosition()) {
                                   windowOpen(amarker.getPosition(),addDriverPopup(ride, rideNum, amarker.getPosition().lat(), amarker.getPosition().lng()));
			       }
			   });
        ride.marker = amarker;
        amarker.setMap(map);
        overlays.push(amarker);
        mc.addMarker(amarker);
        //pathListener(amarker);
        //checkSame(amarker);
    } else if (ride.destination_title == mycollege.name)
    {
        var tooltext = '';
        tooltext += ride.ToD;
        gmarkerOptions['title'] = tooltext;
        var amarker = new google.maps.Marker({position:new google.maps.LatLng(ride.start_point_lat, ride.start_point_long)});
        amarker.setOptions(icons.green);
        google.maps.event.addListener(amarker, "click", function()
			   {
			       if (amarker.getPosition()) {
                                   windowOpen(amarker.getPosition(),getPopupWindowMessage(ride, rideNum, amarker.getPosition().lat(), amarker.getPosition().lng()));
			       }
			   });
        ride.marker = amarker;
        amarker.setMap(map);
        overlays.push(amarker);
        mc.addMarker(amarker);
        //pathListener(amarker);
        //checkSame(amarker);
    }
    else if (ride.start_point_title == mycollege.name)
    {
        var tooltext = '';
        tooltext += ride.ToD;
        rmarkerOptions['title'] = tooltext;
        var bmarker = new google.maps.Marker({position:new google.maps.LatLng(ride.destination_lat, ride.destination_long)});
        bmarker.setOptions(icons.red);

        google.maps.event.addListener(bmarker, "click", function()
			   // From function() to function(latlng)
			   {
			       if (bmarker.getPosition()) {
                                   windowOpen(bmarker.getPosition(),getPopupWindowMessage(ride, rideNum, bmarker.getPosition().lat(), bmarker.getPosition().lng()));
			       }
			   });
        ride.marker = bmarker;
        bmarker.setMap(map);
        overlays.push(bmarker);
        mc.addMarker(bmarker);
    }
    return ride.marker;
}

function joinRideByNumber(rideNum) {
    rides[rideNum].marker.setMap(null);
    rides[rideNum].marker=null;
    var marker = addRideToMap(rides[rideNum], rideNum);
    
    overlays.push(marker);
    
    windowOpen(marker.getPosition(),getPopupWindowMessage(rides[rideNum], 
						    rideNum, 
						    rides[rideNum].destination_lat,
						    rides[rideNum].destination_long));
}

/* 
   Returns the HTML to be contained in a popup window in the GMap
   Asks whether the user wants to join this ride
*/
function getPopupWindowMessage(ride, rideNum, lat, lng)
/*
 * ride -- a full ride object as constructed in index.html
 * rideNum  - the index of the ride in the rides array in index.html
 * lat -- latitude
 * lng -- longitude 
 */
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
    if (ride.ToD.getDate == new Date(today.getFullYear(), today.getMonth(), today.getDate()))
    {
        disabled = "disabled=\"disabled\"";
        msg = "It is too late to join this ride. <br />You might try to call the driver directly at: " + ride.contact;
    }
    else if (ride.max_passengers <= ride.num_passengers) {
        disabled = "disabled=\"disabled\"";
    }
    else {
        disabled = "";
    }
     var text1 = ("Driver: "+ride.drivername+"<br><i>"+ride.start_point_title+"</i> --> <i>"+ride.destination_title+"</i><br>Date: "+ride.part_of_day+" "+numToTextMonth(ride.ToD.getMonth())+" "+ride.ToD.getDate()+", "+ride.ToD.getFullYear()+"<br>"+msg);
    var drop_off_or_pick_up; // drop_off = 0, pick_up = 1
    if (ride.start_point_title == mycollege.name) {
        drop_off_or_pick_up = 0;
    }
    else {
        drop_off_or_pick_up = 1;
    }
    text1 += "<br />" + ride.comment + "<br />";

    var text2 = ("<br /><form id=\"addPass\" onsubmit=\"addPassengerPart2('"+ride.key+"', "+drop_off_or_pick_up+", "+lat+", "+lng+", "+rideNum+"); return false;\"><input type=\"submit\" value=\"Join this Ride\""+disabled+"/></form>");
    //var text2= "<input type='button' name='OK' value='Join this Ride'"+disabled+" onclick='addPassengerPart2('"+ride.key+"', "+drop_off_or_pick_up+", "+lat+", "+lng+", "+rideNum+"); return false;'>";
    var result = text1 + text2;
    return result;
}

function addDriverToRideNumber(rideNum) {
    rides[rideNum].marker.setMap(null);
    rides[rideNum].marker=null;
    var marker = addRideToMap(rides[rideNum], rideNum);
    /*for (amarker in overlays)
      {  
        if (marker.getPosition() == amarker.getPosition()){
              windowOpen(marker.getPosition(),addDriverPopup(rides[rideNum], rideNum, rides[rideNum].destination_lat, rides[rideNum].destination_long));
              return;
              }
      }*/
    marker.setMap(map);
    overlays.push(marker);
    
    windowOpen(marker.getPosition(),addDriverPopup(rides[rideNum], rideNum, rides[rideNum].destination_lat, rides[rideNum].destination_long));
}

function addDriverPopup(ride, rideNum, lat, lng) {
    ride.rideNum = rideNum;
    var htmlText = "<b>Driver Needed</b> <br />";
    htmlText += "{start_point_title} --> {destination_title}<br />";
    htmlText += "{part_of_day} {ToD}<br />";
    htmlText += '<input type="radio" name="driver" value="0" onclick="getDriverContact({rideNum});" />I will drive<br />';
    htmlText += '<input type="radio" name="rider" value="0" onclick="joinRideByNumber({rideNum});" />I need a ride too';

    var t = jsontemplate.Template(htmlText);
    var s = t.expand(ride);

    return s;
}

function getDriverContact(rideNum) {
    ride = rides[rideNum];
    htmlText = "Thanks for driving!<br />";
    htmlText += 'Contact number:  <input type="text" id="drivercontact" name="dcontact" value="AAA-PPP-LLLL" /><br />';
    htmlText += 'Number of Passengers:  <input type="text" id="numpass" name="numpass" value="3" /><br />';
    htmlText += '<input type="button" name="OK" value="OK" onclick="addDriverToRide({rideNum});">';
    htmlText += '<input type="button" name="Cancel" value="Cancel" onclick="closePopup({rideNum});"><br />';

    var t = jsontemplate.Template(htmlText);
    ride.marker.setMap(null);
    ride.marker=null;
    var marker = addRideToMap(rides[rideNum], rideNum);
    overlays.push(marker);
    windowOpen(marker.getPosition(),t.expand(ride));
    //marker.openInfoWindowHtml(t.expand(ride));
}

function addDriverPopupforEvent(ride,event) {
    //ride.rideNum = rideNum;
    console.log(ride);

    console.log(event.address);
    var htmlText = "<b>Driver Needed</b> <br />";
    htmlText +=  ride.start_point_title +"--> "+event.address+"<br />";
    var funcall1 = 'getDriverContactforEvent('+JSON.stringify(ride)+','+JSON.stringify(event)+')'
    var funcall2 =  'joinEventRideByNumber('+JSON.stringify(ride)+','+JSON.stringify(event)+')'
    htmlText += "<input type='radio' name='driver' value='0' onclick='"+funcall1+"' />I will drive<br />";
    htmlText += '<input type="radio" name="rider" value="0" onclick="'+funcall2+'" />I need a ride too';

    //var t = jsontemplate.Template(htmlText);

    //var s = t.expand(ride);

    windowOpen(new google.maps.LatLng(event.lat, event.lng), htmlText);
}

function getDriverContactforEvent(ride,event){

    var funcall = 'addDriverToEventRide('+JSON.stringify(ride)+')';
    htmlText = "Thanks for driving!</br> Please fill out the information below.<br />";
    htmlText += 'Contact number:  <input type="text" id="drivercontact" name="dcontact" value="AAA-PPP-LLLL" /><br />';
    htmlText += 'Number of Passengers:  <input type="text" id="numpass" name="numpass" value="3" /><br />';
    htmlText += "<input type='button' name='OK' value='OK' onclick='"+funcall+"'>";
    console.log(event.lat)
    windowOpen(new google.maps.LatLng(parseFloat(event.lat),parseFloat(event.lng)),htmlText);

}

function addDriverToEventRide(ride) {
    driverContact = document.getElementById("drivercontact").value;
    numPass = document.getElementById("numpass").value;
    if (validatePhoneNumber(driverContact)) {
    submitDriverForRide(ride,driverContact,numPass);
    } else {
    alert("Please supply a valid 10-digit contact number");
    }
}

function joinEventRideByNumber(ride,event){

    windowOpen(new google.maps.LatLng(parseFloat(event["lat"]),parseFloat(event["lng"])),getEventPopupWindowMessage(ride,
                            parseFloat(ride["destination_lat"]),
                            parseFloat(ride["destination_long"]),
                            event));

}

function getEventPopupWindowMessage(ride, lat, lng,event){
 console.log(ride.ToD);
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
    if (ride.ToD.getDate == new Date(today.getFullYear(), today.getMonth(), today.getDate()))
    {
        disabled = "disabled=\"disabled\"";
        msg = "It is too late to join this ride. <br />You might try to call the driver directly at: " + ride.contact;
    }
    else if (ride.max_passengers <= ride.num_passengers) {
        disabled = "disabled=\"disabled\"";
    }
    else {
        disabled = "";
    }
    var rideDate = new Date(ride.ToD);
     var text1 = ("Driver: "+ride.drivername+"<br><i>"+ride.start_point_title+"</i> --> <i>"+ride.destination_title+"</i><br>Date: "+ride.part_of_day+" "+numToTextMonth(rideDate.getMonth())+" "+rideDate.getDate()+", "+rideDate.getFullYear()+"<br>"+msg);
    
    text1 += "<br />" + ride.comment + "<br />";

    //var text2 = ("<br /><form id=\"addPass\" onsubmit=\"getEventPassengerInfo('"+ride.key+"',"+event+"); return false;\"><input type=\"submit\" value=\"Join this Ride\""+disabled+"/></form>");
    //var text2= "<input type='button' name='OK' value='Join this Ride'"+disabled+" onclick='addPassengerPart2('"+ride.key+"', "+drop_off_or_pick_up+", "+lat+", "+lng+", "+rideNum+"); return false;'>";
    var funcall = 'getEventPassengerInfo("'+ride.key+'",'+JSON.stringify(event)+')'
    var text2 = "<input type='button' name='OK' value='Join this Ride'"+disabled+" onclick='"+funcall+"' />";
    var result = text1 + text2;
    return result;
}

function getEventPassengerInfo(ride_key, event){
    console.log("what");
    var funcall = 'checkEventPassengerInfo("'+ride_key+'",'+JSON.stringify(event)+')'
    html = "<b>Please provide your phone number:</b></br>"
    html += "Contact: <input type='text' id='contact' maxlength='12' size='14' value='563-555-1137' onclick='this.value=\"\"' /><br />";
    html += "<input type='button' onclick='"+funcall+"' value='Submit' />";
    html += "<input type='button' onclick='initialize()' value='Cancel' />"; //TODO:  something other than init here
    windowOpen(new google.maps.LatLng(event.lat,event.lng),html);
}

function checkEventPassengerInfo(ride_key, event){

    var contact = document.getElementById('contact').value;
    var badcontact = false;
    badcontact = ! validatePhoneNumber(contact);

    if (badcontact) { // Contains letter(s)
        alert("Please supply a valid contact number using only numbers and dashes.");
    }
    else if (contact == '' || contact.length == 11 || contact.length < 10) { // Number is too short or too long
        alert("Please supply a 10 digit contact number");
    }
    else if (contact == '563-555-1212') { // Didn't change from example
        alert("Please supply an original contact number");
    }
    else {
        if (contact.length == 10) { // 3194317934 => 319-431-7934
            contact = contact.slice(0,3)+"-"+contact.slice(3,6)+"-"+contact.slice(6);
        }
    var funcall = 'saveNewPass("'+ride_key+'","'+contact+'","'+event.address+'",'+event.lat+','+event.lng+');clickListener = google.maps.event.addListener(map, "click", getAddress);';

        var text = "<form>";
        text += '<h4>Is the following information correct?</h4>';
        text += 'Contact: '+contact+'<br /></br>';
        text += "<input type='button' id='submit' value='Submit' onclick='"+funcall+"' />";
        text += "<input type='button' id='back' value='Back' onclick='openWindow(new google.maps.LatLng("+event.lat+", "+event.lng+"),getEventPassengerInfo("+ride_key+","+JSON.stringify(event)+" ));'/></form>";
        //text += "<input type='button' id='back' value='Back' onclick='var window = new google.maps.InfoWindow({position:new google.maps.LatLng("+lat+", "+lng+"),content:getPopupWindowMessage2("+rideNum+", "+doOrPu+", "+lat+", "+lng+", \""+address+"\", \""+contact+"\")});' /></form>";                  
    //(text);
        windowOpen(new google.maps.LatLng(event.lat, event.lng),text);
        //rides[rideNum].marker.openInfoWindow(text);
    }
}

function closePopup(rideNum) {
    ride.marker.setMap(null);
    var marker = addRideToMap(rides[rideNum], rideNum);
    overlays.push(marker);
    clickListener = google.maps.event.addListener(map, "click", getAddress);
}

function addDriverToRide(rideNum) {
    driverContact = document.getElementById("drivercontact").value;
    numPass = document.getElementById("numpass").value;
    if (validatePhoneNumber(driverContact)) {
	submitDriverForRide(rides[rideNum],driverContact,numPass);
    } else {
	alert("Please supply a valid 10-digit contact number");
    }
}

function submitDriverForRide(ride,contact,numPass) {
    var request = new XMLHttpRequest();

    request.open("GET","/adddriver?key="+ride.key+"&contact="+contact+"&numpass="+numPass,false);
    request.send(null);
    clickListener = google.maps.event.addListener(map, "click", getAddress);
    if (request.status == 200) {
	initialize();
    } else {
	alert("An error occurred, check your responses and try again.");
    }
}

function validatePhoneNumber(phone) {
    var incorrect = false;
    phone = phone.replace(/-/g,"");
    phone = phone.replace(/ /g,"");
    phone = phone.replace(/\./g,"");

    if (/\d{10}/.test(phone)) {
	return true;
    } else {
	return false;
    }
}

/*
  Sets up map to use clicks to create a pick up or drop off point for a ride
  Options out: click on map, 'Use this Location', or 'Cancel'
*/
// drop_off = 0, pick_up = 1
function addPassengerPart2(ride_key, drop_off_or_pick_up, lat, lng, rideNum)
{
    // remove all listeners
    google.maps.event.clearListeners(map, 'click');
    overlays.length=0;
    //map.clearOverlays();
   
    // Keep marker for ride's location (lat, lng)
    var thismarker = rides[rideNum].marker;

    // Create text for popup window
    var infowindowtext = '';
    infowindowtext += 'Would you like to be ';
    if (drop_off_or_pick_up == 1) {
        infowindowtext += 'picked up';
    }
    else {
        infowindowtext += 'dropped off';
    }
    infowindowtext += ' at this location?<br />If not, please click the "Use other location" button, then click on the map to select a new ';
    if (drop_off_or_pick_up == 1) {
        infowindowtext += 'pick up';
    }
    else {
        infowindowtext += 'drop off';
    }
    infowindowtext += ' point.<br />';
    infowindowtext += "<input type='button' onclick='windowOpen(rides["+rideNum+"].marker.getPosition(),getPopupWindowMessage2("+rideNum+", "+drop_off_or_pick_up+", "+lat+", "+lng+", \"\"));' value='Use this location' />";
    infowindowtext += "<input type='button' onclick='windows.pop().close();selectAddress("+drop_off_or_pick_up+","+rideNum+","+false+");' value='Use other Location' />";
    infowindowtext += "<input type='button' onclick='initialize()' value='Cancel' />"; //TODO:  something other than init here
    windowOpen(thismarker.getPosition(),infowindowtext);
    google.maps.event.addListener(thismarker, 'click', function(event)
		       {
			   if (event) {
                               windowOpen(thismarker.getPosition(),infowindowtext);
		                       }
		       });
    thismarker.setMap(map);
    overlays.push(thismarker);
    //map.addOverlay(thismarker);
}

function getPopupWindowMessage2(rideNum, doOrPu, lat, lng, address8, contact)
{
    google.maps.event.removeListener(clickListener);
    contact = (typeof contact == 'undefined') ? '563-555-1212': contact; // If contact is not defined, then let it be 563-555-1212
    if (address8 == '') {
        if (doOrPu == 0) {
            address8 = rides[rideNum].destination_title;
        }
        else {
            address8 = rides[rideNum].start_point_title;
        }
    }
    var text = "Please ensure that your address is as specific as possible<br />(<i>37</i> Main Street, not <i>30-50</i> Main Street)<br />";
    if (doOrPu == 0) {
        text += "Drop Off At: ";
    }
    else {
        text += "Pick Up At: ";
    }
    text += "<input type='text' id='address' value='"+address8+"' size='30' /><br />";
    text += "Contact: <input type='text' id='contact' maxlength='12' size='10' value='"+contact+"' onclick='this.value=\"\"' /><br />";
    text += "<input type='button' name='Okay' value='Okay' onclick='addPassengerPart3("+rideNum+", "+lat+", "+lng+", "+doOrPu+"); return false;'>";
    //text += "<input type='submit' id='submit' value='Okay' />";
    var ride_key = rides[rideNum].key;
    text += "<input type='button' id='back' value='Back' onclick='addPassengerPart2(\""+ride_key+"\", "+doOrPu+", "+lat+", "+lng+", "+rideNum+"); return false;' /></form>";
    return text;
}

function addPassengerPart3(rideNum, lat, lng, doOrPu) {
    var contact = document.getElementById('contact').value;
    var address = document.getElementById('address').value;
    var badcontact = false;
    
    badcontact = ! validatePhoneNumber(contact);

    if (badcontact) { // Contains letter(s)
        alert("Please supply a valid contact number using only numbers and dashes.");
    }
    else if (contact == '' || contact.length == 11 || contact.length < 10) { // Number is too short or too long
        alert("Please supply a 10 digit contact number");
    }
    else if (contact == '563-555-1212') { // Didn't change from example
        alert("Please supply an original contact number");
    }
    else if (address == '') {
        alert("Please supply an address");
    }
    else {
        if (contact.length == 10) { // 3194317934 => 319-431-7934
            contact = contact.slice(0,3)+"-"+contact.slice(3,6)+"-"+contact.slice(6);
        }
	var funcall = 'saveNewPass("'+rides[rideNum].key+'","'+contact+'","'+address+'",'+lat+','+lng+');clickListener = google.maps.event.addListener(map, "click", getAddress);';

        var text = "<form>";
        text += '<h4>Is the following information correct?</h4>';
        text += 'Address: '+address+'<br />';
        text += 'Contact: '+contact+'<br />';
        text += "<input type='button' id='submit' value='Submit' onclick='"+funcall+"' />";
        text += "<input type='button' id='back' value='Back' onclick='openWindow(new google.maps.LatLng("+lat+", "+lng+"),getPopupWindowMessage2("+rideNum+", "+doOrPu+", "+lat+", "+lng+", \""+address+"\", \""+contact+"\"));'/></form>";
        //text += "<input type='button' id='back' value='Back' onclick='var window = new google.maps.InfoWindow({position:new google.maps.LatLng("+lat+", "+lng+"),content:getPopupWindowMessage2("+rideNum+", "+doOrPu+", "+lat+", "+lng+", \""+address+"\", \""+contact+"\")});' /></form>";                  
	//(text);
        windowOpen(rides[rideNum].marker.getPosition(),text);
        //rides[rideNum].marker.openInfoWindow(text);
    }
}

function saveNewPass(ride_key, contact, address, lat, lng) {
    var request = new XMLHttpRequest();
    var reqStr = '/addpass?';

    reqStr += 'ride_key='+ride_key+'&';
    reqStr += 'contact='+contact+'&';
    reqStr += 'address='+address+'&';
    reqStr += 'lat='+lat+'&';
    reqStr += 'lng='+lng;

    request.open("GET",reqStr,false);
    request.send(null);
    if (request.status == 200) {
	initialize();
    } else {
	alert("An error occurred, check your responses and try again.");
    }

}

// Changes a numerical month returned from a Date object to a String
function numToTextMonth(num)
{
    var monthList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    return monthList[num-1];
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
    this.part_of_day = part_of_day;
    this.marker = null;
    this.passengers = passengers;
    this.contact = contact;
    this.key = key;
    this.circle = None;
}
//Class that stores information about the college

function College(name, address, lat, lng)
{
this.name = name;
this.address = address;
this.lat= lat;
this.lng= lng;
}

// Class that stores information for a location
function Location(title, latitude, longitude)
{
    this.title = title;
    this.latitude = latitude;
    this.longitude = longitude;
}

// Create a dropdown list of months with this month selected.
function getMonthOptions() {
    var today = new Date();
    var monthList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    res = ""
    for (i=0; i< 12; i++) {
	res += '<option value="'+(i+1)+'" ';
	if (today.getMonth() == i) {
	    res += 'selected="true" ';
	}
	res += '>'+monthList[i]+'</option>\n';
    }
    return res;
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
function changeDates()
{
    //overlays.push(marker);
    //map.addOverlay(marker);
    // Change the data from pull-downs to accurate dates
    /*var today = new Date();
    var yr = today.getFullYear() - 1;
    iyear = iyear + yr;
    fyear = fyear + yr;
    iday = iday + 1;
    fday = fday + 1;
   */

    $begin = $("#begindate").datepicker("getDate");
    $end = $("#enddate").datepicker("getDate");
    fDate = new Date($begin.getFullYear(),$begin.getMonth(),$begin.getDate());
    iDate = new Date($end.getFullYear(),$end.getMonth(),$end.getDate());
    console.log
    
    var y
    for(y in rides)
    {
        var r;
        for (r in rides)
          {
            if (rides[r].ToD <= iDate || rides[r].ToD >= fDate)
              {
                rides[r].marker.setMap(null);
              }
          }
        if (rides[y].ToD >= iDate && rides[y].ToD <= fDate)
        {
            rides[y].marker.setMap(map);
            overlays.push(rides[y].marker);                                           
            //map.addOverlay(rides[y].marker);
        }
    }
    /*var z
    for(z in events)
    {
        var e;
        for (e in events)
          {
            if (events[e].ToD <= iDate || events[e].ToD >= fDate)
              {
                events[e].marker.setMap(null);
              }
          }
        if (events[z].ToD >= iDate && events[z].ToD <= fDate)
        {
            events[z].marker.setMap(map);
            overlays.push(events[z].marker);                                           
            //map.addOverlay(rides[y].marker);
        }
    }*/
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
            //map.removeOverlay(rides[rideNum].marker);
            rides[rideNum].marker.setmap(null);
            rides[rideNum].marker=null;
            var marker = addRideToMap(rides[rideNum], rideNum);
    
            windowOpen(marker.getPosition(),"You have been added<br />to this ride!");
            //marker.openInfoWindowHtml("You have been added<br />to this ride!");                                     
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

function windowOpen(position1,content1)
{
    var window = new google.maps.InfoWindow({position:position1, content:content1});
    google.maps.event.addListener(window,"closeclick",function(){
             clickListener = google.maps.event.addListener(map, "click", getAddress);
             });
    google.maps.event.removeListener(clickListener);
    if (windows.length !=0)
      {
         windows.pop().close();
         windows.push(window);
         window.open(map);
         
      }
    else
      {
        windows.push(window);
        window.open(map);
        
      }
    
}

function putListener()
{
   clickListener = google.maps.event.addListener(map, "click", getAddress);
}

rad = function(x) {return x*Math.PI/180;}

distHaversine = function(p1, p2) {
    var R = 6371;
    var dLat  = rad(p2.lat() - p1.lat());
    var dLong = rad(p2.lng() - p1.lng());

    var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(rad(p1.lat())) * Math.cos(rad(p2.lat())) * Math.sin(dLong/2) * Math.sin(dLong/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    var d = R * c;

    return d.toFixed(3);
}

function getRidesForConnection() {
	var drivernum = document.getElementById("idnum").value;
	var driverRides = new Array(); //rides with driver
	var ndRides= new Array(); //no Drive rides
	var inList = new Array();  //InList keeps track of any rides we have allready found to be a possible connection. Otherwise, we end up using that ride a bunch as we iterate though the route. 
           var connectRides = new Array(); //rides 
    
	for (var i=0;i<rides.length; i++){  //get driver rides
	    if (rides[i].driver == drivernum){
	        driverRides.push(rides[i]);
	    }
	    if (rides[i].driver == "needs driver"){ //get rides with no driver
	       ndRides.push(rides[i]);
	    }
	}

            for (var driveIndex=0;driveIndex<driverRides.length;driveIndex++) { //k = driveIndex
                var dRide = driverRides[driveIndex];
                var request = {  
                    origin:new google.maps.LatLng(mycollege.lat, mycollege.lng),
                    destination:new google.maps.LatLng(dRide.destination_lat,dRide.destination_long),
                    travelMode: google.maps.TravelMode.DRIVING
                };

                directionsService.route(request, function(result, status) {
                    if (status == google.maps.DirectionsStatus.OK) {
                        var pointsArray = result.routes[0].overview_path;  //get an array of points on the path form our origin to destination
                        for (var pointsIndex=0;pointsIndex<pointsArray.length; pointsIndex++){  //iterate through the projected path to see if any applicable rides are close to our user's offered rides.
                            for (var noDIndex=0;noDIndex<ndRides.length;noDIndex++){  

                                if (ndRides[noDIndex].event== null && ndRides[noDIndex].num_passengers>0 && drivernum != ndRides[noDIndex].driver && inList.indexOf(ndRides[noDIndex].key)==-1 && ndRides[noDIndex].num_passengers<= (dRide.max_passengers-dRide.num_passengers) &&(dRide.destination_title ==ndRides[noDIndex].destination_title || dRide.start_point_title ==ndRides[noDIndex].start_point_title)){
                                    var distance = distHaversine(pointsArray[pointsIndex],new google.maps.LatLng(ndRides[noDIndex].destination_lat,ndRides[noDIndex].destination_long));
                                    if (distance <20){ //distance is in miles, adjust for closer connections
        								
        								var infowindowtext = "";
        								infowindowtext = '<p>There is a ride request with a destination very near to your projected path. Would you be willing to drop these passengers off along the way?</p>';
        								infowindowtext += '<form name="connectForm" action="/movepass" method="post">';
        								infowindowtext += '<table border="-1" id="connectTable">';
        								infowindowtext += '<tr>';
        								infowindowtext +=    '<th>Passenger Number</th>';
        								infowindowtext +=    '<th>Your Destination</th>';
        								infowindowtext +=    '<th>Their Destination</th>';
        								infowindowtext +=    '<th>Date</th>';
        								infowindowtext +=    '<th>Accept Passengers</th>';
        								infowindowtext += '<tr>';
        								infowindowtext +=    '<th>'+ndRides[noDIndex].num_passengers+'</th>';
        								infowindowtext +=    '<th>'+dRide.destination_title+'</th>';
        								infowindowtext +=    '<th>'+ndRides[noDIndex].destination_title+'</th>';
        								infowindowtext +=    '<th>'+ndRides[noDIndex].ToD+'</th>';
        								infowindowtext +=    '<th><input type="radio" name="keys" value='+ndRides[noDIndex].key+"|"+dRide.key+' /></th>';
        								infowindowtext += '</table>';
        								infowindowtext +='<input type="submit" value="Submit">';
        								infowindowtext +='</form>';

                                                                                        //places connection marker between passenger ride and driver ride.
                                                                                        console.log(infowindowtext)
        								var midLat = (ndRides[noDIndex].destination_lat + dRide.destination_lat)/2
                                                                                        var midLong = (ndRides[noDIndex].destination_long + dRide.destination_long)/2
        								var cmarker = new google.maps.Marker({position:new google.maps.LatLng(midLat, midLong)});
                                                                                        console.log(cmarker)

        						                      cmarker.setOptions(icons.con);
        						                      cmarker.setMap(map);

        						                      var connectListener = google.maps.event.addListener(cmarker, "click", (function(midLat, midLong, infowindowtext){  //This function inside function thing for the listener is due to scope, look up google maps event closure for more. 

        									   // From function() to function(latlng)
                                                                                                      return function()
        									   {
        									       if (cmarker.getPosition()) {

        						                                   windowOpen(new google.maps.LatLng(midLat, midLong),infowindowtext);

        									       }
        									   };})(midLat, midLong,infowindowtext))
        						                      mc.addMarker(cmarker);
                                                                                        inList.push(ndRides[noDIndex].key);
                                                                                        console.log(inList)
                                    }
                                }

                            }

                        }

                    }

                });
            }
            console.log(connectRides)
        }
function selectAddress(DooPu,rideNum,openableBoole) {

	google.maps.event.addListener(map, 'click', function(event)
		       {
			   if (event!=null) 
			   { 
			       geocoder.geocode({latLng:event.latLng}, function(results,status){
							 if (!status || status != google.maps.GeocoderStatus.OK) 
							 {
							     alert("Status: " + status);
							 }
							 else
							 {
							     var point = results[0].geometry.location;
							     var doOrPu = DooPu; // drop_off = 0, pick_up
                                                            if (openableBoole ==true)
                                                              {
                                                            windowOpen(point,getPopupWindowMessage2(rideNum, doOrPu, 
														  point.lat(), 
														  point.lng(), results[0].formatted_address));
                                                               }
                                                             else
                                                               {
                                                                openableBoole = true;
                					        }
							 }
						     });
			   }
		       });
}

function getParameterByName(name) {

	  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
	  var regexS = "[\\?&]" + name + "=([^&#]*)";
	  var regex = new RegExp(regexS);
	  var results = regex.exec(window.location.search);
	  if(results == null)
		return "";
	  else
		return decodeURIComponent(results[1].replace(/\+/g, " "));
		
}
