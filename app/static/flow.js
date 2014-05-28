var Flow = augment(Object, function () {
	this.constructor = function () {
		this.next = document.querySelectorAll('[data-next]');
		this.views = document.querySelectorAll('[data-slide]');
		this.loading = document.querySelector('[data-loading]');
		this.headers = document.querySelectorAll('[data-header]');
		this.loading.classList.add('hidden');

		this.col_map = document.querySelector('#col_map');
		this.col_dialog = document.querySelector('#col_dialog');

		this.specify = document.querySelectorAll('[data-specify]');

		this.id_last = 1;
		this.option = '';

		console.log(this.loading)

		for (var i = 0; i < this.views.length; i++) {
			var view = this.views[i];

			if (view.dataset.slide != 1) {
				view.classList.toggle('hidden');
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
		for (var i = 0; i < this.specify.length; i++) {
			var current = this.specify[i];
			current.addEventListener('click', this.specify_event.bind(this));
		}
	}

	this.next_event = function (e) {
		var btn = e.target;
		var opts = btn.dataset.next.split(':');
		this.change_slide(opts[0], opts[1]);
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

	this.specify_event = function (e) {
		var target = e.target;
		this.option = target.dataset.specify;
		this.change_slide(3);
	}

	this.change_slide = function (id, option) {
		// if (id == 2) {

		// }
		this.id_last = id;
		for (var i = 0; i < this.views.length; i++) {
			var view = this.views[i];
			if (!view.classList.contains('hidden')) {
				view.classList.add('hidden');
			}
			if (view.dataset.slide == id && view.dataset.option == option) {
				view.classList.remove('hidden');
			}
			if (view.dataset.slide == 2 && id == 2) {
				this.col_map.classList.remove('col-md-8');
				this.col_map.classList.add('col-md-6');
				// view.classList.remove('col-md-4');
				// view.classList.add('col-md-6');
			}
		}
		// this.loading.classList.remove('hidden');
		// window.setTimeout(function () {
		// 	this.loading.classList.add('hidden');
		// 	for (var i = 0; i < this.views.length; i++) {
		// 		var view = this.views[i];
				// if (view.dataset.slide == id) {
				// 	view.classList.remove('hidden');
				// }
		// 	}
		// }.bind(this), 1000);
		// for (var i = 0; i < this.headers.length; i++) {
		// 	var header = this.headers[i];
		// 	if (header.classList.contains('active')) {
		// 		header.classList.remove('active');
		// 	}
		// 	if (header.dataset.header == id) {
		// 		header.classList.add('active');
		// 	}
		// }
	}
});