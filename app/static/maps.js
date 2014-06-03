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
		this.windows = [];
		this.events = {};
		this.icons = {};
		this.map;
		this.geocoder;

		this.state = 'select_location';
		this.current_ride = {};
		this.current_event = {};

		this.marker_1 = {};
		this.marker_2 = {};

		this.create_new_marker = true;

		this.table_container = document.querySelector('[data-container="tables"]');

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
			var layout = document.querySelector('[data-template="event"]');
			var template = Handlebars.compile(layout.innerHTML);
			var html = template({
				events: data
			})
			this.table_container.insertAdjacentHTML(
				'beforeend',
				html
			)
			this.events = data;
			for (var i = 0; i < this.events.length; i++) {
				this.add_event(i);
			}
		}.bind(this));
		req_events.fail(function (message, status) {

		}.bind(this));

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
			this.rides = data;
			for (var i = 0; i < this.rides.length; i++) {
				this.add_ride(i);
			}
		}.bind(this));
		req_rides.fail(function (message, status) {

		}.bind(this));

		this.create_markers();

		var ride_send_btn = document.querySelector('[data-send="ride"]');
		ride_send_btn.addEventListener('click', this.send_ride.bind(this));

		var passenger_send_form = document.querySelector('[data-send="passenger"]');
		passenger_send_form.addEventListener('submit', this.send_passenger.bind(this));

		var event_form = document.querySelector('[data-send="event"]');
		event_form.addEventListener('submit', this.send_event.bind(this));

		document.body.addEventListener('click', function (e) {
			var target = e.target;
			if (target.dataset.join) {
				this.join_ride.apply(this, [e]);
			}
		}.bind(this));

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

		this.geocoder = new google.maps.Geocoder();
		//google.maps.event.addListener()
	}

	this.add_ride = function (idx) {
		/* Get ride */
		var ride = this.rides[idx];
		/* Set template and compile */
		var layout = document.querySelector('[data-template="popup"]');
		var source = Handlebars.compile(layout.innerHTML)

		/* Create origin marker & info window */
		var origin_html = source({
			primary: 'Starting',
			primary_add: ride.origin_add,
			secondary: 'Ending',
			secondary_add: ride.dest_add,
			id: ride.id
		})
		
		origin_pos = new google.maps.LatLng(
			ride.origin_lat,
			ride.origin_lng
		);
		ride.origin_marker = new google.maps.Marker({
			position: origin_pos,
			icon: this.icons.car_success
		});
		ride.origin_info = new google.maps.InfoWindow({
			position: origin_pos,
			content: origin_html
		});

		google.maps.event.addListener(ride.origin_marker, 'click', function () {
			ride.origin_info.open(this.map, ride.origin_marker)
		}.bind(this));
		ride.origin_marker.setMap(this.map);

		/* Create dest marker & info window */
		var dest_html = source({
			secondary: 'Starting',
			secondary_add: ride.origin_add,
			primary: 'Ending',
			primary_add: ride.dest_add,
			id: ride.id
		})
		dest_pos = new google.maps.LatLng(
			ride.dest_lat,
			ride.dest_lng
		)
		ride.dest_marker = new google.maps.Marker({
			position: dest_pos,
			icon: this.icons.car_error
		})
		ride.dest_info = new google.maps.InfoWindow({
			position: dest_pos,
			content: origin_html
		});

		google.maps.event.addListener(ride.dest_marker, 'click', function () {
			ride.dest_info.open(this.map, ride.dest_marker);
		}.bind(this));
		ride.dest_marker.setMap(this.map);
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
			google.maps.event.addListener(marker, 'click', function () {
				dialog.open(this.map, marker)
			})
			google.maps.event.addListener(
				dialog,
				'closeclick'
			);
			this.create_new_marker = false;
		} else {
			console.log('Cannot create new marker right now');
		}
	}

	this.add_event = function (event) {
		var marker = this.events[event.id].marker;
		marker = new google.maps.Marker({
			position: new google.maps.LatLng(event.lat, event.lng),
			icon: this.icons.event
		})
		marker.setMap(this.map);
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
		this.latLng = e.latLng;
		this.geocoder.geocode({
			latLng: this.latLng
		}, this.disp_address.bind(this));
	}

	this.disp_address = function (location) {
		// var source = document.querySelector('#location-template').innerHTML;
		// var template = Handlebars.compile(source);
		// var html = template({
		// 	location: 'Test Location'
		// });

		var point = location[0].geometry.location;
		this.set_window(point, 'New Marker');

		if (this.state == 'select_location') {
			this.marker_1.lat = point.k;
			this.marker_1.lng = point.A;
			this.marker_1.address = location[0].formatted_address;
			flow.change_slide('trip_type');
		}
		if (this.state == 'location_2') {
			this.marker_2.lat = point.k;
			this.marker_2.lng = point.A;
			this.marker_2.address = location[0].formatted_address;

			var location_2 = document.querySelector('[data-ride="loc_2"]');
			var location_btn = document.querySelector('[data-ride="loc_btn"]');

			location_2.textContent = this.marker_2.address;
			location_btn.removeAttribute('disabled');
		}
	}

	this.special_action = function (route, btn) {
		// Set location #1
		if (route == 'location_1') {
			if (btn.dataset.ride == 'driver') {
				this.current_ride.driver = true;
			} else if (btn.dataset.ride == 'passenger') {
				this.current_ride.driver = false;
			}
			
			var location = document.querySelector('[data-ride="loc_1"]');
			location.textContent = this.marker_1.address;
			flow.change_slide(route);
		} else if (route == 'location_2') {
			// Set location_type when selecting location #2
			var location_type_form = document.querySelector('[data-ride="loc_1_type"]');
			var location_type_disp = document.querySelector('[data-ride="loc_2_type"]');
			var text;
			this.marker_1.location_type = location_type_form.value;
			console.log(location_type_form.value)
			if (this.marker_1.location_type == 'destination') {
				this.current_ride.destination = this.marker_1;
				this.marker_2.location_type = 'origin';
				text = 'destination';
			} else if (this.marker_1.location_type == 'origin') {
				this.current_ride.origin = this.marker_1;
				this.marker_2.location_type = 'destination';
				text = 'starting point';
			}
			location_type_disp.textContent = text;
			this.create_new_marker = true;
			flow.change_slide(route);
		} else if (route == 'details') {
			this.current_ride[this.marker_2.location_type] = this.marker_2;
			if (this.current_ride.driver == true) {
				flow.change_slide('driver_details')
			} else {
				flow.change_slide('passenger_details')
			}
		} else if (route == 'join_ride') {
			var id = btn.dataset.id;
			var container = document.querySelector('[data-route="join_ride"]');
			var source = document.querySelector('[data-template="join_ride"]').innerHTML;
			var template = Handlebars.compile(source);
			var ride;
			// Find specific ride by ID
			for (var i = 0; i < this.rides.length; i++) {
				if (this.rides[i].id = id) {
					ride = this.rides[i];
				}
			}
			var html = template({
				origin: ride.origin_add,
				dest: ride.dest_add,
				date: ride.date,
				time: ride.time,
				driver: ride.driver,
				driver_name: ride.driver_name,
				contact: ride.contact,
				id: ride.id
			});
			while (container.firstChild) {
				container.removeChild(container.firstChild)
			}
			container.insertAdjacentHTML('beforeend', html);
			flow.change_slide('join_ride');
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
			notify({
				type: 'success',
				strong: 'You created a new ride!',
				message: 'We sent you a confirmation email.'
			});
		}.bind(this));
		req_rides.fail(function (message, status) {
			this.flow.change_slide('select_location');
			notify({
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
			notify({
				type: 'success',
				strong: 'You asked for a ride!',
				message: 'We sent you a confirmation email.'
			});
		}.bind(this));
		req_rides.fail(function (message, status) {
			this.flow.change_slide('select_location');
			notify({
				type: 'danger',
				strong: 'Sorry!',
				message: 'The ride was not created. Please try again.'
			});
		}.bind(this));
	}

	// Sends request for person to join ride as passenger
	this.join_ride = function (e) {
		var target = e.target;
		var data = target.dataset.join.split(':');
		var req_rides = $.ajax({
			type: 'POST',
			url: '/join_ride',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify({
				type: data[0],
				id: data[1]
			})
		});
		req_rides.done(function (data) {
			this.flow.change_slide('select_location');
			notify({
				type: 'success',
				strong: 'You joined the ride!',
				message: 'We sent you a confirmation email.'
			});
		}.bind(this));
		req_rides.fail(function (data, status) {
			this.flow.change_slide('select_location');
			notify({
				type: 'danger',
				strong: 'Sorry!',
				message: 'You did not join the ride. Please try again.'
			});
		}.bind(this));
	}

	this.send_event = function (e) {
		e.preventDefault();
		var form = document.querySelector('[data-send="event"]')
		var event = {};
		event.name = form.name.value;
		event.address = this.marker_1.address;
		event.lat = this.marker_1.lat;
		event.lng = this.marker_1.lng;
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
			notify({
				type: 'success',
				strong: 'Event created!',
				message: 'We sent you a confirmation email.'
			});
		}.bind(this));
		req_event.fail(function (message, status) {
			this.flow.change_slide('select_location');
			notify({
				type: 'danger',
				strong: 'Sorry!',
				message: 'The event was not created. Please try again.'
			});
		}.bind(this));
	}
});

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