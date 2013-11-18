$(function() {
	$("#rideForm").formwizard({ 
		formPluginEnabled: true,
	 	validationEnabled: true,
	 	focusFirstInput : true,
	 	formOptions :{
			success: function(data){$("#status").fadeTo(500,1,function(){ $(this).html("You just created a ride!").fadeTo(5000, 0);})}, 
			beforeSubmit: function(data){
				//$("#data").html("data sent to the server: " + $.param(data));
				$("#to").html("DID THIS WORK?");
				},
			dataType: 'json',
			resetForm: true
			}	
	 	});
  	});


/////////////////////////////////////////////////////


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
