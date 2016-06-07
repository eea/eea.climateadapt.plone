(function($){
	$(document).ready(function(){

        $(".show_key_objects").on('click', function(event){
			// gets the keyword in order to pass it on to the request
            var form_key = $(this).parents('tr').children('td')[0].innerText;

			// get the div where the links will be inserted
			var obj_div = $(this).siblings('div');

			// check if the element was clicked before so that
			// we do the ajax load only once
			if($(this).data('clicked') == true) {
			}
			else {
				$.ajax({
	                url: '/keyword-objects?keyword=' + form_key,
	                dataType: "json",
	                success: function(data){
						datastring = data.join('\n');
						obj_div.append(datastring);
					}
	            })
			}

			// adds class to accordion
			this.classList.toggle("active");
	        this.nextElementSibling.classList.toggle("show");

			// flag for click
			$(this).data('clicked', true);

			// changes text per click
			$(this).text(function (a,b) {
				return (b == "Show" ? "Hide" : "Show");
			});
        });
    });
})(jQuery);
