(function($){
	$(document).ready(function(){
		setTimeout(function(){
			$("#form-widgets-websites-buttons-add").on('click', function(event){
				window.location.hash = "form-widgets-websites-buttons-add";
				window.location.hash = "form-widgets-websites-buttons-add";
			});
		},100);

		setTimeout(function(){
			$("#form-widgets-websites-buttons-remove").on('click', function(event){
				window.location.hash = "form-widgets-websites-buttons-remove";
				window.location.hash = "form-widgets-websites-buttons-remove";
			});
		},100);

		$('.tile-container').each(function(){
			var span = $(this).find('.tile-type-name');
			var editbtn = $(this).children('a');
			var div = $(this).children('div');
			if (span.text() == 'Relevant AceContent') {
				span.detach().appendTo(div);
			}
			if (editbtn.text() == 'Edit') {
				editbtn.detach().appendTo(div);
			}
		});

        $(".acecontent_filtering_tile select").on('change', function(event){
            $(this).parents('form').submit();
        });

		$('ul.dropdown-menu [data-toggle=dropdown]').on('click', function(event) {
			event.preventDefault();
			event.stopPropagation();
			$(this).parent().siblings().removeClass('open');
			$(this).parent().toggleClass('open');
		});
        $('.faceted-left-column').each(function(){
            var left_column = $(this);
            left_column.find('.faceted-widget').each(function(){
                var wid = $(this);
                wid.find('legend').each(function(){
                    var text = $(this).text();
                    var handle = $('<a>');
                    handle.attr('class', 'case-studies-database-search-filters-section-header searchpage-column-accordion-handle');
                    handle.attr('href', '#');
                    handle.text(text);
                    var simbol = $('<span>');
                    simbol.attr('class','case-studies-database-search-filters-section-header-icon');
                    simbol.text('+');
                    handle.append(simbol);
                    $(this).replaceWith(handle);
                });
                wid.find('.searchpage-column-accordion-handle').on('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    var wid = $(this).closest('.faceted-widget');
                    wid.find("form").toggle(400);
                    wid.find(".faceted-operator").toggle();
                    $(this).toggleClass('collapsed');
                    if ($(this).hasClass('collapsed')){
                        $(this).find('span').text('-');
                    } else {
                        $(this).find('span').text('+');
                    }
                });
            });
            left_column.find('.faceted-searchpagecheckbox-widget').each(function(){
                var wid = $(this);
                wid.find('.searchpageoperator input[type="radio"]').on('change', function(event){
                    var action = $(this).val();
                    var form = $(this).closest('form');
                    var wid = $(this).closest('.faceted-widget');
                    var wid_id = wid.attr('id').split('_')[0];
                    if (action === 'display'){
                        form.find('ul').show();
                    } else {
                        form.find('ul').hide();
                        Faceted.Widgets[wid_id].reset();
                        Faceted.Widgets[wid_id].do_query();
                    }
                });
                wid.find('form ul input[type="checkbox"]:checked').each(function(event){
                    var form = $(this).closest('form');
                    form.find('.searchpageoperator input[type="radio"][value="display"]').click();
                    wid.find('.searchpage-column-accordion-handle').click();
                });
            });
        });

		// Check all accordions on the page, add class where necessary
		var selector = $(".panel-title a");
		$(selector).each(function(index) {
			if($(this).text().toLowerCase().indexOf("read more") > -1 || $(this).text().toLowerCase().indexOf("read less") > -1) {
				$(this).parents("div.panel-heading").removeClass('edit-tool-custom-click');
				$(this).parents("div.panel-heading").addClass('edit-tool-custom-click');
				$(this).parents("h4.panel-title").removeClass('read-more-acc');
				$(this).parents("h4.panel-title").addClass('read-more-acc');
				$(this).parents("div.tile-default").removeClass('readmore-overflow');
				$(this).parents("div.tile-default").addClass('readmore-overflow');
			}
		});

		// Add classes to arccodion
		$('.panel-title a').click(function(){
			if ($(this).text().toLowerCase().indexOf("read more") > -1 || $(this).text().toLowerCase().indexOf("read less") > -1) {
			 	var acc_parent = $(this).parents("div.panel-default");
				$(acc_parent).children().eq(1).removeClass('edit-tool-custom');
				$(acc_parent).children().eq(1).addClass('edit-tool-custom');
				$(this).removeClass('read-more-class');
				$(this).addClass('read-more-class');
				$(this).text(function (a,b) {
					return (b == "Read more" ? "Read less" : "Read more");
				});
			}
		});
		// Year defaults for faceted
		var range_click = $(".faceted-range-widget").children().children();

		$(range_click).click(function() {
			$('#year-start-input').val(0);
			$('#year-end-input').val(9999);
		});

		// Make the first photo of gallery visible
		$('#links').children('.gallery-hide').eq(0).css('display', 'block');

		// Display event for gallery open
		$('#links').on('click', function(event) {
			$(this).children('.gallery-hide').css('display', 'block');
		});

		// Display events for gallery close
		$('#blueimp-gallery').on('click', function(event) {
			if(event.target.className == "slide " ||
			   event.target.className == "close"  ||
		   	   event.target.className == "slide") {
				$('#links').children('.gallery-hide').slice(1, 4).css('display', 'none');
			}
		});

		$(document).keyup(function(e) {
			if (e.keyCode === 27) {
				$('#links').children('.gallery-hide').slice(1, 4).css('display', 'none');
			}
		});

		// Initialize blueimp gallery
		if (document.getElementById('links') != null) {
			document.getElementById('links').onclick = function (event) {
			  event = event || window.event;
			  var target = event.target || event.srcElement,
			    link = target.src ? target.parentNode : target,
			    options = {
			      index: link, event: event,
			      onslide: function (index, slide) {

			        self = this;
			        var initializeAdditional = function (index, data, klass, self) {
			          var text = self.list[index].getAttribute(data),
			            node = self.container.find(klass);
			          node.empty();
			          if (text) {
			            node[0].appendChild(document.createTextNode(text));
			          }
			        };
			        initializeAdditional(index, 'data-description', '.description', self);
			      }
			    },
			    links = this.getElementsByTagName('a');
			  blueimp.Gallery(links, options);
			};
		}
	});

//Add tooltips to glossary terms
$(document).ready(function() {
            function qtip2Initializer() {
        // Make sure to only match links to the glossary
		$('a[href*="glossary#link"]').each(function() {
                    var that = this;

        		var url = $(this).attr('href');

        		var thisLinkTerm = url.substring(url.indexOf("#")+1);

        		//add glossary CSS class
        		$(this).addClass("glossary-inline-term");

                        // Your logic to execute when qTip2 is available
        	        // We make use of the .each() loop to gain access to each element via the "this" keyword...
        		$(that).qtip({
        		    content: {
                                text: function(event, api) {
                                    var thatText = $(that).text();

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
                                    return '<div class="GlossaryTitle">' + thatText.charAt(0).toUpperCase() + thatText.slice(1) + '</div><p>Loading glossary term...</p>'; // Set some initial text
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

                if(window.require && window.requirejs) {
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
	var bannerTimer = setTimeout(transitionSlides, 200);
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
			bannerTimer = setTimeout(transitionSlides, 5000);
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
