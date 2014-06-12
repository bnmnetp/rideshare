document.body.addEventListener('click', function (e) {
    var target = e.target;

    if (target.dataset.driver) {
        send('driver', target.dataset.driver);
    }
    if (target.dataset.passenger) {
        send('passenger', target.dataset.passenger);
    }
}.bind(this));

var send = function (type, action) {
	var data = {};
	data.type = type;
	data.action = action;

	var push = $.ajax({
		type: 'POST',
		url: window.location.pathname,
		dataType: 'json',
		contentType: 'application/json; charset=UTF-8',
		data: JSON.stringify(data)
	});

	push.done(function (data) {
		notify({
			type: 'success',
			strong: data.strong,
			message: data.message
		});
		if (type == 'driver' && action == 'leave') {
			var primary = document.querySelector('[data-driver="leave"]');
			var secondary = document.querySelector('[data-driver="join"]');
		} else if (type == 'driver' && action == 'join') {
			var primary = document.querySelector('[data-driver="join"]');
			var secondary = document.querySelector('[data-driver="leave"]');
		} else if (type == 'passenger' && action == 'leave') {
			var primary = document.querySelector('[data-passenger="leave"]');
			var secondary = document.querySelector('[data-passenger="join"]');
		} else if (type == 'passenger' && action == 'join') {
			var primary = document.querySelector('[data-passenger="join"]');
			var secondary = document.querySelector('[data-passenger="leave"]');
		}
		primary.parentNode.classList.add('hidden');
		secondary.parentNode.classList.remove('hidden');
	});

	push.fail(function (data, status) {
		notify({
			type: 'danger',
			strong: data.strong,
			message: data.message
		});
	});
}

