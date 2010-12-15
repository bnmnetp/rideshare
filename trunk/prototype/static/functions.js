// initalize rides array then plot them.
// The rides array is declared in index.html

var rides = new Array();
var map;
var geocoder;
var address2;

function initialize(mess) 
{
    if (GBrowserIsCompatible()) 
    {
	var request = new XMLHttpRequest();
	var today = new Date();
	request.open("GET","/getrides?after="+today.getFullYear()+"-"+(today.getMonth()+1)+"-"+today.getDate(),false);
	request.send(null);
	if (request.status == 200) {
	    // loop over all
	    rides = eval(request.responseText);
	    for (r in rides) {
		var tod = rides[r].ToD
		rides[r].ToD = new Date(tod.substring(0,4),tod.substring(5,7)-1,tod.substring(8,10));
	    }
	}




	// Begin creation of Icons for Rides
	var greenIcon = new GIcon();
	greenIcon.image = "http://www.google.com/mapfiles/dd-start.png";
	//      greenIcon.image = "http://www.google.com/intl/en_us/mapfiles/ms/micons/green-dot.png";
	greenIcon.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png";
	greenIcon.iconSize = new GSize(12, 20); // 12, 20
	greenIcon.shadowSize = new GSize(22, 20);
	greenIcon.iconAnchor = new GPoint(6, 20); // 6, 20
	greenIcon.infoWindowAnchor = new GPoint(10, 1);

	gmarkerOptions = { icon:greenIcon };

	var redIcon = new GIcon();
	redIcon.image = "http://www.google.com/mapfiles/dd-end.png";
	redIcon.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png";
	redIcon.iconSize = new GSize(12, 20);
	redIcon.shadowSize = new GSize(22, 20);
	redIcon.iconAnchor = new GPoint(6, 20);
	redIcon.infoWindowAnchor = new GPoint(5, 1);

	rmarkerOptions = { icon:redIcon };

	// Sample custom marker code created with Google Map Custom Marker Maker
	// http://www.powerhut.co.uk/googlemaps/custom_markers.php
	
	var myIcon = new GIcon();
	myIcon.image = 'static/image.png';
	myIcon.shadow = 'static/shadow.png';
	myIcon.iconSize = new GSize(20,17);
	myIcon.shadowSize = new GSize(29,17);
	myIcon.iconAnchor = new GPoint(10,17);
	myIcon.infoWindowAnchor = new GPoint(10,0);
	myIcon.printImage = 'static/printImage.gif';
	myIcon.mozPrintImage = 'static/mozPrintImage.gif';
	myIcon.printShadow = 'static/printShadow.gif';
	myIcon.transparent = 'static/transparent.png';
	myIcon.imageMap = [19,0,19,1,19,2,18,3,18,4,17,5,16,6,19,7,19,8,19,9,19,10,16,11,19,12,13,13,13,14,15,15,19,16,8,16,7,15,6,14,6,13,5,12,5,11,5,10,4,9,4,8,4,7,3,6,2,5,1,4,1,3,0,2,0,1,0,0];

	bmarkerOptions = { icon:myIcon };

	var blueIcon = new GIcon(G_DEFAULT_ICON);
	blueIcon.image = "http://www.google.com/intl/en_us/mapfiles/ms/micons/blue-dot.png";
	blueIcon.iconSize = new GSize(20, 17);
	blueIcon.iconAnchor = new GPoint(10,17);
	blueIcon.shadowSize = new GSize(29,16)
	blueIcon.infoWindowAnchor = new GPoint(10,0);
	markerOptions = { icon:myIcon };
	var marker = new GMarker(new GLatLng(43.313059,-91.799501), markerOptions);

        reqMarkerOptions = {icon:blueIcon}

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

    makeRideTable();
    if (mess) {
	alert(mess);
    }
}



function makeRideTable() {
    var table = document.getElementById("rideTable");

    for(var i = table.rows.length; i > 1;i--) {
	table.deleteRow(i -1);
    }
    var r;
    for (r in rides)
    {
	var row = table.insertRow(table.rows.length);
	var c0 = row.insertCell(0);
	c0.innerHTML = rides[r].driver;
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

// Returns the Inital form used in the ride creation process...
// o From Luther to
//    address.....
// o To Luther
//
function getNewRidePopupHTML(lat, lng, address3)
{
    var full = "<b>Create a New Ride</b>";

    full += "<form><p style=\"text-align: left;\">";

    full += "<input onclick=\"newRidePopupHTMLPart2("+lat+", "+lng+", '" 
              + address3 +"', false);\" type=\"radio\" name=\"rideType\" value=\"0\" id=\"rideType\""+"/>From Luther to <br />";

    full += address3 + "<br />";

    full += "<input onclick=\"newRidePopupHTMLPart2("+lat+", "+lng+", '" 
              + address3 + "', true);\" type=\"radio\" name=\"rideType\" value=\"1\" id=\"rideType\"/>To Luther</p></form>";

    return full;
}


function newRidePopupHTMLPart2(lat, lng, address4, to, contact)
{
    map.closeInfoWindow();
    var htmlText = getNewRideIsDriverHTML(lat, lng, address4, to, contact);
    map.openInfoWindowHtml(new GLatLng(lat, lng), htmlText);
}

// Returns the html for Step 2 in Ride Creation
//
// o I can drive
// o I am looking for a ride
//
// To
//  address
// From
//  address
function getNewRideIsDriverHTML(lat, lng, address, to, contact)
{
    var full = "<b>Create a New Ride</b>";

    full += "<form><p>"
    full += '<input onclick="newRidePopupHTMLPart2b('+lat+","+lng+", '"
            + address+"',"+to+", true);"+'" type="radio" name="driver" value="1" /> I will drive <br />';
    full += '<input onclick="newRidePopupHTMLPart2b('+lat+","+lng+", '"
            + address+"',"+to+", false);"+'" type="radio" name="driver" value="0" /> I am looking for a ride <br />';
    full += "</form></p>";
    full += "From:<br />";
    if (to) {
	full += address + "<br />";
    } else {
	full += "Luther College <br />";
    }
    full += "To: <br />";
    if (to) {
	full += "Luther College";
    } else {
	full += address;
    }
    return full;
}

function newRidePopupHTMLPart2b(lat, lng, address4, to, driver)
{
    map.closeInfoWindow();
    var htmlText = getNewRidePopupHTML2(lat, lng, address4, to, driver);
    map.openInfoWindowHtml(new GLatLng(lat, lng), htmlText);
}

//
//
// Generate the HTML for the final popup in creating a ride
//
//
// TODO:  there is no need for form and onsubmit here it should just be a button with the function call, since this form will NEVER 
//        actually get submitted.
function getNewRidePopupHTML2(lat, lng, address5, to, isDriver, contact)
{
    contact = (typeof contact == 'undefined') ? '563-555-1212': contact; // If contact is not defined, then let it be 563-555-1212
    var line5="<b>Create a new Ride</b> <form onsubmit=\"verifyNewRidePopup("+lat+", "+lng+", '"+address5+"', "+isDriver+"); return false;\" id=\"newride\"><div id=\"textToAll\">Please ensure that your address is as specific as possible<br />(<i>37</i> Main Street, not <i>30-50</i> Main Street)<br />From <input type=\"text\" id=\"textFrom\" name='textFrom' size=\"50\"";
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
    line6 = line6 + "><br /></div>";
    var line7="<div id=\"maxpdiv\">";
    if (isDriver) {
	var line8="Maximum number of passengers: <input type=\"text\" name=\"maxp\" id=\"maxp\" maxLength=\"3\" size=\"3\" value=\"2\"><br />";
    } else {
	line8 = "";
    }
    var line9="How can you be contacted by phone? <input type=\"text\" name=\"number\" id=\"number\" maxlength=\"12\" size=\"10\" value=\""+contact+"\" onclick=\"this.value=''\"></div>";
    var line10="<div id=\"toddiv\">";
    var line11="Time of Departure: <select name=\"earlylate\" id=\"earlylate\"><option value=\"0\" selected=\"selected\">Early</option><option value=\"1\">Late</option></select>";
    var line12="<select name=\"partofday\" id=\"partofday\"><option value=\"0\" selected=\"selected\">Morning</option><option value=\"1\">Afternoon</option><option value=\"2\">Evening</option></select>";
    var line13="<select name=\"month\" id='month' onChange=\"changeDays(document.getElementById('day'), this); return false;\">" + getMonthOptions() + "</select>";
    var line14="<select name=\"day\" id=\"day\">";
    var today = (new Date()).getDate();
    
    for (var i = 1; i < 32; i++)
    {
        line14 += "<option value=\""+i+"\" ";
	if ( today+2 == i ) {
	    line14 += "selected=\"selected\"";
        }
	line14 += ">"+ i + "</option>";
    }
    line14 = line14 + "</select>";
    var line15="<select name=\"year\" id='year'>";
    var yr = (new Date()).getFullYear();
    var line16 = "";
    for (var i = yr-1; i < yr+4; i++)
    {
        line16 +="<option value=\""+i+"\"";
        if (i == yr)
            line16 += "selected=\"selected\"";
        {
        }
        line16 += ">"+i+"</option>";
    }
    line16 = line16 + "</select></div>";
    line16 = line16 + "Comments: <input type=\"text\" id=\"ridecomment\" name=\"ridecomment\" size=\"50\">"
    var line17="<div id=\"buttons\"><input type=\"submit\" id=\"submit\" name=\"submit\" value=\"Okay\"><input type=\"button\" id=\"cancel\" name='cancel' value='Cancel' onclick='map.closeInfoWindow();'></div><input type=\"hidden\" name=\"driver\" value=\""+isDriver+"\">   </form>";
    var full = line5+line6+line7+line8+line9+line10+line11+line12+line13+line14+line15+line16+line17;
    return full;
}


// Verify that all new ride information is valid
//
function verifyNewRidePopup(lat, lng, address6, isDriver)
{
    var from = document.getElementById("textFrom").value;
    var to = document.getElementById("textTo").value;
    var earlylate = document.getElementById("earlylate").value;
    var partofday = document.getElementById("partofday").value;
    var month = document.getElementById("month").value;
    var day = document.getElementById("day").value;
    var year = document.getElementById("year").value;
    var comment = document.getElementById("ridecomment").value;

    // Check for valid number
    var number = document.getElementById("number").value;
    if (isDriver) {
	var maxp = document.getElementById("maxp").value;
    } else{
	var maxp = "3";
    }
    var goodContact = false;

    var currentTime = new Date();
    var rideDate = new Date(year, month, day);
    goodContact = validatePhoneNumber(number);
    var badmaxp = false;

    if (/[^0-9-]+/.test(maxp)) {
	badmaxp = true;
    }
    // Ensure valid number is supplied
    if (! goodContact)
    {
        alert("Please supply a valid ten-digit contact number.");
    }
    // Ensure an original number is supplied
    else if (number == '563-555-1212')
    {
        alert("Please supply an original contact number.");
    }
    // Ensure to and from are filled
    else if (to == '')
    {
        alert("Please supply a destination.");
    }
    else if (from == '')
    {
        alert("Please supply a start point.");
    }
    // Ensure maxp is filled
    else if (isDriver && (maxp == '' || badmaxp))
    {
        alert("Please supply a valid maximum number of passengers.");
    }
    // test date.. make sure it is in the future
    else if (rideDate < currentTime) {
	alert("The date for a ride must be in the future"+rideDate);
    }
    // Bring up confirm window
    else
    {
        if (number.length == 10) {
            number = number.slice(0, 3) + '-' + number.slice(3, 6) + '-' + number.slice(6);
        }
        map.closeInfoWindow();
        var htmlText = getNewRidePopupHTML3(lat, lng, from, to, maxp, number, earlylate, partofday, month, day, year,isDriver,comment);
        map.openInfoWindowHtml(new GLatLng(lat, lng), htmlText);
    }  
}

function getNewRidePopupHTML3(lat, lng, from, to, maxp, number, earlylate, partofday, month, day, year,isDriver,comment)
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
    var vals = {};
    vals['lat'] = lat;
    vals['lng'] = lng;
    vals['from'] = from;
    vals['to'] = to;
    vals['maxp'] = maxp;
    vals['contact'] = number;
    vals['earlylate'] = earlylate;
    vals['partofday'] = partofday;
    vals['month'] = month;
    vals['day'] = day;
    vals['year'] = year;
    vals['isDriver'] = isDriver;
    vals['comment'] = comment;
    if (from == "Luther College, Decorah, Iowa") {
	vals['toLuther'] = false;
    } else {
	vals['toLuther'] = true;
    }

//    var funcall = 'saveRide({lat},{lng},{toLuther},"{from}","{to}",{maxp},{earlylate},{partofday},"{contact}",{month},{day},{year},{isDriver},"{comment}");';

//    var t = jsontemplate.Template(funcall);
//    funcall = t.expand(vals);
    var funcall = 'saveRide('+JSON.stringify(vals)+')';
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
    full += "<form>";
    full += "<input type='button' id='submit' name='submit' value='Submit' onclick='" + funcall + "'/>";
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
    full +="', "+checked.toString()+", "+number+", "+isDriver+");\"/></form>";
    return full;
}

function  saveRide(vals) {

    var request = new XMLHttpRequest();

    var reqStr = '/newride?';


    for (var prop in vals) {
	reqStr += prop + "=" + vals[prop] + "&";
    }

    request.open("GET",reqStr,false);
    request.send(null);
    if (request.status == 200) {
	initialize();
    } else {
	alert("An error occurred, check your responses and try again.");
    }

}


// Adds a popup to the GoogleMap that fits 'ride'
function addRideToMap(ride, rideNum)
{

    if (ride.driver == "needs driver") {
	var tooltext = 'needs driver';
	reqMarkerOptions['title'] = tooltext;
	if (ride.destination_title == "Luther College, Decorah, IA") {
            var amarker = new GMarker(new GLatLng(ride.start_point_lat, ride.start_point_long), reqMarkerOptions);
	} else {
            var amarker = new GMarker(new GLatLng(ride.destination_lat, ride.destination_long), reqMarkerOptions);
	}
        GEvent.addListener(amarker, "click", function(latlng)
			   {
			       if (latlng) {
				   amarker.openInfoWindowHtml(addDriverPopup(ride, rideNum, latlng.lat(), latlng.lng()));
			       }
			   });
        ride.marker = amarker;
        map.addOverlay(amarker);
    } else if (ride.destination_title == "Luther College, Decorah, IA")
    {
        var tooltext = '';
        tooltext += ride.ToD;
        gmarkerOptions['title'] = tooltext;
        var amarker = new GMarker(new GLatLng(ride.start_point_lat, ride.start_point_long), gmarkerOptions);
        GEvent.addListener(amarker, "click", function(latlng)
			   // From function() to function(latlng)
			   {
			       if (latlng) {
				   amarker.openInfoWindowHtml(getPopupWindowMessage(ride, rideNum, latlng.lat(), latlng.lng()));
			       }
			   });
        ride.marker = amarker;
        map.addOverlay(amarker);
    }
    else if (ride.start_point_title == "Luther College, Decorah, IA")
    {
        var tooltext = '';
        tooltext += ride.ToD;
        rmarkerOptions['title'] = tooltext;
        var bmarker = new GMarker(new GLatLng(ride.destination_lat, ride.destination_long), rmarkerOptions);
        GEvent.addListener(bmarker, "click", function(latlng)
			   // From function() to function(latlng)
			   {
			       if (latlng) {
				   bmarker.openInfoWindowHtml(getPopupWindowMessage(ride, rideNum, latlng.lat(), latlng.lng()));
			       }
			   });
        ride.marker = bmarker;
        map.addOverlay(bmarker);
    }
    return ride.marker;
}

function joinRideByNumber(rideNum) {
    map.removeOverlay(rides[rideNum].marker);
    var marker = addRideToMap(rides[rideNum], rideNum);
    marker.openInfoWindowHtml(getPopupWindowMessage(rides[rideNum], 
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
    if (ride.ToD < new Date(today.getFullYear(), today.getMonth(), today.getDate() + 2))
    {
        disabled = "disabled=\"disabled\"";
        msg = "It is too late to join this ride";
    }
    else if (ride.max_passengers <= ride.num_passengers) {
        disabled = "disabled=\"disabled\"";
    }
    else {
        disabled = "";
    }
    var text1 = ("Driver: "+ride.driver+"<br><i>"+ride.start_point_title+"</i> --> <i>"+ride.destination_title+"</i><br>Date: "+ride.part_of_day+" "+numToTextMonth(ride.ToD.getMonth())+" "+ride.ToD.getDate()+", "+ride.ToD.getFullYear()+"<br>"+msg);
    var drop_off_or_pick_up; // drop_off = 0, pick_up = 1
    if (ride.start_point_title == "Luther College, Decorah, IA") {
        drop_off_or_pick_up = 0;
    }
    else {
        drop_off_or_pick_up = 1;
    }
    text1 += "<br />" + ride.comment + "<br />";

    var text2 = ("<br /><form id=\"addPass\" onsubmit=\"addPassengerPart2('"+ride.key+"', "+drop_off_or_pick_up+", "+lat+", "+lng+", "+rideNum+"); return false;\"><input type=\"submit\" value=\"Join this Ride\""+disabled+"/></form>");
    var result = text1 + text2;
    return result;
}

function addDriverToRideNumber(rideNum) {
    map.removeOverlay(rides[rideNum].marker);
    var marker = addRideToMap(rides[rideNum], rideNum);
    marker.openInfoWindowHtml(addDriverPopup(rides[rideNum], 
						    rideNum, 
						    rides[rideNum].destination_lat,
						    rides[rideNum].destination_long));
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
    map.removeOverlay(ride.marker);
    var marker = addRideToMap(rides[rideNum], rideNum);
    marker.openInfoWindowHtml(t.expand(ride));
}


function closePopup(rideNum) {
    map.removeOverlay(ride.marker);
    var marker = addRideToMap(rides[rideNum], rideNum);
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
    map.closeInfoWindow();
    // remove all listeners
    GEvent.clearListeners(map);
    map.clearOverlays();

    // Create text for popup window
    var infowindowtext = '';
    infowindowtext += 'Would you like to be ';
    if (drop_off_or_pick_up == 1) {
        infowindowtext += 'picked up';
    }
    else {
        infowindowtext += 'dropped off';
    }
    infowindowtext += ' at this location?<br />If not, please click on the map to select a new ';
    if (drop_off_or_pick_up == 1) {
        infowindowtext += 'pick up';
    }
    else {
        infowindowtext += 'drop off';
    }
    infowindowtext += ' point.<br />';
    infowindowtext += "<input type='button' onclick='rides["+rideNum+"].marker.openInfoWindowHtml(getPopupWindowMessage2("+rideNum+", "+drop_off_or_pick_up+", "+lat+", "+lng+", \"\"))' value='Use this location' />";
    infowindowtext += "<input type='button' onclick='initialize();' value='Cancel' />"; //TODO:  something other than init here
    // Keep marker for ride's location (lat, lng)
    var thismarker = rides[rideNum].marker;
    GEvent.addListener(thismarker, "click", function(latlng)
		       // From function() to function(latlng)
		       {
			   if (latlng) {
			       thismarker.openInfoWindowHtml(infowindowtext);
			   }
		       });
    map.addOverlay(thismarker);

    GEvent.addListener(map, 'click', function(overlay, latlng) 
		       {
			   if (latlng != null) 
			   {
			       geocoder.getLocations(latlng, function(response) 
						     {
							 if (!response || response.Status.code != 200) 
							 {
							     alert("Status Code: " + response.Status.code);
							 }
							 else
							 {
							     var place = response.Placemark[0];
							     point = new GLatLng(place.Point.coordinates[1],
										 place.Point.coordinates[0]);
							     var doOrPu = drop_off_or_pick_up; // drop_off = 0, pick_up = 1
							     map.openInfoWindowHtml(point, getPopupWindowMessage2(rideNum, doOrPu, 
														  point.lat(), 
														  point.lng(), place.address));
							 }
						     });
			   }
		       });

    // Popup regarding choice of pickup / dropoff point
    thismarker.openInfoWindowHtml(infowindowtext);
}

function getPopupWindowMessage2(rideNum, doOrPu, lat, lng, address8, contact)
{
    contact = (typeof contact == 'undefined') ? '563-555-1212': contact; // If contact is not defined, then let it be 563-555-1212
    if (address8 == '') {
        if (doOrPu == 0) {
            address8 = rides[rideNum].destination_title;
        }
        else {
            address8 = rides[rideNum].start_point_title;
        }
    }
    var text = "<form onsubmit='addPassengerPart3("+rideNum+", "+lat+", "+lng+", "+doOrPu+"); return false;'>Please ensure that your address is as specific as possible<br />(<i>37</i> Main Street, not <i>30-50</i> Main Street)<br />";
    if (doOrPu == 0) {
        text += "Drop Off At: ";
    }
    else {
        text += "Pick Up At: ";
    }
    text += "<input type='text' id='address' value='"+address8+"' size='30' /><br />";
    text += "Contact: <input type='text' id='contact' maxlength='12' size='10' value='"+contact+"' onclick='this.value=\"\"' /><br />";
    text += "<input type='submit' id='submit' value='Okay' />";
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
	var funcall = 'saveNewPass("'+rides[rideNum].key+'","'+contact+'","'+address+'",'+lat+','+lng+');';

        var text = "<form>";
        text += '<h4>Is the following information correct?</h4>';
        text += 'Address: '+address+'<br />';
        text += 'Contact: '+contact+'<br />';
        text += "<input type='button' id='submit' value='Submit' onclick='"+funcall+"' />";
        text += "<input type='button' id='back' value='Back' onclick='map.openInfoWindowHtml(new GLatLng("+lat+", "+lng+"), getPopupWindowMessage2("+rideNum+", "+doOrPu+", "+lat+", "+lng+", \""+address+"\", \""+contact+"\"));' /></form>";
	alert(text);
        rides[rideNum].marker.openInfoWindow(text);
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
    return monthList[num];
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

// Create a dropdown list of months with this month selected.
function getMonthOptions() {
    var today = new Date();
    var monthList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    res = ""
    for (i=0; i< 12; i++) {
	res += '<option value="'+i+'" ';
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
