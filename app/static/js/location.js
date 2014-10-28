var QueryLocation = function QueryLocation (parent, submit_form) {
	this.parent = parent;
	this.btn = this.parent.querySelector('[data-location="search"]');
	this.input = this.parent.querySelector('[data-location="input"]');
	this.output = this.parent.querySelector('[data-location="output"]');
	this.address = this.parent.querySelector('[data-location="address"]');

	this.submit_form = submit_form;

	this.result = {
		'add': '',
		'lat': false,
		'lng': false
	}

	this.btn.addEventListener('click', this.send_request.bind(this));
};

QueryLocation.prototype.send_request = function (e) {
	if (this.input.value != '') {
		$.get(
			"http://maps.googleapis.com/maps/api/geocode/json?address=" + this.input.value,
			function (data) {
				this.output.classList.remove('hidden');
				this.address.textContent = data['results'][0]['formatted_address'];
				this.result.add = data['results'][0]['formatted_address'];
				this.result.lat = parseFloat(data['results'][0]['geometry']['location']['lat']);
				this.result.lng = parseFloat(data['results'][0]['geometry']['location']['lng']);
				this.submit_form.set('orig_address', this.result.add);
				this.submit_form.set('orig_lat', this.result.lat);
				this.submit_form.set('orig_lng', this.result.lng);
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