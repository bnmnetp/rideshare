// augment js
// https://github.com/javascript/augment
(function (global, factory) {
    if (typeof define === "function" && define.amd) define(factory);
    else if (typeof module === "object") module.exports = factory();
    else global.augment = factory();
}(this, function () {
    "use strict";

    var Factory = function () {};
    var slice = Array.prototype.slice;

    return function (base, body) {
        var uber = Factory.prototype = typeof base === "function" ? base.prototype : base;
        var prototype = new Factory;
        body.apply(prototype, slice.call(arguments, 2).concat(uber));
        if (!prototype.hasOwnProperty("constructor")) return prototype;
        var constructor = prototype.constructor;
        constructor.prototype = prototype;
        return constructor;
    }
}));

var community = new College("Luther College", "700 College Drive Decorah,IA", 43.313059, -91.799501);

var Map = augment(Object, function () {
	this.constructor = function () {
		// set coordinates for your community here:
		this.location = {
			lat: 43.313059,
			lng: -91.799501
		};
		this.rides = [];
		this.overlays = [];
		this.windows = [];
		this.events = [];
		this.icons = {};
		this.cluster_click = false;
		this.map;
		this.geocoder;
		this.address;
		this.click_listener;
		this.mc;
		this.direction_service;
		this.direction_display;

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
	// Creates map markers and stores them in this.icons
	this.create_markers = function () {
		this.icons.event = new google.maps.Icon({
			url: 'static/stargate.png',
			anchor: new google.maps.Point(20,20),
			size: new google.maps.Size(30,40)
		})
		this.icons.marker_shadow = new google.maps.Icon({
			url: 'http://labs.google.com/ridefinder/images/mm_20_shadow.png',
			size: new google.maps.Size(22,20)
		})
		this.icons.car_success = new google.maps.Icon({
			url: 'static/carGreen.png',
			anchor: new google.maps.Point(20,20),
			size: new google.maps.Size(30,40)
		})
		this.icons.car_error = new google.maps.Icon({
			url: 'static/carRed.png',
			anchor: new google.maps.Point(20,20),
			size: new google.maps.Size(30,40)
		})
		this.icons.person = new google.maps.Icon({
			url: 'static/person.png',
			anchor: new google.maps.Point(20,20),
			size: new google.maps.Size(30,40)
		})
		this.icons.person_shadow = new google.maps.Icon({
			url: 'static/person.png',
			anchor: new google.maps.Point(20,20),
			size: new google.maps.Size(30,40)
		})
		this.icons.plus = new google.maps.Icon({
			url: 'static/cross.png',
			anchor: new google.maps.Point(20,20),
			size: new google.maps.Size(30,40)
		})

		this.map = new google.maps.Map({
			mapDiv: document.querySelector('#map_canvas'),
			opts: {
				draggableCursor: 'crosshair',
				center: google.maps.LatLng(this.location.lat, this.location.lng),
				mapTypeId: google.maps.MapTypeId.ROADMAP,
				zoom: 6
			}
		})
		this.marker = new google.maps.Marker({
			position: this.location,
			map: this.map
		})
		this.direction_service = new google.maps.DirectionsService();
		this.direction_display = new google.maps.DirectionsRenderer({preserveViewport:false});
	}

	this.add_ride = function () {
		
	}

	this.add_event = function () {

	}
});

var College = augment(Object, function () {
	this.constructor(name, address, lat, long) {
		this.name = name;
		this.address = address;
		this.lat = lat;
		this.long = long;
	}
})

var Location = augment(Object, function () {
	this.constructor(title, lat, long) {
		this.title = title;
		this.lat = lat;
		this.long = long;
	}
})