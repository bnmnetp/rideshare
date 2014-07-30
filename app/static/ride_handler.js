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
		document.location.reload(true);
	}.bind(this));

	push.fail(function (data, status) {
		notify({
			type: 'danger',
			strong: data.strong,
			message: data.message
		});
	});
}

