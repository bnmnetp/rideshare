var Flow = function Flow (def) {
	this.views = document.querySelectorAll('[data-view]');
	this.routes = document.querySelectorAll('[data-route]');

	this.highlight(def);
	this.switch(def);

	document.body.addEventListener('click', function (e) {
		var target = e.target;

		if (target.dataset.view) {
			this.highlight(target.dataset.view);
			this.switch(target.dataset.view);
		};
	}.bind(this));
};

Flow.prototype.highlight = function (id) {
	var i, view;

	for (i = 0; i < this.views.length; i++) {
		view = this.views[i];

		if (view.dataset.view == id) {
			view.classList.add('active');
		} else {
			view.classList.remove('active');
		}
	};
};

Flow.prototype.switch = function (id) {
	var i, route;

	for (i = 0; i < this.routes.length; i++) {
		route = this.routes[i];

		if (route.dataset.route == id) {
			route.classList.remove('hidden');
		} else {
			route.classList.add('hidden');
		}
	};
};