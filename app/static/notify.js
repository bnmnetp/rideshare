// notify.js is a wrapper function for showing templated alerts
// Needs [data-notify="template"] as a handlebar templae
// Needs [data-notify="container"] for where you want the alert to be rendered
// opts are the variables to be displayed in template
var notify = function (opts) {
	var alert_template = document.querySelector('[data-notify="template"]');
	var alert_container = document.querySelector('[data-notify="container"]');

	var source = alert_template.innerHTML;
	var template = Handlebars.compile(source);
	var html = template(opts);
	alert_container.insertAdjacentHTML('beforeend', html);
}