var Filter = augment(Object, function () {
	this.constructor = function () {
		this.container = document.querySelector('[data-container="filter"]');
		this.source = document.querySelector('[data-template="ride"]').innerHTML;
		this.template = Handlebars.compile(this.source);
		this.circle = null;

		this.filters = document.querySelectorAll('[data-filter]');

		document.body.addEventListener('click', function (e) {
			var target = e.target;

			if (target.dataset.filter) {
				this.action(target.dataset.filter);
			}
		}.bind(this));
	};

	this.action = function (filter) {
		this.active(filter);
		this.start_loading();
		var fetch = $.ajax({
			type: 'POST',
			url: '/filter',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify({
				filter: filter,
				circle: null
			})
		});

		fetch.done(function (data) {
			this.display_results(data);
		}.bind(this));

		fetch.fail(function (message, status) {
			notify({
				type: 'danger',
				strong: 'Oh no.',
				message: 'Something went wrong.'
			})
		});
	};

	this.active = function (filter) {
		for (var i = 0; i < this.filters.length; i++) {
			var cur = this.filters[i];
			if (cur.dataset.filter == filter) {
				cur.classList.add('active');
			} else {
				cur.classList.remove('active');
			}
		}
	};

	this.clear_container = function () {
		while (this.container.hasChildNodes()) {
			this.container.removeChild(this.container.childNodes[0])
		}
	}

	this.display_results = function (data) {
		this.clear_container();
		if (data.length > 0) {
			for (var i = 0; i < data.length; i++) {
				var d = data[i];
				console.log(d);
				var html = this.template(d);
				this.container.insertAdjacentHTML('beforeend', html);
			}
		} else {
			this.container.insertAdjacentHTML(
				'beforeend',
				'<div class="panel-message">No rides match that criteria.</div>'
			);
		}
	};

	this.start_loading = function () {
		this.clear_container();
		var loading_html = '<div class="loading"><i class="fa fa-circle-o-notch fa-spin fa-5x"></i></div>';
		this.container.insertAdjacentHTML(
			'beforeend',
			loading_html
		)
	};
});