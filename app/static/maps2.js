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

if (!Array.prototype.last){
    Array.prototype.last = function () {
        return this[this.length - 1];
    };
};

var get_geolocation = function (e) {
	var target = e.target;
	navigator.geolocation.getCurrentPosition(function (pos) {
		map.geocode_latlng({
			lat: pos.coords.latitude,
			lng: pos.coords.longitude
		});
	});
};

var display_geolocation = function () {
	var geo_btns = document.querySelectorAll('.geo_location');
	for (var i = 0; i < geo_btns.length; i++) {
		var btn = geo_btns[i];
		btn.classList.remove('hidden');
		btn.addEventListener('click', get_geolocation);
	}
};

if ('geolocation' in navigator) {
	console.log('Geolocation Availible');
	display_geolocation();
} else {
	console.log('Geolocation Unavailible');
}

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
		var m = map.new_ride;

		m.max_passengers = form.max_passengers.value;
		m.date = form.date.value;
		m.time = form.time.value;
		m.details = form.details.value;
		m.circle = getParameterByName('circle');
		m.driver = true;

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
		var m = map.new_ride;

		m.date = form.date.value;
		m.time = form.time.value;
		m.details = form.details.value;
		m.circle = getParameterByName('circle');
		m.driver = false;

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

		var form  = e.target;

		var m = {};
		m.name = form.name.value;
		m.address = map.new_event.loc.address;
		m.lat = map.new_event.loc.lat;
		m.lng = map.new_event.loc.lng;
		m.date = form.date.value;
		m.time = form.time.value;
		m.details = form.details.value;
		m.circle = getParameterByName('circle');

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

var paths = {
	create_event: [
		'location_selection',
		'event_details'
	],
	create_ride: [
		'select_type',
		{
			driver: [
				'location_selection',
				'location_dest',
				'safety',
				'driver_details'
			],
			passenger: [
				'location_selection',
				'location_dest',
				'passenger_details'
			]
		}
	],
	ride_to_event: [
		'location_selection',
		'select_type',
		{
			driver: [
				'safety',
				'driver_details'
			],
			passenger: [
				'passenger_details'
			]
		}
	],
	join_ride: [
		'join_ride'
	]
};

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

		this.last = false;
		this.state = 'select_location';
		this.indicator = '';
		this.new_ride = {};
		this.new_event = {};

		this.markers = [];

		this.create_new_marker = false;

		this.create_markers();

		this.s_forms = document.querySelectorAll('[data-search]');
		for (var i = 0; i < this.s_forms.length; i++) {
			var current = this.s_forms[i];
			current.addEventListener('submit', function (e) {
				e.preventDefault();
				var address = current.address.value;
				this.geocoder.geocode({
					address: address
				}, this.extract_address.bind(this));
			}.bind(this));
		}

		this.reset();

		this.reset_btn = document.querySelector('[data-reset]');
		this.reset_btn.addEventListener('click', function (e) {
			this.reset();
		}.bind(this));
	};

	this.reset = function () {
		if (typeof flow != 'undefined') {
			this.last = false;
			this.state = 'select_location';
			flow.reset();
		}

		this.create_new_marker = true;
		
		this.indicator = '';

		for (var i = 0; i < this.markers.length; i++) {
			this.markers[i].setMap(null);
		}
		this.markers = [];
	};

	this.create_markers = function () {
	    this.map = new google.maps.Map(document.querySelector('#map_canvas'), {
	        draggableCursor: 'crosshair',
	        center: new google.maps.LatLng(this.location.lat, this.location.lng),
	        mapTypeId: google.maps.MapTypeId.ROADMAP,
	        zoom: 10
	    });

	    google.maps.event.addListener(this.map, 'click', this.get_address.bind(this))

		this.geocoder = new google.maps.Geocoder();
	};

	this.set_window = function (location, icon) {
		if (this.create_new_marker) {
			var latlng = new google.maps.LatLng(location.lat, location.lng);

			var marker = new google.maps.Marker({
				position: latlng,
				map: this.map,
				icon: icons[icon]
			});

			this.map.panTo(latlng);
			this.markers.push(marker);

			this.create_new_marker = false;
		} else {
			console.log('Cannot create new marker right now');
		}
	};

	this.geocode_latlng = function (deta) {
		console.log(deta);
		var latlng = new google.maps.LatLng(deta.lat, deta.lng);
		this.geocoder.geocode({
			latLng: latlng
		}, this.extract_address.bind(this));
	};

	this.get_address = function (e) {
		this.latlng = e.latLng;
		this.geocoder.geocode({
			latLng: this.latlng
		}, this.extract_address.bind(this));
	};

	this.extract_address = function (location) {
		var point = location[0].geometry.location;
		var details = {};
		details.lat = point.lat();
		details.lng = point.lng();
		details.add = location[0].formatted_address;
		details.point = point;
		this.disp_address(details);
	};

	this.disp_address = function (deta) {
		console.log(this.state);
		if (this.state == 'location_selection') {
			console.log('selection')
			var set = {};
			if (flow.path_history.indexOf('create_ride') > -1) {
				this.set_window(deta, 'success');
				this.new_ride.orig = {};
				set = this.new_ride.orig;
			} else if (flow.path_history.indexOf('create_event') > -1) {
				this.set_window(deta, 'person');
				this.new_event.loc = {};
				set = this.new_event.loc;
			} else if (flow.path_history.indexOf('ride_to_event') > -1) {
				this.set_window(deta, 'error');
				this.new_ride.dest = {};
				set = this.new_ride.dest;
			}
			set.lat = deta.lat;
			set.lng = deta.lng;
			set.address = deta.add;

			var select_text = document.querySelector('[data-location="text"]');
			var select_btn = document.querySelector('[data-location="btn"]');

			select_text.textContent = set.address;
			select_btn.classList.remove('hidden');
		}
		if (this.state == 'location_dest') {
			console.log('destination')
			this.set_window(deta, 'error');
			this.new_ride.dest = {};
			this.new_ride.dest.lat = deta.lat;
			this.new_ride.dest.lng = deta.lng;
			this.new_ride.dest.address = deta.add;

			var loc_dest = document.querySelector('[data-ride="loc_dest"]');
			var loc_btn = document.querySelector('[data-ride="loc_btn"]');

			loc_dest.textContent = this.new_ride.dest.address;
			loc_btn.classList.remove('hidden');
		}
	};

	this.special_action = function (btn) {
		if (this.state == 'select_location') {
			this.create_new_marker = false;
		}
		if (this.state == 'join_ride') {
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
		}
		if (this.state == 'ride_to_event') {
			this.new_ride.event = btn.dataset.id;
		}
		if (flow.path_history.last() == 'location_selection') {
			this.create_new_marker = true;
			var container = document.querySelector('[data-route="location_selection"]');
			var source = document.querySelector('[data-template="select_location"]').innerHTML;
			var template = Handlebars.compile(source);

			var html = template({
				type: 'test'
			});
			while (container.firstChild) {
				container.removeChild(container.firstChild)
			}
			container.insertAdjacentHTML('beforeend', html);
		}
		if (flow.path_history.last() == 'location_dest') {
			this.create_new_marker = true;
		}
	};
});

var map = new Map();
var markers = new Markers();
var forms = new Forms();