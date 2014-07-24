var Filter = augment(Object, function () {
	this.constructor = function () {
		this.container = document.querySelector('[data-container="filter"]');
		this.source = document.querySelector('[data-template="ride"]').innerHTML;
		this.template = Handlebars.compile(this.source);
		document.body.addEventListener('click', function (e) {
			var target = e.target;

			if (target.dataset.filter) {
				this.action(target.dataset.filter);
			}
		}.bind(this));
	};

	this.action = function (filter) {
		var fetch = $.ajax({
			type: 'POST',
			url: '/rides',
			dataType: 'json',
			contentType: 'application/json; charset=UTF-8',
			data: JSON.stringify({
				filter: filter
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

	this.display_results = function (data) {
		for (var i = 0; i < data.length; i++) {
			var d = data[i];

			var html = this.template(d);
			this.container.insertAdjacentHTML('beforeend', html);
		}
	};
});