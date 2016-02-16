(function($){
	$(document).ready(function(){
		$('ul.dropdown-menu [data-toggle=dropdown]').on('click', function(event) {
			event.preventDefault(); 
			event.stopPropagation(); 
			$(this).parent().siblings().removeClass('open');
			$(this).parent().toggleClass('open');
		});
	});

//Add tooltips to glossary terms
$(document).ready(function() {
            function qtip2Initializer() {
                // Make sure to only match links to the glossary
		$('a[href*="glossary#link"]').each(function() {
                    var that = this;
    			  
                        console.log("Link", this);
        		var url = $(this).attr('href');
                                              
        		var thisLinkTerm = url.substring(url.indexOf("#")+1);
        			   
        		//add glossary CSS class
        		$(this).addClass("glossary-inline-term");

                        // Your logic to execute when qTip2 is available
        	        // We make use of the .each() loop to gain access to each element via the "this" keyword...
        		$(that).qtip({
        		    content: {
                                text: function(event, api) {
                                    $.ajax({
                                        // url: element.data('url') // Use data-url attribute for the URL
                                        url: $(that).attr('href')
                                    })
                                    .then(function(content) {
                                        // Set the tooltip content upon successful retrieval
        		                var htmlFiltered = $(content).find("#" + thisLinkTerm);
                                        api.set('content.text', htmlFiltered);
                                    }, function(xhr, status, error) {
                                        // Upon failure... set the tooltip content to the status and error value
                                        api.set('content.text', status + ': ' + error);
                                    });
                                    return 'Loading...'; // Set some initial text
                                }
        		     },
        		     position: {
        		        at: 'bottom center', // Position the tooltip above the link
        		        my: 'top center',
        		        viewport: $(window), // Keep the tooltip on-screen at all times
        		        effect: false // Disable positioning animation
        		     },
        		     show: {
        		        event: 'mouseenter',
        		        solo: true // Only show one tooltip at a time
        		     },
        		     hide: {
        		        event: 'mouseleave'
        		     },
        		     style: {
        		        classes: 'ui-tooltip-blue ui-tooltip-shadow ui-tooltip-rounded'
        		     }
        		});   // END qtip
        			  
                });
            }

                if(window.require) {
                    requirejs.config({
                        paths: {
                            // You may also need to tell set the jquery path, as some sites (like BBC) use a different name!
                            qtip2: '//cdnjs.cloudflare.com/ajax/libs/qtip2/2.2.1/jquery.qtip.min'
                        }
                    });
                    requirejs(['qtip2'], qtip2Initializer); // Load it using RequireJS, and execute the qtip2 logic
                }

    		 
    		   // Make sure it doesn't follow the link when we click it
    		   //.click(function(event) { event.preventDefault(); });
		});




})(jQuery);



// homepage carousel
//
$(document).ready(function() {
	$('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-content ul.blank').children().each(function(index,value){
		
		if ( $(this).hasClass('active') ) {
			$('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-controls').find('ul').append('<li class="active">' + (index+1) + '</li>');
		
		} else {
			$('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-controls').find('ul').append('<li>' + (index+1) + '</li>');
		}

		if ( $('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-content ul.blank').children().length == (index+1) ) {
			initHomepageSliderControls();
		}
	});
	
	var numBanners = $('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-content ul.blank').children().length; 	
	var activeIndex=1;
	var fadeOutSpeed = 200;
	var fadeInSpeed = 200;
	var bannerTimer = setTimeout(transitionSlides, 20000);
	
	function transitionSlides(){
		var currentSlide = $('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-content ul.blank>li:nth-child(' + activeIndex + ')');
		var currentToggle = $('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-controls ul>li:nth-child(' + activeIndex + ')');	
		if(activeIndex+1 > numBanners){
			activeIndex=1;
		}
		else{
			activeIndex++;
		}
		var nextSlide = $('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-content ul.blank>li:nth-child(' + activeIndex + ')');
		var nextToggle = $('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-controls ul>li:nth-child(' + activeIndex + ')');
		$(currentSlide).fadeOut(fadeOutSpeed, function() {
			$(currentSlide).removeClass('active');
			$(currentToggle).removeClass('active');
		});
		$(nextSlide).fadeIn(fadeInSpeed, function() {
			$(nextSlide).addClass('active');
			$(nextToggle).addClass('active');
			bannerTimer = setTimeout(transitionSlides, 20000);
		});
	}	
			
	function transition (that){
		if ( !$(that).hasClass('active')  ) {			
			$('#case-studies-homepage-slider-wrapper>.case-studies-homepage-slider-content>ul>li.active').fadeOut(fadeOutSpeed, function() {
				$('#case-studies-homepage-slider-wrapper>.case-studies-homepage-slider-content>ul>li.active').removeClass('active');
				$('#case-studies-homepage-slider-wrapper>.case-studies-homepage-slider-controls>ul>li.active').removeClass('active');
			});
			$('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-content ul').children().eq( $(that).index() ).fadeIn(fadeInSpeed, function() {
				$('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-content ul').children().eq( $(that).index() ).addClass('active');
				$('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-controls ul').children().eq( $(that).index() ).addClass('active');
			});
		}
	}
	
	function initHomepageSliderControls() {
		$('#case-studies-homepage-slider-wrapper .case-studies-homepage-slider-controls ul').children().each(function() {
				$(this).click(function() {
					transition(this);
					clearTimeout(bannerTimer);
				});
			});
		}
});

