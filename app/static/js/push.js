var SubmitForm = augment(Object, function () {

    this.constructor = function (obj) {
        this.form = obj.form;
        this.model = obj.model;
        this.method = obj.method;
        this.route = obj.route;
        this.done = obj.done;
        this.fail = obj.fail;

        if (obj.libs) {
            this.libs = obj.libs;
        } else {
            this.libs = [];
        }

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
                if (this.form[current].type == 'checkbox') {
                    if (this.model[current] == true) {
                        this.form[current].checked = true;
                    }
                } else if (current != '') {
                    this.form[current].value = this.model[current];
                }
            }
        }
    };

    this.get_values = function () {
        var i, current;

        for (i = 0; i < this.keys.length; i++) {
            current = this.keys[i];
            if (this.form[current]) {
                if (this.form[current].type == 'checkbox') {
                    this.data[current] = this.form[current].checked;
                } else {
                    this.data[current] = this.form[current].value;   
                }
            } else if (this.data[current]) {

            } else {
                this.data[current] = this.model[current];
            }
        }
    };

    this.submit_form = function (e) {
        e.preventDefault();

        var valid = true;

        for (var lib of this.libs) {
            console.log('test')
            if (!lib.is_valid()) {
                valid = false;
            } else {
                lib.set_values(this.data);
            }
        }

        if (valid) {
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
        } else {
            this.fail.bind(this)('Library not valid', 500);
        }
        valid = true;
    };

    this.set = function (key, value) {
        this.data[key] = value;
    };
});