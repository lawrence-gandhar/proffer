
(function($) {
    'use strict';
    $(document).ready(function() {
        
		// Multi Select 
		
		// Permission Location
		
		$( "select#id_location" ).change(function(){
			
			if( $('#id_location :selected').length > 0){
				var selectednumbers = [];
				$('#id_location :selected').each(function(i, selected) {
					selectednumbers[i] = $(selected).val();
				});
				
				
				$.post("/location-select/",
					{
					'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(), 
					'selectednumbers':JSON.stringify(selectednumbers),
					'id_user':$("select#id_user :selected").val()
					},
					function(data){
						
						var html_s = '';
						
						$.each($.parseJSON(data), function(i,v){
							
							var selected = "";
							if(v.selected == '1') selected = "selected";
							
							html_s += '<option value="'+v.id+'"'+selected+'>'+v.ipaddress+' - '+v.location_name+'</option>';
						});
						
						$("select#id_server").empty().append(html_s);
					}
				);
			}			
		}).change();
		
    });
})(django.jQuery);

