var Default = augment(Object, function () {
	this.constructor = function (form, ctx) {
		console.log(this);
		this.arr = Object.keys(ctx);

		for (var i = 0; i < this.arr.length; i++) {
			var cur = this.arr[i];
			if (form[cur]) {
				form[cur].value = ctx[cur];
			}
		}
	}

	this.get_values = function (data) {
		for (var i = 0; i < this.arr.length; i++) {
			var cur = this.arr[i];
			if (form[cur]) {
				data[cur] = form[cur].value;
			}
		}
	}
});