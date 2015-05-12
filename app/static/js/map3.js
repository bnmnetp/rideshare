var get_geolocation = function (e) {
	var target = e.target;
	navigator.geolocation.getCurrentPosition(function (pos) {
		map.geocode_latlng({
			lat: pos.coords.latitude,
			lng: pos.coords.longitude
		});
	});
};

var get_parameter = function (name) {
	name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
	var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
		results = regex.exec(location.search);
	return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
};

// var display_geolocation = function () {

// };

var template_helper = function (target, template_str, ctx) {
	var template_node = document.querySelector('[data-template="' + template_str + '"]');
	console.log(template_node, template_str)
	var template_compile = Handlebars.compile(template_node.innerHTML);
	var html = template_compile(ctx);
	if (target) {
		target.insertAdjacentHTML('beforeend', html);
	}
	return html;
};

var has_geolocation = false;
if ('geolocation' in navigator) {
	console.log('Geolocation Availible');
	has_geolocation = true;
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
		url: '/static/img/end.png',
		anchor: new google.maps.Point(20, 20),
		size: new google.maps.Size(30, 40)
	},
	success: {
		url: '/static/img/start.png',
		anchor: new google.maps.Point(20, 20),
		size: new google.maps.Size(30, 40)
	},
	person: {
		url: '/static/img/person.png',
		anchor: new google.maps.Point(20, 20),
		size: new google.maps.Size(30, 40)
	},
	plus: {
		url: '/static/img/cross.png',
		anchor: new google.maps.Point(20, 20),
		size: new google.maps.Size(30, 40)
	}
}

var Markers = function Markers (map) {
	this.markers = [];
	this.map = map.map;
};

Markers.prototype.last_marker = function () {
	var last_idx = this.markers.length - 1;
	return this.markers[last_idx];
};

Markers.prototype.add_event_marker = function (lat, lng) {
	var position = new google.maps.LatLng(
		lat,
		lng
	);
	var marker = new google.maps.Marker({
		position: position,
		icon: icons.person
	});

	marker.setMap(this.map);

	this.markers.push(marker);
};

Markers.prototype.add_event_info = function (ctx) {
	var html = template_helper(null, 'event_info', ctx);

	var marker = this.last_marker();

	var info = new google.maps.InfoWindow({
		position: marker.position(),
		content: html
	});

	google.maps.event.addListener(marker, 'click', function () {
		info.open(this.map, marker)
	}.bind(this));
};

Markers.prototype.delete_marker = function () {
	if (this.markers.length > 0) {
		this.last_marker().setMap(null);
		this.markers.pop();
	}
};

var Map = function Map () {
	this.details = {};

	this.layout = {};
	this.layout.side = document.querySelector('[data-layout="side"]');
	this.layout.header = document.querySelector('[data-layout="header"]');
	this.layout.map = document.querySelector('[data-layout="map"]');

	this.flow = {};
	this.flow.current = 0;
	this.flow.views = ['type', 'location', 'details'];

	this.flow.actions = {
		type: function () {
			if (this.markers) {
				this.markers.delete_marker();
			}

			template_helper(
				this.layout.side,
				'type_select',
				{}
			);
		}.bind(this),
		location: function () {
			template_helper(
				this.layout.side,
				'location_select',
				{
					type: 'event'
				}
			);
			template_helper(
				this.layout.header,
				'selected',
				{}
			);
			this.check_geolocation();

			document
				.querySelector('[data-search]')
				.addEventListener('submit', function (e) {
					e.preventDefault();
					var address = e.target.address.value;
					this.geocoder.geocode({
						address: address
					}, this.act_address.bind(this));
				}.bind(this));

		}.bind(this),
		details: function () {
			template_helper(
				this.layout.side,
				'event_details',
				{}
			);
			document
				.querySelector('[data-send="event"]')
				.addEventListener('submit', this.new_event.bind(this));

			$('[data-datepicker]').datetimepicker({
				pickTime: false,
				defaultDate: moment().format("MM/DD/YYYY")
			});

			$('[data-time="container"]').datetimepicker({
				icons: {
					time: "fa fa-clock-o",
					date: "fa fa-calendar",
					up: "fa fa-arrow-up",
					down: "fa fa-arrow-down"
				},
				pickDate: false
			});

			$('[data-time="input"]').val(
				moment().format('h:mm A')
			)
		}.bind(this)
	};

	this.map_element = document.querySelector('#map_canvas');
	this.geocoder = new google.maps.Geocoder();

	this.flow.actions.type();
	this.create_map();

	document.addEventListener('click', function (e) {
		var target = e.target;

		if (target.dataset.next) {
			this.advance();
		}

		if (target.dataset.reset) {
			this.reset();
		}
	}.bind(this));
};

Map.prototype.add_markers = function (markers) {
	this.markers = markers;
}

Map.prototype.check_geolocation = function () {
	if (has_geolocation) {
		var geo_container = document.querySelector('[data-geolocation="container"]');
		geo_container.classList.remove('hidden');

		var geo_btn = document.querySelector('[data-geolocation="btn"]');
		geo_btn.addEventListener('click', get_geolocation.bind(this));	
	}
};

Map.prototype.create_map = function () {
	this.location = {
		lat: 43.313059,
		lng: -91.799501
	};
	this.map = new google.maps.Map(this.map_element, {
		draggableCursor: 'crosshair',
		center: new google.maps.LatLng(this.location.lat, this.location.lng),
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		zoom: 10
	});

	google.maps.event.addListener(this.map, 'click', this.geocode_address.bind(this))
};

Map.prototype.geocode_address = function (e) {
	this.latlng = e.latLng;
	this.geocoder.geocode({
		latLng: this.latlng
	}, this.act_address.bind(this));
};

Map.prototype.act_address = function (d) {
	if (this.current_view() == 'location') {
		this.markers.delete_marker();

		var point = d[0].geometry.location;
		this.details.lat = point.lat();
		this.details.lng = point.lng();
		this.details.add = d[0].formatted_address;
		console.log(this.details);

		var selected = document.querySelector('[data-location="text"]');
		selected.textContent = this.details.add;

		var btn = document.querySelector('[data-location="btn"]');
		btn.classList.remove('hidden');

		this.markers.add_event_marker(
			this.details.lat,
			this.details.lng
		);
	};
};

Map.prototype.current_view = function () {
	return this.flow.views[this.flow.current];
};

Map.prototype.advance = function () {
	this.clear_node(this.layout.side);
	this.clear_node(this.layout.header);
	this.flow.current++;
	var view = this.current_view();
	this.flow.actions[view]();
};

Map.prototype.reset = function () {
	this.clear_node(this.layout.side);
	this.clear_node(this.layout.header);
	this.flow.current = 0;
	var view = this.current_view();
	this.flow.actions[view]();
};

Map.prototype.clear_node = function (ele) {
	while (ele.firstChild) {
		ele.removeChild(ele.firstChild);
	}
};

Map.prototype.bind_events = function (parent, evt) {
	parent.addEventListener('click', evt.bind(this));
};

Map.prototype.new_event = function (e) {
	e.preventDefault();

	var form  = e.target;

	var m = {};
	m.name = form.name.value;
	m.address = this.details.add;
	m.lat = this.details.lat;
	m.lng = this.details.lng;
	m.date = form.date.value;
	m.time = form.time.value;
	m.details = form.details.value;
	m.location = form.location.value;
	m.circle = circle;

	var push = $.ajax({
		type: 'POST',
		url: '/newevent',
		dataType: 'json',
		contentType: 'application/json; charset=UTF-8',
		data: JSON.stringify(m)
	});

	push.done(function (data) {
		this.reset();
		notify({
			type: 'success',
			strong: 'Event created!',
			message: 'Redirecting...'
		});
		document.location = '/event/' + data.id;
	}.bind(this));

	push.fail(function (data, status) {
		notify({
			type: 'danger',
			strong: 'Sorry!',
			message: 'The event was not created. Please try again.'
		});
	}.bind(this));
};