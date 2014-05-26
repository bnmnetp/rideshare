// augment js
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

var Map = augment(Object, function () {
	this.constructor = function () {
		var rides = [],
		overlays = [],
		windows = [],
		events = [],
		icons = {},
		cluster_click = false;
		var map,
		geocoder,
		address,
		click_listener,
		mc,
		direction_service,
		direction_display;

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