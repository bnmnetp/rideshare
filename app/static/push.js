var SubmitForm = augment(Object, function () {

    this.constructor = function (obj) {
        this.form = obj.form;
        this.model = obj.model;
        this.method = obj.method;
        this.route = obj.route;
        this.done = obj.done;
        this.fail = obj.fail;

        this.data = {};

        this.keys = Object.keys(this.model);

        this.set_defaults();

        this.form.addEventListener('submit', this.submit_form.bind(this), false);
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
        var i, current;

        for (i = 0; i < this.keys.length; i++) {
            current = this.keys[i];
            if (this.form[current]) {
                this.data[current] = this.form[current].value;
            }
        }
    };

    this.submit_form = function (e) {
        e.preventDefault();

        var req;

        this.get_values();

        req = $.ajax({
            type: this.method,
            url: this.route,
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify(this.data)
        });

        req.done(this.done.bind(this));

        req.fail(this.fail.bind(this));
    };

    this.set = function (key, value) {
        this.data[key] = value;
    };

});