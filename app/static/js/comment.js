var Comment = augment(Object, function () {
    this.constructor = function (deta) {
        this.form = document.querySelector("[data-comment='form']");
        this.container = document.querySelector(deta.container);
        this.source = document.querySelector('[data-comment="template"]').innerHTML;
        this.template = Handlebars.compile(this.source);

        this.deta = deta;

        this.get_comments(deta);

        this.form.addEventListener('submit', this.submit.bind(this))
    }

    this.add_comment = function (deta) {
        var html = this.template(deta);
        this.container.insertAdjacentHTML('afterbegin', html);
    }

    this.get_comments = function (deta) {
        var req = $.ajax({
            type: 'POST',
            url: '/comments',
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify({
                type: deta.type,
                id: deta.id
            })
        });

        req.done(function (data) {
            this.parse_comments(data);
        }.bind(this));
    }

    this.parse_comments = function (data) {
        for (var i = 0; i < data.length; i++) {
            this.add_comment(data[i]);
        }
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
                id: this.deta.id,
                is_owner: true
            })
        });
        req.done(function (data) {
            // Refer to comments.CommentHandler for expected response
            data.is_owner = true
            this.add_comment(data);
            e.target.comment.value = '';
        }.bind(this));
        req.fail(function (data, status) {

            console.log('Error');
        }.bind(this));
    }
})