var QueryLocation = function QueryLocation (parent, def) {
	// default is obj for keys [add, lat, lng]
	this.parent = parent;
	this.btn = this.parent.querySelector('[data-location="search"]');
	this.input = this.parent.querySelector('[data-location="input"]');
	this.output = this.parent.querySelector('[data-location="output"]');
	this.address = this.parent.querySelector('[data-location="address"]');
	this.err = this.parent.querySelector('[data-location="error"]');

	this.result = def;

	this.has_address = false;

	this.set_defaults();

	this.btn.addEventListener('click', this.send_request.bind(this));
	this.input.addEventListener('change', function (e) {
		this.has_address = false;
		this.output.classList.add('hidden');
	}.bind(this));
};

QueryLocation.prototype.set_defaults = function () {
	this.input.value = this.result.add;
	if (this.result.add != null) {
		this.has_address = true;
		this.output.classList.remove('hidden');
		this.address.textContent = this.result.add;
	}
};

QueryLocation.prototype.send_request = function (e) {
	if (this.err.classList.contains('show')) {
		this.err.textContent = '';
		this.err.classList.remove('show');
	}
	if (this.input.value != '') {
		this.has_address = true;
		$.get(
			"http://maps.googleapis.com/maps/api/geocode/json?address=" + this.input.value,
			function (data) {
				this.output.classList.remove('hidden');
				this.address.textContent = data['results'][0]['formatted_address'];
				this.result.add = data['results'][0]['formatted_address'];
				this.result.lat = parseFloat(data['results'][0]['geometry']['location']['lat']);
				this.result.lng = parseFloat(data['results'][0]['geometry']['location']['lng']);

			}.bind(this)
		);
	} else {
		this.output.classList.remove('hidden');
		this.address.textContent = 'No address'
	}
	
    // address = urllib.quote(data['address'])
    // url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s" % address

    // response = urllib2.urlopen(url)
    // json_geocode = json.loads(response.read())
    // ride.origin_add = json_geocode['results'][0]['formatted_address']
    // ride.origin_lat = json_geocode['results'][0]['geometry']['location']['lat']
    // ride.origin_lng = json_geocode['results'][0]['geometry']['location']['lng']
};

QueryLocation.prototype.is_valid = function () {
	if (this.has_address) {
		this.err.textContent = '';
		this.err.classList.remove('show');
		return true;
	} else {
		this.err.textContent = 'Please search for the address before submitting.';
		this.err.classList.add('show');
		return false;
	}
};

QueryLocation.prototype.set_values = function (data) {
	data.ql_add = this.result.add;
	data.ql_lat = this.result.lat;
	data.ql_lng = this.result.lng;
};