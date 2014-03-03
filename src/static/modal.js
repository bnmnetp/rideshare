$(function() {
	$("#rideForm").formwizard({ 
		formPluginEnabled: true,
	 	validationEnabled: true,
	 	focusFirstInput : true,
	 	formOptions :{
			success: function(data){
				$("#rideForm").formwizard("reset");
				modalClose();
			}}, 
			beforeSubmit: function(data){
				//$("#data").html("data sent to the server: " + $.param(data));
				$("#to").html("DID THIS WORK?");
				console.log("RIGHT BEEFORE SUBMIT");
				},
			dataType: 'json',
			resetForm: true,
		validationOptions : {
			rules: {
				contact: "required"
			}
		}
	});
	 	
	$("#rideForm").bind("step_shown", function(event, data){

		if (data['isLastStep'] == true) {
			var toCollege = $("#toLuther").val();
			var driver = $("#driver").val();
			var maxp = $("#maxp").val();
			var earlylate = $("#earlylate option:selected")[0]['text'];
			var partofday = $("#partofday option:selected")[0]['text'];
			var month = $("#month option:selected")[0]['text'];
			var day = $("#day option:selected")[0]['text'];
			var year = $("#year option:selected")[0]['text'];
			var contact = $(".contact");
			var comment = $(".comment");
			console.log(comment);
			addDriver();
			addToFrom();
			console.log();
			console.log("This is the last step");
			if (toCollege == false) {
				toCollege = " from ";
			} else {
				toCollege = " to ";
			}
			
			if (driver == "user") {
				driver = "I will drive";
				if (maxp > 1) {
					maxp = "I can take "+maxp+" more passengers <br>";
					} else {
					maxp = "I can take "+maxp+" more passenger <br>";
					}
					contact = contact[0].value;
					comment = comment[0].value;
			
			} else {
				driver = "I need a ride";
				maxp = "";
				contact = contact[1].value;
				comment = comment[1].value
			}
			
			$("#information").html($("#collegeName").val()+toCollege+$("#address").val()+"<br>"+
				driver+"<br>"+maxp+earlylate+" "+partofday+" "+month+" "+day+", "+year+"<br>"+contact+"<br>"+comment);    
		}

		});
	 	
  	});

$(function() {
	$("#eventForm").formwizard({ 
		formPluginEnabled: true,
	 	validationEnabled: true,
	 	focusFirstInput : true,
	 	formOptions :{
			success: function(data){$("#status").fadeTo(500,1,function(){ $(this).html("You just created a ride!").fadeTo(5000, 0);}),location.reload()}, 
			beforeSubmit: function(data){$("#data").html("data sent to the server: " + $.param(data));},
			dataType: 'json',
			resetForm: true
			}	
	 	});
  	});

function modalClose() {

		$.modal.close();

	}	

function nextClicked() {
	
	var step = $("#rideForm").formwizard("state").currentStep; 

	var html = $("#data").html();

	$("#data").html(html + "<br>" + step);

	//var driver = document.querySelector('input[name="driver"]:checked').value;
	var driver = $('#driver').find(":selected")[0]['value'];

	var driver2 = $("#user").html();

	if (driver == "user") {

		driver = "I am driving"		

	} else {

		driver = "I need a ride"

	}


	if (step == "summary") {


		$("#information").html("To: " + $("#to").val() + "<br>" + "From: " + $("#from").val() + 
			"<br>" + driver2 + "<br>");		

	}



}

function backClick() {

	var html = $("#data").html();

	$("#data").html(html + "<br>" + "Backward!");

}


function addToFrom() {

	
	var selected = document.querySelector('input[name="direction"]:checked').value;

	var html = $("#data").html();
	if (selected == "to_loc") {
		
		var to = $("#address").val();
		var from = $("#collegeName").val();		
		
		$("#toLuther").val("false");
		$("#to").val(to);
		$("#from").val(from);

	}

	if (selected == "from_loc") {

		var to = $("#collegeName").val();
		var from = $("#address").val();

		$("#toLuther").val("true");
		$("#to").val(to);
		$("#from").val(from);	

	}

	$("#data").html(html + "<br>" + "To: " + $("#to").val() + "<br>" + " From: " + $("#from").val());

}

function addDriver() {

	var selected = $('#driver').find(":selected")[0]['value'];
	var html = $("#data").html();
	if (selected == "user") {
		$("#isDriver").val('true');
	} 
	if (selected == "other") {
		$("#isDriver").val('false');
		$("#maxp").val = "3";
	}

}

function saveARide() {
		
	// populate vals object
	var vals = {}

	vals['lat'] = $("#lat").val();
	vals['lng'] = $("#lng").val();
		vals['from'] = $("#from").val();
		vals['to'] = $("#to").val();
		vals['maxp'] = $("#maxp").val();
		vals['contact'] = $("#contact").val();;
		vals['earlylate'] = $("#earlylate").val();
		vals['partofday'] = $("#partofday").val();
		vals['month'] =$("#month").val();
		vals['day'] = $("#day").val();
		vals['year'] = $("#year").val();
		vals['isDriver'] = $("#isDriver").val();
		vals['comment'] = $("#comment").val();
		vals['circleType']= $("#circleType").val();
		vals['toLuther'] = $("#toLuther").val();

	vals = JSON.stringify(vals);

	// pass 'stringified' vals to the requeststring after adding '=' and '&'
	
		var request = new XMLHttpRequest();

		var reqStr = '/newride?';

		for (var prop in vals) {
		reqStr += prop + "=" + vals[prop] + "&";
		}

		request.open("GET",reqStr,false);
		request.send(null);
		//clickListener = google.maps.event.addListener(map, "click", getAddress);
		if (request.status == 200) {
		initialize();
		} else {
		alert("An error occurred, check your responses and try again.");
		}

}

$(document).ready(function() {

	var $radios = $('input:radio[name=direction]');
    if($radios.is(':checked') === false) {
        $radios.filter('[value=from_loc]').prop('checked', true);
    }
	var today = new Date();

	var day = today.getDate();
	var month = today.getMonth()+1;
	var year = today.getFullYear();

	console.log(month,day,year);
    $(".month").val(month);
    $(".day").val(day);
    $(".year").val(year);
    
});

