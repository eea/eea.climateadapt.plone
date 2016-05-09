//All JQuery stuff after this point

$(document).ready(function(){

	//New image for search button in the header
	$('#searchbox input[type="image"]').attr('src', "/ace-theme/images/vergrootglas.png");
	//Searchbox keyword name attribute changed to search portlet specific "_77_"
	$('#searchbox #keywords').attr('name', '_77_keywords');

	//Several classes for the main menu
	$("ul li:first-child").addClass("first");
    $("ul li:last-child").addClass("last");
    $('li').has('ul').addClass('submenu');

    //Elements for the db search speedbutton on the frontpage
    $(".db-search-fp img").attr("src","/ace-theme/images/vergroot_blauw.png");
    $('.db-search-fp .portlet-body').prepend('<p id="db-search-fp-info-text">Search the <span style="font-size:15px">database</span></p>');
    $('.db-search-fp .portlet-body').prepend('<a id="db-search-fp-link" href="/data-and-downloads"></a>');

    //Fixes to main and sec. menu
    if ($("#sec-menu ul").length == 0){
    	  $("#navigation .selected a").css({"background":"none","border":"none", "margin-top":"0"});
    	  $("#topnav").css({"border-bottom":"1px solid #a5bf26"});
    	  $("ul#topnav li.selected a").css({"color":"#FFF"});
    }

    //Add a bottom line to the search results windows on the Search and Discover page
    $(".search-discover .resultlist:last-child").css({"border-bottom":"2px solid #d7e3ef"});

    //Set equal heights to columns on various pages
    setEqualHeight($(".detailleft, .detailright")); //Ace detail pages
    setEqualHeight($(".ace_layout_3 #layout-column_column-2, .ace_layout_3 #layout-column_column-3, .ace_layout_3 #layout-column_column-4")); //Sector pages
    setEqualHeight($(".frontpage-layout #layout-column_column-4, .frontpage-layout #layout-column_column-5, .frontpage-layout #layout-column_column-6, .frontpage-layout #layout-column_column-7")); //frontpage
    setEqualHeight($(".ast #layout-column_column-3, .ast #layout-column_column-4")); //AST
    setEqualHeight($(".faq #layout-column_column-2, .faq #layout-column_column-3, .faq #layout-column_column-4")); //FAQ and Mapviewer

    //Search button on the portlet web content search page
    $('.portlet-journal-content-search .portlet-body input[type="image"]').attr("src","/ace-theme/images/vergroot_blauw.png");

    //Search button on the portlet web content search page
    $('.portlet-journal-content-search .col-3 a').css("font-size","11px");

});


//Add tooltips to glossary terms
$(document).ready(function()
		{
		   // Make sure to only match links to the glossary
		   $('a[href*="glossary#link"]').each(function()
		   {

			   var url = $(this).attr('href');
			   var thisLinkTerm = url.substring(url.indexOf("#")+1);

			   //add glossary CSS class
			   $(this).addClass("glossary-inline-term");

			  // We make use of the .each() loop to gain access to each element via the "this" keyword...
		      $(this).qtip(
		      {
		         content: {
		            // Set the text to a message you want to use
		            text: '<p>Loading glossary term...</p>',
		            ajax: {
		               url: $(this).attr('href'), // Use the href attribute of each element for the url to load
		               cache: false,
		               dataType: "html",
		               success: function(data){
		                  html = data;
		                  //alert(thisLinkTerm);
		                  var htmlFiltered = $(html).find("#" + thisLinkTerm);
		                  this.set('content.text', htmlFiltered);
		               }
		            },
		            title: {
		               text: $(this).text() // Give the tooltip a title using each elements text
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
		      });
		   })

		   // Make sure it doesn't follow the link when we click it
		   //.click(function(event) { event.preventDefault(); });
		});

function setEqualHeight(columns){
	var tallestcolumn = 0;
	columns.each(
		function(){
			currentHeight = $(this).height();
				if(currentHeight > tallestcolumn){
					tallestcolumn  = currentHeight;
				}
		}
	);
	columns.css("min-height", tallestcolumn);
}
