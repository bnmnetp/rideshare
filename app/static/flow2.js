var Flow = augment(Object, function () {
	this.constructor = function (default_route, paths) {
		this.next = document.querySelectorAll('[data-next]');
		this.views = document.querySelectorAll('[data-route]');

		this.paths = paths;
		this.path = [];
		this.has_path = false;
		this.path_history = [];

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
				this.change_slide.apply(this, [target]);
			}
		}.bind(this));

		this.current = this.find_next(default_route);
		if (this.current) {
			this.current.classList.add('active');
		}
	}

	this.reset = function () {
		this.path = [];
		this.has_path = false;
		this.path_history = [];
		this.idx = 0;
		this.view_slide('select_location');
	}

	this.set_handler = function (handler) {
		this.handler = handler;
	}

	this.find_next = function (attr) {
		var next = false;
		for (var i = 0; i < this.next.length; i++) {
			var cur = this.next[i];
			if (cur.dataset.next == attr) {
				next = cur;
				break;
			}
		}
		return next;
	}

	this.change_slide = function (btn = false) {
		var route, option;

		if (!this.has_path && btn && btn.dataset.next) {
			route = btn.dataset.next;
			if (route in paths) {
				this.reset();
				this.path = this.paths[route];
				this.path_history.push(route);
				this.has_path = true;
				this.handler.state = route;
				if (this.handler) {
					this.handler.special_action(btn);
				}
				this.view_slide(this.path[this.idx])

				this.path_history.push(this.path[this.idx]);

				this.handler.state = this.path[this.idx];
			}
		} else if (this.has_path) {
			this.idx++;
			if (typeof this.path[this.idx] === 'object') {
				var imd = this.path[this.idx][btn.dataset.option];
				this.path = imd;
				this.idx = 0;
			}
			this.path_history.push(this.path[this.idx]);
			if (this.handler) {
				this.handler.special_action(btn);
			}
			this.view_slide(this.path[this.idx]);

			this.handler.state = this.path[this.idx];
		}
		console.log('Path', this.path_history);
		console.log('IDX', this.idx);
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