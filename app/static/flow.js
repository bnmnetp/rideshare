var Flow = augment(Object, function () {
	this.constructor = function () {
		this.next = document.querySelectorAll('[data-next]');
		this.views = document.querySelectorAll('[data-route]');
		this.loading = document.querySelector('[data-loading]');
		this.headers = document.querySelectorAll('[data-header]');
		this.loading.classList.add('hidden');

		this.col_map = document.querySelector('#col_map');
		this.col_dialog = document.querySelector('#col_dialog');

		this.alert_template = document.querySelector('#alert_template');
		this.alert_container = document.querySelector('#alert_container');

		this.id_last = 1;
		this.option = '';
		this.map;

		console.log(this.loading)

		for (var i = 0; i < this.views.length; i++) {
			var view = this.views[i];
			
			if (view.dataset.route == 'select_location') {
				view.classList.remove('hidden')
			} else {
				view.classList.add('hidden');
			}
		}

		for (var i = 0; i < this.next.length; i++) {
			var current = this.next[i];
			current.addEventListener('click', this.next_event.bind(this));
		}
		for (var i = 0; i < this.headers.length; i++) {
			var current = this.headers[i];
			current.addEventListener('click', this.header_event.bind(this));
		}

	}

	this.set_map = function (map) {
		this.map = map;
	}

	this.next_event = function (e) {
		var btn = e.target;
		this.special_action(btn.dataset.next, btn);
		//this.change_slide(btn.dataset.next);
	}

	this.header_event = function (e) {
		var target = e.target;
		if (target.nodeName == "SPAN") {
			target = target.parentNode;
		}
		if (target.dataset.header < this.id_last) {
			this.change_slide(target.dataset.header);
		}
	}

	this.special_action = function (route, btn) {
		this.map.special_action(route, btn);
	}

	this.change_slide = function (route) {
		this.id_last = route;
		this.map.state = route;
		for (var i = 0; i < this.views.length; i++) {
			var view = this.views[i];
			if (!view.classList.contains('hidden')) {
				view.classList.add('hidden');
			}
		}
		this.loading.classList.remove('hidden');
		window.setTimeout(function () {
			this.loading.classList.add('hidden');
			for (var i = 0; i < this.views.length; i++) {
				var view = this.views[i];
				if (view.dataset.route == route) {
					view.classList.remove('hidden');
				}
			}
		}.bind(this), 500);
	}

	this.alert = function (opts) {
		var source = this.alert_template.innerHTML;
		var template = Handlebars.compile(source);
		var html = template(opts);
		this.alert_container.insertAdjacentHTML('beforeend', html);
	}
});