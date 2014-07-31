var Flow = augment(Object, function () {
	this.constructor = function (default_route, paths) {
		this.next = document.querySelectorAll('[data-next]');
		this.views = document.querySelectorAll('[data-route]');

		this.paths = paths;
		this.path = [];
		this.has_path = false;
		this.history = [];

		this.option = '';
		this.handler = false;
		this.default_route = default_route;

		for (var i = 0; i < this.views.length; i++) {
			var view = this.views[i];
			
			if (view.dataset.route == this.default_route) {
				view.classList.remove('hidden')
			} else {
				view.classList.add('hidden');
			}
		}

		document.body.addEventListener('click', function (e) {
			var target = e.target;
			if (target.dataset.next) {
				this.find_opts.apply(this, [target]);
			}
		}.bind(this));
	}

	this.reset = function () {
		this.path = [];
		this.has_path = false;
		this.history = [];
		this.idx = 0;
		this.view_slide('path');
	}

	this.set_handler = function (handler) {
		this.handler = handler;
	}

	this.find_opts = function (btn) {
		var opts = {};
		if (btn && btn.dataset) {
			opts = btn.dataset;
		}
		this.change_slide(opts);
	}

	this.change_slide = function (opts) {
		var route;
		if ('next' in opts) {
			route = opts.next;
			if (route in paths) {
				this.reset();
				this.path = paths[route];
				this.history.push(route);
				this.has_path = true;
			}
		}
		if (this.has_path) {
			var from = this.history[this.history.length - 1];
			var to = this.path[this.idx];
			var opts;
			this.history.push(to);
			this.handler.state = to;
			this.handler.special_action(from, to, opts);
			this.view_slide(to);
			this.idx++;
		}
	}

	this.view_slide = function (route) {
		for (var i = 0; i < this.views.length; i++) {
			var view = this.views[i];
			if (view.dataset.route == route) {
				view.classList.remove('hidden');
			} else {
				if (!view.classList.contains('hidden')) {
					view.classList.add('hidden');
				}
			}

		}
	}
});