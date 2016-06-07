(function($){
	$(document).ready(function(){

        $(".show_key_objects").on('click', function(event){
			// gets the keyword in order to pass it on to the request
            var form_key = $(this).parents('tr').children('td')[0].innerText;

			// get the div where the links will be inserted
			var obj_div = $(this).siblings('.keyword_objects');

			// check if the element was clicked before so that
			// we do the ajax load only once
			if($(this).data('clicked') == true) {
			}
			else {
				$.ajax({
	                url: '/keyword-objects?keyword=' + form_key,
	                dataType: "json",
	                success: function(data){
						// add newlink after links
						datastring = data.join('\n');

						// Linkify http/https/ftp
						replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
						replacedText = datastring.replace(replacePattern1, '<a href="$1" target="_blank">$1</a>');

						// Add content to div
						obj_div.append(replacedText);
					}
	            })
			}

			// adds class to accordion
			this.classList.toggle("active");
	        this.nextElementSibling.classList.toggle("show");

			// flag for click
			$(this).data('clicked', true);
        });
    });
})(jQuery);
