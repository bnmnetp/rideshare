var Comment = augment(Object, function () {
	this.constructor = function (deta) {
		this.form = document.querySelector("[data-comment='form']");
		this.container = document.querySelector(deta.container);

		this.deta = deta;

	    this.form.addEventListener('submit', this.submit.bind(this))
	}

	this.submit = function (e) {
        e.preventDefault();
        var req = $.ajax({
            type: 'POST',
            url: '/comment',
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify({
                comment: e.target.comment.value,
                type: this.deta.type,
                id: this.deta.id
            })
        });
        req.done(function (data) {
            // Refer to comments.CommentHandler for expected response
            var source = document.querySelector('[data-comment="template"]').innerHTML;
            var template = Handlebars.compile(source);
            var html = template({
                name: data.name,
                date: data.date,
                comment: data.comment
            })
            this.container.insertAdjacentHTML('afterbegin', html);
        }.bind(this));
        req.fail(function (data, status) {
        	// Add notify func call
            console.log('Error');
        }.bind(this));
	}
})