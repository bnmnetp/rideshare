

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

		this.marker_current = {};

		this.create_new_marker = true;

		var d = new Date();

		var req_events = $.ajax({
			type: 'GET',
			url: '/getevents',
			data: {
				circle: getParameterByName('circle'),
				after: d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate()
			}
		});
		req_events.done(function (message) {

		});
		req_events.fail(function (message, status) {

		});

		var req_rides = $.ajax({
			type: 'GET',
			url: '/getrides',
			data: {
				circle: getParameterByName('circle'),
				after: d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate()
			}
		});
		req_rides.done(function (message) {

		});
		req_rides.fail(function (message, status) {

		});

		this.create_markers();
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
		flow.change_slide(2, 'general');
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

	this.special_action = function (id, option) {
		// Set location #1 for data-slide=3, data-option=ride
		console.log('Test')
		if (id == 3 && option == 'ride') {
			console.log('Test')
			var location = document.querySelector('[data-location="1"]');
			location.textContent = this.marker_current.address;
		}
		if (id = 4 && option == 'ride') {
			var previous = document.querySelector('[data-location="3"], [data-option="ride"]');
		}
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
