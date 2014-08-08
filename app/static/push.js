var Push = augment(Object, function () {

    this.constructor = function (obj) {
        this.form = obj.form;
        this.model = obj.model;
        this.method = obj.method;
        this.route = obj.route;
        this.done = obj.done;
        this.fail = obj.fail;

        this.keys = Object.keys(this.model);

        this.form.addEventListener('submit', function (e) {
            e.preventDefault();
            this.submit_form.apply(this, [e]);
        }.bind(this), false);
    };

    this.set_defaults = function () {
        var i, current;
        for (i = 0; i < this.keys.length; i++) {
            current = this.keys[i];
            if (this.form[current]) {
                this.form[current].value = this.model[current];
            }
        }
    };

    this.get_values = function () {
        var data = {}, i, current;

        for (i = 0; i < this.keys.length; i++) {
            current = this.keys[i];
            if (this.form[current]) {
                data[current] = this.form[current].value;
            }
        }

        return data;
    };

    this.submit_form = function (e) {
        e.preventDefault();

        var data = {}, req;

        data = this.get_values();

        req = $.ajax({
            type: this.method,
            url: this.route,
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify(data)
        });

        req.done(this.done.bind(this));

        req.fail(this.fail.bind(this));
    }.bind(this);

});