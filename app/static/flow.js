var Flow = augment(Object, function () {
	this.constructor = function (default_route) {
		this.next = document.querySelectorAll('[data-next]');
		this.views = document.querySelectorAll('[data-route]');

		this.id_last = 1;
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
				this.next_event.apply(this, [e]);
			}
		}.bind(this));

		this.current = this.find_next(default_route);
		if (this.current) {
			this.current.classList.add('active');
		}
	}

	this.set_handler = function (handler) {
		this.handler = handler;

	}

	this.next_event = function (e) {
		var btn = e.target;
		if (this.handler) {
			this.handler.special_action(btn.dataset.next, btn);
		} else {
			this.change_slide(btn.dataset.next);
		}	
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

	this.change_slide = function (route) {
		if (this.current) {
			this.current.classList.remove('active');
		}
		this.current = this.find_next(route);
		if (this.current) {
			this.current.classList.add('active');
		}

		this.id_last = route;
		this.handler.state = route;
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