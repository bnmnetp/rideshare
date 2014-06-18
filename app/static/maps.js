function getParameterByName(name) {
	name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
	var regexS = "[\\?&]" + name + "=([^&#]*)";
	var regex = new RegExp(regexS);
	var results = regex.exec(window.location.search);
	if (results == null) {
		return "";
	}
	else {
		return decodeURIComponent(results[1].replace(/\+/g, " "));
	}		
}

// if ('geolocation' in navigator) {
// 	console.log('location availible')
// 	display_geolocation();
// } else {
// 	console.log('no geolocation')
// }

// var display_geolocation = function () {
// 	var geo_btn = document.querySelector('#geo_btn');
// 	geo_btn.classList.remove('hidden');

// 	geo_btn.addEventListener('click');
// }

var icons = {
	event: {
		url: '/static/stargate.png',
		anchor: new google.maps.Point(20, 20),
		size: new google.maps.Size(30, 40)
	},
	shadow: {
		url: 'http://labs.google.com/ridefinder/images/mm_20_shadow.png',
		size: new google.maps.Size(22, 20)
	},
	error: {
		url: '/static/carRed.png',
		anchor: new google.maps.Point(20, 20),
		size: new google.maps.Size(30, 40)
	},
	success: {
		url: '/static/carGreen.png',
		anchor: new google.maps.Point(20, 20),
		size: new google.maps.Size(30, 40)
	},
	person: {
		url: '/static/person.png',
		anchor: new google.maps.Point(20, 20),
		size: new google.maps.Size(30, 40)
	},
	plus: {
		url: '/static/cross.png',
		anchor: new google.maps.Point(20, 20),
		size: new google.maps.Size(30, 40)
	}
}

var Forms = augment(Object, function () {
	this.constructor = function () {
		this.send_ride = document.querySelector('[data-send="ride"]');
		this.send_ride.addEventListener('submit', this.controller_ride.bind(this));

		this.send_pass = document.querySelector('[data-send="passenger"]');
		this.send_pass.addEventListener('submit', this.controller_pass.bind(this));

		this.send_event = document.querySelector('[data-send="event"]');
		this.send_event.addEventListener('submit', this.controller_event.bind(this));

		document.body.addEventListener('click', function (e) {
			var target = e.target;
			if (target.dataset.join) {
				this.controller_join.apply(this, [e]);
			}
		}.bind(this));
	}

	this.controller_ride = function (e) {
		e.preventDefault();
		console.log(e);

		var form  = e.target;
		var m = map.current_ride;

		m.max_passengers = form.max_passengers.value;
		m.date = form.date.value;
		m.time = form.time.value;
		m.details = form.details.value;

		var push = $.ajax({
			type: 'POST',
			url: '/newride',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify(m)
		});

		push.done(function (data) {
			flow.change_slide('select_location');
			notify({
				type: 'success',
				strong: 'You created a new ride!',
				message: 'We sent you a confirmation email.'
			});
		});

		push.fail(function (message, status) {
			notify({
				type: 'danger',
				strong: 'Sorry!',
				message: 'The ride was not created. Please try again.'
			});
		});
	}

	this.controller_pass = function (e) {
		e.preventDefault();
		console.log(e);

		var form  = e.target;
		var m = map.current_ride;

		m.date = form.date.value;
		m.time = form.time.value;
		m.details = form.details.value;

		var push = $.ajax({
			type: 'POST',
			url: '/newride',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify(m)
		});

		push.done(function (data) {
			flow.change_slide('select_location');
			notify({
				type: 'success',
				strong: 'You asked for a ride!',
				message: 'We sent you a confirmation email.'
			});
		});

		push.fail(function (message, status) {
			notify({
				type: 'danger',
				strong: 'Sorry!',
				message: 'The ride was not created. Please try again.'
			});
		});
	}

	this.controller_event = function (e) {
		e.preventDefault();
		console.log(e);

		var form  = e.target;

		var m = {};
		m.name = form.name.value;
		m.address = map.marker_1.address;
		m.lat = map.marker_1.lat;
		m.lng = map.marker_1.lng;
		m.date = form.date.value;
		m.time = form.time.value;
		m.details = form.details.value;

		var push = $.ajax({
			type: 'POST',
			url: '/newevent',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify(m)
		});

		push.done(function (data) {
			flow.change_slide('select_location');
			notify({
				type: 'success',
				strong: 'Event created!',
				message: 'We sent you a confirmation email.'
			});
		});

		push.fail(function (data, status) {
			notify({
				type: 'danger',
				strong: 'Sorry!',
				message: 'The event was not created. Please try again.'
			});
		});
	}

	this.controller_join = function (e) {
		e.preventDefault();
		var target = e.target;
		var data = target.dataset.join.split(':');

		var push = $.ajax({
			type: 'POST',
			url: '/join_ride',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify({
				type: data[0],
				id: data[1]
			})
		});

		push.done(function (data) {
			flow.change_slide('select_location');
			notify({
				type: 'success',
				strong: 'You joined the ride!',
				message: 'We sent you a confirmation email.'
			});
		});

		push.fail(function (data, status) {
			notify({
				type: 'danger',
				strong: 'Sorry!',
				message: 'You did not join the ride. Please try again.'
			});
		});
	}
});

var Markers = augment(Object, function () {
	this.constructor = function () {
		this.req_events = $.ajax({
			type: 'POST',
			url: '/events',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify({
				circle: getParameterByName('circle')
			})
		});

		this.req_events.done(function (data) {
			map.events = data;
			for (var i = 0; i < map.events.length; i++) {
				this.add_event(i);
			}
		}.bind(this));

		this.req_events.fail(function (message, status) {

		}.bind(this));

		this.req_rides = $.ajax({
			type: 'POST',
			url: '/rides',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify({
				circle: getParameterByName('circle')
			})
		});

		this.req_rides.done(function (data) {
			map.rides = data;
			for (var i = 0; i < map.rides.length; i++) {
				this.add_ride(i);
			}
		}.bind(this));

		this.req_rides.fail(function (message, status) {

		}.bind(this));
	}

	this.add_event = function (idx) {
		/* Get Event */
		var event = map.events[idx];
		/* Get template for popup on click */
		var layout = document.querySelector('[data-template="popup-event"]');
		var source = Handlebars.compile(layout.innerHTML);
		/* Generate HTML */
		var html = source({
			add: event.address,
			date: event.date,
			id: event.id
		});

		event_pos = new google.maps.LatLng(
			event.lat,
			event.lng
		)

		event.marker = new google.maps.Marker({
			position: event_pos,
			icon: icons.person
		})

		event.marker_info = new google.maps.InfoWindow({
			position: event_pos,
			content: html
		});

		google.maps.event.addListener(event.marker, 'click', function () {
			event.marker_info.open(map.map, event.marker)
		}.bind(this));

		event.marker.setMap(map.map);
	}

	this.add_ride = function (idx) {
		/* Get ride */
		var ride = map.rides[idx];
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
			icon: icons.success
		});
		ride.origin_info = new google.maps.InfoWindow({
			position: origin_pos,
			content: origin_html
		});

		google.maps.event.addListener(ride.origin_marker, 'click', function () {
			ride.origin_info.open(map.map, ride.origin_marker)
		}.bind(this));
		ride.origin_marker.setMap(map.map);
		
		if (ride.event == 'None') {
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
				icon: icons.error
			})
			ride.dest_info = new google.maps.InfoWindow({
				position: dest_pos,
				content: dest_html
			});

			google.maps.event.addListener(ride.dest_marker, 'click', function () {
				ride.dest_info.open(map.map, ride.dest_marker);
			}.bind(this));
			ride.dest_marker.setMap(map.map);
		}

	}
});

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
		this.map;
		this.geocoder;

		this.state = 'select_location';
		this.indicator = '';
		this.current_ride = {};
		this.current_event = {};

		this.markers = [];

		this.marker_start = {};
		this.marker_end = {};

		this.create_new_marker = true;

		this.create_markers();

		this.search_form = document.querySelector('#search_form');
		this.search_form.addEventListener('submit', function (e) {
			e.preventDefault();
			var address = this.search_form.address.value;
			this.geocoder.geocode({
				address: address
			}, this.disp_address.bind(this));
		}.bind(this));
		this.reset();

		this.reset_btn = document.querySelector('[data-reset]');
		this.reset_btn.addEventListener('click', function (e) {
			this.reset();
		}.bind(this));
	}

	this.reset = function () {
		if (typeof flow != 'undefined') {
			flow.change_slide('select_location');
		}

		this.create_new_marker = true;
		
		this.indicator = '';

		for (var i = 0; i < this.markers.length; i++) {
			this.markers[i].setMap(null);
		}
		this.markers = [];
	}

	this.create_markers = function () {
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
			this.markers.push(marker);
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

	this.get_address = function (e) {
		this.latLng = e.latLng;
		this.geocoder.geocode({
			latLng: this.latLng
		}, this.disp_address.bind(this));
	}

	this.disp_address = function (location) {
		var point = location[0].geometry.location;
		this.set_window(point, 'New Marker');

		if (this.state == 'event_location') {
			this.marker_start.lat = point.k;
			this.marker_start.lng = point.A;
			this.marker_start.address = location[0].formatted_address;
			flow.change_slide('events_details');
		}
		if (this.state == 'ride_location') {
			this.marker_start.lat = point.k;
			this.marker_start.lng = point.A;
			this.marker_start.address = location[0].formatted_address;
			flow.change_slide('select_type');
		}
		if (this.state == 'location_2') {
			this.marker_2.lat = point.k;
			this.marker_2.lng = point.A;
			this.marker_2.address = location[0].formatted_address;

			var location_2 = document.querySelector('[data-ride="loc_2"]');
			var location_btn = document.querySelector('[data-ride="loc_btn"]');

			location_2.textContent = this.marker_2.address;
			location_btn.classList.remove('hidden');
		}
	}

	this.special_action = function (route, btn) {
		// Set location #1
		if (route == 'location_dest') {
			if (btn.dataset.ride == 'driver') {
				this.current_ride.driver = true;
			} else if (btn.dataset.ride == 'passenger') {
				this.current_ride.driver = false;
			}
			if (this.indicator == 'event_location') {
				if (this.current_ride.driver == true) {
					flow.change_slide('driver_details');
				} else if (this.current_ride.driver == false) {
					flow.change_slide('passenger_details');
				}
			} else {
				flow.change_slide(route);
			}
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
		} else if (route == 'event_ride_location') {
			this.current_ride.event = btn.dataset.id;
			flow.change_slide(route);
		} else {
			flow.change_slide(route);
		}
	}
});

var map = new Map();
var markers = new Markers();
var forms = new Forms();