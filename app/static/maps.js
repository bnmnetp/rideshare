var College = augment(Object, function () {
	this.constructor = function (name, address, lat, long) {
		this.name = name;
		this.address = address;
		this.lat = lat;
		this.long = long;
	}
})

var community = new College("Luther College", "700 College Drive Decorah,IA", 43.313059, -91.799501);

var Map = augment(Object, function () {
	this.constructor = function () {
		// set coordinates for your community here:
		this.location = {
			lat: 43.313059,
			lng: -91.799501
		};
		this.rides = {};
		this.overlays = [];
		this.windows = [];
		this.events = {};
		this.icons = {};
		this.cluster_click = false;
		this.map;
		this.geocoder;
		this.address;
		this.click_listener;
		this.cluster;
		this.direction_service;
		this.direction_display;

		this.state = 'select_location';
		this.current_ride = {};
		this.current_event = {};

		this.marker_current = {};

		this.create_new_marker = true;

		var d = new Date();

		var req_events = $.ajax({
			type: 'POST',
			url: '/events',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify({
				circle: getParameterByName('circle')
			})
		});
		req_events.done(function (data) {
		});
		req_events.fail(function (message, status) {

		});

		var req_rides = $.ajax({
			type: 'POST',
			url: '/rides',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify({
				circle: getParameterByName('circle')
			})
		});
		req_rides.done(function (data) {
			var ride_layout = document.querySelector('#ride_template')
			var template = Handlebars.compile(ride_layout.innerHTML)
			var html = template({
				rides: data
			})
			console.log(ride_layout.innerHTML)
			console.log(data)
			document.querySelector('#table').insertAdjacentHTML(
				'beforeend',
				html
			)
		});
		req_rides.fail(function (message, status) {

		});

		this.create_markers();

		var ride_send_btn = document.querySelector('[data-send="ride"]');
		ride_send_btn.addEventListener('click', this.send_ride.bind(this));

		var passenger_send_form = document.querySelector('[data-send="passenger"]');
		passenger_send_form.addEventListener('submit', this.send_passenger.bind(this));

		var event_form = document.querySelector('[data-send="event"]');
		event_form.addEventListener('submit', this.send_event.bind(this));

		this.search_form = document.querySelector('#search_form');
		console.log(this.search_form)
		this.search_form.addEventListener('submit', function (e) {
			console.log('Test #1')
			e.preventDefault();
			var address = this.search_form.address.value;
			this.geocoder.geocode({
				address: address
			}, this.disp_address.bind(this));
		}.bind(this));
	}

	this.set_flow = function (flow) {
		this.flow = flow;
	}

	// Creates map markers and stores them in this.icons
	this.create_markers = function () {
		this.icons.event = {
			url: 'static/stargate.png',
			anchor: new google.maps.Point(20, 20),
			size: new google.maps.Size(30, 40)
		};
		this.icons.marker_shadow = {
			url: 'http://labs.google.com/ridefinder/images/mm_20_shadow.png',
			size: new google.maps.Size(22, 20)
		};
		this.icons.car_success = {
			url: 'static/carGreen.png',
			anchor: new google.maps.Point(20, 20),
			size: new google.maps.Size(30, 40)
		};
		this.icons.car_error = {
			url: 'static/carRed.png',
			anchor: new google.maps.Point(20, 20),
			size: new google.maps.Size(30, 40)
		};
		this.icons.person = {
			url: 'static/person.png',
			anchor: new google.maps.Point(20, 20),
			size: new google.maps.Size(30, 40)
		};
		this.icons.person_shadow = {
			url: 'static/person.png',
			anchor: new google.maps.Point(20, 20),
			size: new google.maps.Size(30, 40)
		};
		this.icons.plus = {
			url: 'static/cross.png',
			anchor: new google.maps.Point(20, 20),
			size: new google.maps.Size(30, 40)
		};

	    this.map = new google.maps.Map(document.querySelector('#map_canvas'), {
	        draggableCursor: 'crosshair',
	        center: new google.maps.LatLng(this.location.lat, this.location.lng),
	        mapTypeId: google.maps.MapTypeId.ROADMAP,
	        zoom: 10
	    })

	    google.maps.event.addListener(this.map, 'click', this.get_address.bind(this))

		this.marker = new google.maps.Marker({
			position: this.location,
			map: this.map
		})
		this.direction_service = new google.maps.DirectionsService();
		this.direction_display = new google.maps.DirectionsRenderer({preserveViewport:false});

		this.cluster = new MarkerClusterer(this.map);
		this.cluster.setGridSize(30);
		google.maps.event.addListener(this.cluster, "clusterclick", function (cluster) {
			this.cluster_click = true;
		});

		this.geocoder = new google.maps.Geocoder();
		//google.maps.event.addListener()
	}

	this.add_ride = function (ride) {
		var marker_position;
		var marker = this.rides[ride.id].marker;
		if (ride.destination_title == community.name) {
			marker_position = new google.maps.LatLng(ride.destination_lat, ride.destination_long)
		} else {
			marker_position = new google.maps.LatLng(ride.destination_lat, ride.destination_long)
		}
		marker = new google.maps.Marker({
			position: new google.maps.LatLng(ride.start_point_lat, ride.start_point_long),
			icon: this.icons.person
		});
		google.maps.event.addListener(marker, 'click', function () {
			if (marker.getPosition()) {
				windowOpen(
					marker.getPosition(),
					addDriverPopup(
						ride,
						marker.getPosition().lat(),
						marker.getPosition().lng()
					)
				)
			}
		});
		ride.marker = marker;
		marker.setMap(this.map);
		overlays.push(marker);
		this.cluster.addMarker(marker);
		return ride.marker;
	} 

	this.add_event = function (event) {
		var marker = this.events[event.id].marker;
		marker = new google.maps.Marker({
			position: new google.maps.LatLng(event.lat,event.lng),
			icon: this.icons.event
		})
		marker.setMap(this.map);
		overlays.push(marker);
		google.maps.event.addListener(marker, 'click', function () {
			if (marker.getPosition()) {
				var d = new Date();
				var rides = {};
				var req_rides = $.ajax({
					type: 'GET',
					url: '/getrides',
					data: {
						circle: getParameterByName('circle'),
						event: event.id,
						after: d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate()
					}
				});
				req_rides.done(function (res) {
					rides = JSON.parse(res);
					for (var i = 0; i < rides.length; i++) {
						ride = rides[i];
						ride.spots_available = ride.max_passengers - ride.num_passengers;
					}
					var source = document.querySelector('#ride-template').innerHTML;
					var template = Handlebars.compile(source);
					var html = template(rides);
				});
				req_rides.fail(function (res, status) {

				});

			}
		});


	}

	this.get_address = function (e) {
		if (e != null) {
			this.latLng = e.latLng;
			this.geocoder.geocode({
				latLng: this.latLng
			}, this.disp_address.bind(this));
		}
	}

	this.disp_address = function (location) {
		var source = document.querySelector('#location-template').innerHTML;
		var template = Handlebars.compile(source);
		var html = template({
			location: 'Test Location'
		});
		console.log(location)

		var point = location[0].geometry.location;
		this.marker_current.lat = point.k;
		this.marker_current.lng = point.A;
		this.marker_current.address = location[0].formatted_address;
		this.set_window(
			point,
			html
		)

		if (this.state == 'select_location') {
			flow.change_slide('trip_type');
		}
		if (this.state == 'location_2') {
			var location_2 = document.querySelector('[data-ride="loc_2"]');
			var location_btn = document.querySelector('[data-ride="loc_btn"]');
			location_2.textContent = this.marker_current.address;
			location_btn.removeAttribute('disabled');
		}
	}

	this.set_window = function (location, content) {
		if (this.create_new_marker) {
			var LatLng = new google.maps.LatLng(location.k, location.A);
			var dialog = new google.maps.InfoWindow({
				position: LatLng,
				content: content
			});
			var marker = new google.maps.Marker({
				position: LatLng,
				map: this.map,
			})
			console.log(dialog);
			google.maps.event.addListener(
				dialog,
				'closeclick',
				function () {
					this.click_listener = google.maps.event.addListener(
						map,
						'click',
						this.get_address
					)
				}.bind(this)
			);
			google.maps.event.removeListener(this.click_listener);
			this.create_new_marker = false;
		} else {
			console.log('Cannot create new marker right now');
		}
	}

	this.special_action = function (route, btn) {
		// Set location #1 for data-slide=3, data-option=ride
		if (route == 'location_1') {
			if (btn.dataset.ride == 'driver') {
				this.current_ride.driver = true;
			} else if (btn.dataset.ride == 'passenger') {
				this.current_ride.driver = false;
			}
			
			var location = document.querySelector('[data-ride="loc_1"]');
			location.textContent = this.marker_current.address;
			flow.change_slide(route);
		} else if (route == 'location_2') {
			// Set location_type when selecting location #2
			var location_type_form = document.querySelector('[data-ride="loc_1_type"]');
			var location_type_disp = document.querySelector('[data-ride="loc_2_type"]');
			var text;
			this.marker_current.location_type = location_type_form.value;
			if (location_type_form.value != 'finish') {
				this.current_ride.destination = this.marker_current;
				text = 'destination';
			} else {
				this.current_ride.origin = this.marker_current;
				text = 'starting point';
			}
			location_type_disp.textContent = text;
			this.create_new_marker = true;
			flow.change_slide(route);
		} else if (route == 'details') {
			if (this.marker_current.location_type != 'finish') {
				this.current_ride.origin = this.marker_current;
				
			} else {
				this.current_ride.destination = this.marker_current;
			}
			if (this.current_ride.driver == true) {
				flow.change_slide('driver_details')
			} else {
				flow.change_slide('passenger_details')
			}
		} else {
			flow.change_slide(route);
		}
	}

	this.send_ride = function (e) {
		e.preventDefault();
		var form = document.querySelector('#ride_form');
		this.current_ride.max_passengers = form.max_passengers.value;
		this.current_ride.date = form.date.value;
		this.current_ride.time = form.time.value;
		this.current_ride.details = form.details.value;
		var req_rides = $.ajax({
			type: 'POST',
			url: '/newride',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify(this.current_ride)
		});
		req_rides.done(function (message) {
			this.flow.change_slide('select_location');
			this.flow.alert({
				type: 'success',
				strong: 'You created a new ride!',
				message: 'We sent you a confirmation email.'
			});
		}.bind(this));
		req_rides.fail(function (message, status) {
			this.flow.change_slide('select_location');
			this.flow.alert({
				type: 'danger',
				strong: 'Sorry!',
				message: 'The ride was not created. Please try again.'
			});
		}.bind(this));
	}

	this.send_passenger = function (e) {
		e.preventDefault();
		var form = document.querySelector('[data-send="passenger"]')
		this.current_ride.date = form.date.value;
		this.current_ride.time = form.time.value;
		this.current_ride.details = form.details.value;
		var req_rides = $.ajax({
			type: 'POST',
			url: '/newride',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify(this.current_ride)
		});
		req_rides.done(function (message) {
			this.flow.change_slide('select_location');
			this.flow.alert({
				type: 'success',
				strong: 'You asked for a ride!',
				message: 'We sent you a confirmation email.'
			});
		}.bind(this));
		req_rides.fail(function (message, status) {
			this.flow.change_slide('select_location');
			this.flow.alert({
				type: 'danger',
				strong: 'Sorry!',
				message: 'The ride was not created. Please try again.'
			});
		}.bind(this));
	}

	this.send_event = function (e) {
		e.preventDefault();
		var form = document.querySelector('[data-send="event"]')
		var event = {};
		event.name = form.name.value;
		event.address = this.marker_current.address;
		event.lat = this.marker_current.lat;
		event.lng = this.marker_current.lng;
		event.date = form.date.value;
		event.time = form.time.value;
		event.details = form.details.value;
		var req_event = $.ajax({
			type: 'POST',
			url: '/newevent',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify(event)
		});
		req_event.done(function (message) {
			this.flow.change_slide('select_location');
			this.flow.alert({
				type: 'success',
				strong: 'Event created!',
				message: 'We sent you a confirmation email.'
			});
		}.bind(this));
		req_event.fail(function (message, status) {
			this.flow.change_slide('select_location');
			this.flow.alert({
				type: 'danger',
				strong: 'Sorry!',
				message: 'The event was not created. Please try again.'
			});
		}.bind(this));
	}
});

var Ride = augment(Object, function () {
	this.constructor = function (obj) {

	}

	this.send = function () {

	}
})

var Location = augment(Object, function () {
	this.constructor = function (title, lat, long) {
		this.title = title;
		this.lat = lat;
		this.long = long;
	}
})

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

var DriverController = augment(Object, function () {
	this.constructor = function () {

	}

	this.set_location = function (id) {

	}
})
