$(document).ready(function() {
  var $body = $('body');
  var d = new Date();
  var month = d.getMonth();

  rotateActiveTab(month);

  // HOMEPAGE: initialize slick slider
  if ($('.slider').slick) {
    $('.slider-for').slick({
      infinite: true,
      speed: 500,
      fade: true,
      slidesToShow: 1,
      dots: true,
      autoplay: true,
      autoplaySpeed: 4000,
    });

    // slider thumbnails
    var $sliderThumb = $('.slider-thumb');

    $sliderThumb.click(function(e) {
      e.preventDefault();
      var slideIndex = $(this).index();
      $('.slider-for').slick('slickGoTo', parseInt(slideIndex));
    });

    // pause and play slider on thumbnails hover
    $sliderThumb.mouseenter(function(e) {
      $('.slider-for').slick('slickPause');
    }).mouseleave(function() {
      $('.slider-for').slick('slickPlay');
    });

    // add active class for the current slider thumbnail
    $('.slider-for').on('setPosition', function() {
      var currentSlide = $('.slider-for').slick('slickCurrentSlide') + 1;
      $sliderThumb.removeClass('active-slider');
      $('.slider-thumb:nth-child('+ currentSlide +')').addClass('active-slider');
    });
  }


  // Set timout for slider caption
  // to prevent the element from jumping when the page is laoding
  setTimeout(function() {
    $('.slider-caption, .slider-nav, .image-copyright').fadeIn(700);
  }, 200);

  // HOMEPAGE: align slider caption, pause button
  // and thumbnails to the main content area
  function getPageContainerPadding() {
    var cw = $(".content-container").width();
    var ww = $(window).width();
    var cwRight = (ww - cw) / 2;
    return cwRight;
  }

  var $slider = $('.slider');

  $('.slider-caption, .slider-nav').css('right', function() {
    return getPageContainerPadding() +  'px';
  });

  $('.image-copyright').css('left', function() {
    return getPageContainerPadding() +  'px';
  });

  // HOMEPAGE: Main area
  // Get the heighest div and make equal height on every boxes
  var windowWidth = $(window).width();
  var $mainBox = $('.main-box');
  var mainBoxMaxHeight = 0;

  $mainBox.each(function() {
    mainBoxMaxHeight = ($(this).outerHeight() > mainBoxMaxHeight) ? $(this).outerHeight() : mainBoxMaxHeight;
  });

  if (windowWidth >= 767) {
    $mainBox.css('height', mainBoxMaxHeight);
  } else {
    $mainBox.css('height', '');
  }

  // fire resize event after the browser window resizing it's completed
  var resizeTimer;
  $(window).resize(function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(doneResizing, 500);
  });

  function doneResizing() {
    $('.slider-caption, .slider-nav').css('right', function() {
      return getPageContainerPadding() +  'px';
    });

    $('.image-copyright').css('left', function() {
      return getPageContainerPadding() +  'px';
    });

    if ($(this).width() >= 767) {
      $mainBox.css('height', mainBoxMaxHeight);
    } else {
      $mainBox.css('height', '');
    }
  }

  // HOMEPAGE: Tabs functionality
  $('ul.nav-tabs a').click(function(e) {
    $(this).tab('show');
    // e.preventDefault();
  });

  $('.policies-nav a').hover(function() {
    $(this).tab('show');
  });

  var url = window.location.href;

  // Eu sector main page
  // /eu-adaptation-policy/sector-policies
  $('.policies-tile .nav-tabs a').click(function(e) {
    e.preventDefault();
    var href = $(this).attr('href');
    var href = href.substring(1);

    if (url.indexOf("index_html") > -1) {
      url = url.replace('index_html', href)
      document.location = url;
    } else {
      document.location = url + '/' + href;
    }
  });

  // Homepage policies section
  $('.policies-dynamic-area a').click(function(e) {
    e.preventDefault();
    var href = $(this).attr('href');
    var href = href.substring(1);

    document.location = url + '/eu-adaptation-policy/sector-policies/' + href;
  });

  // HOMEPAGE: Dynamic area:
  // on click center tab items on small screen sizes
  $('.main-nav-tabs li a').click(function() {
    var $parent = $(this).parent();
    centerTabItem($parent, '.main-nav-tabs');
  });

  function centerTabItem(target, outer) {
    var outer = $(outer);
    var target = $(target);
    var outerW = outer.width();
    var targetW = target.outerWidth(true);
    var targetIn = target.index();
    var q = 0;
    var centerElement = outer.find('li');

    for (var i = 0; i < targetIn; i++) {
      q += $(centerElement[i]).outerWidth(true);
    }

    outer.animate({
      scrollLeft: Math.max(0, q - (outerW - targetW) / 2)
    }, 500);
  }

  // HOMEPAGE: rotate active tabs depending on month
  function rotateActiveTab(month) {
    var monthR = month % 5;
    var $list = $('ul.main-nav-tabs');
    var item = $list.children('li')[monthR];
    if (item) {
      var $hrefs = $('a', item);
      $hrefs.length && $hrefs.tab('show');
    }
  }

  // HOMEPAGE: Dynamic area - Adaptation support tool:
  // Highlight steps on hover
  $('.dynamic-area .ast-step-wrapper').hover(function() {
    $(this).children('.ast-circle').css({
      'background-color': '#FFD554',
      'border': '2px solid #fff',
      'transform': 'scale(1.08)',
      'color': '#4F4F4F'
    });
    $(this).children('.step-text').css({
      'background-color': '#FFD554',
      'transform': 'scale(1.08)'
    });

    }, function() {
    $(this).children('.ast-circle').css({
      'background-color': '#8A9C3A',
      'border': '2px solid #fff',
      'transform': 'scale(1)',
      'color': '#fff'
    });
    $(this).children('.step-text').css({
      'background-color': '#f5f5f5',
      'transform': 'scale(1)'
    });
  });

  // Mobile menu button on click event
  $('.mobile-menu i').click(function() {
    $body.toggleClass('no-ovf');
    $(this).toggleClass('fa-bars fa-times');
    $('.header').toggleClass('mobile-header');
    $('.header .main-nav, .top-menu-content').toggleClass('nav-toggle');

    return false;
  });

  var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  if (isMobile) {
    // show submenu on click
    $('.main-nav-item').each(function() {
      var $this = $(this);
      var link = $this.find('.main-nav-link');

      if (!link.attr('href')) {

        $this.click(function() {
          link.parent().siblings('.sub-menu-wrapper').toggle();
          link.parent().parent().siblings().find('.sub-menu-wrapper').hide();
        });

      }
    });
  }


  // Mobile - hide header on scroll down
  var didScroll;
  var lastScrollTop = 0;
  var delta = 5;
  var navbarHeight = $('.top-menu').outerHeight();

  $(window).scroll(function(event) {
    didScroll = true;

    if (windowWidth <= 800) {
      if ($(window).scrollTop() >= 80) {
        $('.header').addClass('sticky-header');
      }
      else {
        $('.header').removeClass('sticky-header');
      }
    }
  });

  if (windowWidth <= 800) {
    setInterval(function() {
      if (didScroll) {
        hasScrolled();
        didScroll = false;
      }
    }, 250);
  }

  function hasScrolled() {
    var st = $(this).scrollTop();

    if (Math.abs(lastScrollTop - st) <= delta)
      return;

    if (st > lastScrollTop && st > navbarHeight) {
      // Scroll down
      $('.top-menu').removeClass('nav-down').addClass('nav-up');
    } else {
      // Scroll up
      if (st + $(window).height() < $(document).height()) {
        $('.top-menu').removeClass('nav-up').addClass('nav-down');
      }
    }
    lastScrollTop = st;
  }


  // Top menu login
  $('#user-name').click(function(e) {
    e.preventDefault();
  });

  // Navigation menu: align sub-menu to the right
  // if overflows the main navigation menu
  var mainMenuWidth = $('.main-nav-menu').width();

  $('.main-nav-menu li').mouseenter(function() {
    var $this = $(this);
    var subMenuWidth = $this.children('.sub-menu-wrapper').width();
    if ($this.find('.sub-menu-wrapper').length > 0) {
      var subMenuLeft = $this.children('.sub-menu-wrapper').offset().left;
    }

    if (mainMenuWidth - (subMenuWidth + subMenuLeft) < 0) {
      $this.children('.sub-menu-wrapper').css({
        'right': 0,
        'left': 'auto'
      });
    }
  });

  // Divide the sub-menu in 2 columns if 'sub-sub-menu' exist
  // var navigationItem = $('.main-nav-item');
  // navigationItem.each(function() {
  //   var $this = $(this);
  //   if ($this.find('.sub-sub-menu-wrapper').length > 0) {
  //     var submenuwrapper = $this.find('.sub-menu-wrapper');
  //     var submenucols = submenuwrapper.find(".sub-menu").length > 1 ? submenuwrapper.find(".sub-menu").length : 2;
  //     submenuwrapper.css({
  //       'column-count': submenucols,
  //       '-webkit-column-count' : submenucols,
  //       '-moz-column-count': submenucols,
  //     });
  //   }
  // });

  // GENERAL
  // Add table class
  $('.CSSTableGenerator').addClass('listing');

  // add button class
  $('#document-action-download_pdf,' +
    '#login-form .formControls input,' +
    '#folderlisting-main-table .context').addClass('standard-button secondary-button');

  var $blueButton = $('.bluebutton');
  $blueButton.addClass('standard-button primary-button');
  $blueButton.parent().css('text-align', 'left');

  // add button classes for form buttons
  var $submitButton = $('input[type=submit]');
  $submitButton.each(function () {
    var $this = $(this);
    if ($this.val().match(/^(Save|Activate|Deactivate|Update subscriptions|Apply Changes)$/i)) {
      $this.addClass('standard-button primary-button');
    } else if ($this.val() === 'Cancel') {
      $this.addClass('standard-button secondary-button');
    } else {
      $this.addClass('standard-button secondary-button');
    }
  });

  $('select').addClass('form-control');

  // hide rss feed link
  $('#document-action-rss').parent().hide();

  // Add active class on sub-navigation active items
  // special transnational subpages, ex:
  // url: .../cca/countries-regions/transnational-regions/baltic-sea-region/adaptation/policy-framework
  // help page: share your information subpages, ex:
  // url: .../cca/help/share-your-info/publications-and-reports
  var current = window.location.href;
  $('.share-info-wrapper #third-level-menu a, .cover-section_nav-tile a, .uvmb-nav a').each(function() {
    var $this = $(this);
    if (current.indexOf($this.attr('href')) > -1 || $this.attr('href').indexOf(current) > -1) {
      $this.addClass('active-nav');
    }
  });

  // Add a specific class for grid layout pages
  var currentLocation = window.location.pathname;

  var isPolicyPage = $('.subsection-sector-policies').length > 0;
  var isASTPage = $('.subsection-tools-adaptation-support-tool').length > 0;

  // EU SECTOR POLICIES
  // url: .../cca/eu-adaptation-policy/sector-policies/agriculture
  if (isPolicyPage) {
    var policySubTitles = $('.read_more_second').children('h2');
    policySubTitles.each(function() {
      $(this).replaceWith($('<p><strong>' + this.innerHTML + '</strong><p>'));
    });

    // move eu sector policy factsheet
    var $sidebar = $('.column.col-md-3');
    $sidebar.before($sidebar.find('.factsheet-pdf').parent());
    $('.factsheet-pdf').parent().css('text-decoration', 'none');
  }

  // TRANSNATIONAL SUBPAGES (two specific subpages)
  // move detailed content under the sidebar (baltic sea, central europe)
  var $sidebar = $('.subsection-transnational-regions .column.col-md-3');
  $sidebar.after($sidebar.find('.detailed-content').parentsUntil('.tile-default'));

  // COUNTRY PAGES
  // url: .../cca/countries-regions/countries/austria
  $('.country-header').closest('#content').addClass('country-profile-content');
  $('.country-select-tile').closest('.row').css('margin', '0');
  $('.country-profile-content .sweet-tabs').attr('id', 'country-tab');

  // custom country dropdown functionality
  var $countryTitle = $('.dd-country-title');
  $('.dd-country-title .options li').on('click', function() {
    $countryTitle.find('.selected').html($(this).text());
    $countryTitle.find('.selected-inp').val($(this).data('value')).trigger('change');
    $countryTitle.find('.options').removeClass('show');
  });

  $('.dd-title-wrapper').on('click', function(e) {
    $countryTitle.find('.options').fadeToggle().toggleClass('show');
    $countryTitle.find('i').toggleClass('fa fa-angle-up fa fa-angle-down');
    e.stopPropagation();
  });

  $('.dd-country-title .selected-inp').on('change', function(ev) {
    var url = ev.target.value;
    var country = $(".dd-country-title li[data-value='" + url + "']").text().replace(' ', '-');

    if (country.length) {
      document.location = '/countries/' + country.toLowerCase();
    }
  });

  // resize the country dropdown list to the country title
  $.fn.resizeselectList = function(settings) {
    return this.each(function() {
      $(this).change(function() {
        var $this = $(this);
        var $selected = $this.parents().find('.dd-country-title .selected');
        var text = $selected.text();

        var $titlePlaceholder = $('<span/>').html(text).css({
          'font-size': $selected.css('font-size'),
          'font-weight': $selected.css('font-weight'),
          'visibility': 'hidden'
        });

        $titlePlaceholder.appendTo($this.parent());
        // get country title width
        var width = $titlePlaceholder.width();
        $titlePlaceholder.remove();

        $this.width(width + 45);
      }).change();
    });
  };
  $('.resizeselect-list').resizeselectList();


  // ADAPTATION SUPPORT TOOL
  // url: .../cca/knowledge/tools/adaptation-support-tool
  function astLayout() {

    if (isASTPage) {
      $('.col-md-8').children('.tile:nth-child(2)').addClass('tile-wrapper');

      var titleAST = $('.tile-content').children('h1');
      titleAST.each(function() {
        $('<h2>' + $(this).html() + '</h2>').replaceAll(this);
      });

      $('.cover-richtext-tile ul li a').attr('target', '_blank');
    }

    var $circleStep = $('.ast-map .ast-circle');
    $circleStep.hover(function() {
      $(this).siblings('.step-text').css('display', 'block');
    }, function() {
      $(this).siblings('.step-text').css('display', 'none');
    });

    var currentStep = $('.ast-title-step').text();
    if (currentStep == 0) {
      $('.ast-title-step').remove();
    }

    // highlight the current step
    $circleStep.each(function() {
      if ($(this).text() === currentStep) {
        $(this).css({
          'background-color': '#FFD554',
          'border': '2px solid #F2C94C',
          'color': '#4F4F4F',
          'font-family': 'OpenSansB'
        });
      }
    });
  }

  astLayout();

  // Fix floating button
  $('.share-your-info-ace-button').wrapAll('<div class="clearfix"/>');

  if (windowWidth <= 800) {
    $('#main-nav-item-3').children('.sub-menu-wrapper').append($('<div class="mobile-clearfix"/>'));
  }

  // Add a placeholder message for search input fields
  $('#search-field input[type="text"]').attr('placeholder', 'type here...');

  var $h2 = $('.subsection-tools-urban-ast h2');
  $h2.each(function() {
    if ($(this).text().indexOf('Example cases:') >= 0) {
      $(this).addClass('example-cases');
    }
  });

  // Open all links out of the tool in a new window
  var isUrbanAST = $('.subsection-tools-urban-ast').length > 0;
  if (isUrbanAST) {
    $('.cover-richtext-tile ul li a').attr('target', '_blank');
  }

  // Move PDF button in the content area
  var $pdfButton = $('#document-action-download_pdf');
  $pdfButton.parent().wrapAll('<div class="documentExportActions"/>');
  var $pdfExport = $('.documentExportActions');
  var $isColumnedPage = $('.content-column').length > 0;
  var isCountryProfile = $('.country-header').length > 0;

  if ($isColumnedPage) {
    $('.content-column').append($pdfExport);
  } else if (isCountryProfile) {
    $('.tab-content').append($pdfExport);
    $pdfExport.css({
      'float':'none',
      'display': 'inline-block'
    });
  } else {
    $('#content').append($pdfExport);
    $pdfExport.css({
      'float':'none',
      'display': 'inline-block'
    });
  }

  // Urban AST export section pdf button
  if (currentLocation.indexOf('/tools/urban-ast') !== -1 && currentLocation.indexOf('pdf.body') === -1) {
    var path = window.location.pathname.split('/');
    path.pop();
    path = path.join('/') + '/ast.pdf'
    var $sectionPDF = '<a href="{0}" ' +
    'class="standard-button ast-section-pdf">' +
    'Download section as PDF</a>';
    $sectionPDF = $sectionPDF.replace("{0}", path)
    $pdfButton.parent().before($sectionPDF);
  }

  // AST export section pdf button
  if (currentLocation.indexOf('/tools/adaptation-support-tool') !== -1 && currentLocation.indexOf('pdf.body') === -1) {
    var path = window.location.pathname.split('/');
    path.pop();
    path = path.join('/') + '/ast.pdf'
    var $sectionPDF = '<a href="{0}" ' +
    'class="standard-button ast-section-pdf">' +
    'Download section as PDF</a>';
    $sectionPDF = $sectionPDF.replace("{0}", path)
    $pdfButton.parent().before($sectionPDF);
  }

  // Fix tiles
  $('.tile-container').each(function() {
    var $this = $(this);
    var editbtn = $this.children('a');
    var contentWrapper = $this.children('div');
    if (editbtn.text() == 'Edit') {
      editbtn.detach().appendTo(contentWrapper);
    }
  });

  $('.template-compose .tile').each(function() {
    var $this = $(this);
    if ($this.hasClass('col-md-4')) {
     $this.removeClass('col-md-4');
     $this.parent('.tile-container').addClass('col-md-4');
    }
    else if ($this.hasClass('col-md-6')) {
     $this.removeClass('col-md-6');
     $this.parent('.tile-container').addClass('col-md-6');
    }
  });

  $('.col-md-6, .col-md-4').each(function() {
    var $this = $(this);

    $this.find('.cover-richtext-tile').children('h2').addClass('richtext-tile-title');
    $('.richtext-tile-title').parent().css('padding', '0 .5em');
  });

  // Accordion: Toggle arrow up and down on click
  var $panelTitle = $('.panel-title a');

  $panelTitle.addClass('arrow-down');
  $panelTitle.click(function() {
    $(this).toggleClass('arrow-up arrow-down');
  });

  // Custom accordion with faded text
  $('.tile').each(function() {
    var $this = $(this);
    if (!$this.hasClass('classic-accordion')) {
      $this.find('.panel-default').closest('.cover-richtext-tile').addClass('custom-accordion');
    }
  });

  var $customAccordion = $('.custom-accordion');
  var $panelHeading = $customAccordion.find('.panel-heading');
  var $panelCollapse = $customAccordion.find('.panel-collapse');
  var $panelDefault = $customAccordion.find('.panel-default');

  $panelTitle.click(function() {
    var $this = $(this);
    if ($this.text() === "Read more") {
      $this.text("Read less")
    } else if ($this.text() === "Read less") {
      $this.text("Read more")
    }
    // $(this).text(function(i, text) {
    //   return text === "Read more" ? "Read less" : "Read more";
    // })
  });

  $panelCollapse.css({
    'display': 'block',
    'height': '100px',
    'overflow': 'hidden',
    'position': 'relative'
  });

  $panelHeading.css('text-align', 'right');

  var $panelLayer = $('<div class="panel-layer fadein"/>');
  $panelCollapse.prepend($panelLayer);

  $panelDefault.each(function() {
    var panelTitle = $('.panel-title a', this);
    var panelCollapse = $('.panel-collapse', this);
    var panelLayer = $('.panel-layer', this);
    $('.panel-heading', this).before(panelCollapse);

    panelTitle.toggle(
      function() {
        panelCollapse.addClass('panel-opened');
        panelLayer.removeClass('fadein').addClass('fadeout');
      }, function() {
        panelCollapse.removeClass('panel-opened');
        panelLayer.removeClass('fadeout').addClass('fadein');
      }
    );
  });

  // Hide the download pdf on the search page
  if (window.location.href.indexOf("data-and-downloads") > -1) {
    $pdfButton.parent().hide();
  }

  // Move interactive maps under the sidebar
  // eg. ../cca/knowledge/adaptation-information/observations-and-scenarios
  var $mapView = $('.speedbutton');
  if ($mapView.length > 0) {
    var $sidebar = $('.col-md-3.content-sidebar');
    var $mapViewParent = $mapView.closest('.tile-default').addClass('interactive-map-wrapper');
    var $mapViewParentSibling = $mapViewParent.prev().addClass('map-list-wrapper');
    $('.interactive-map-wrapper, .map-list-wrapper').wrapAll('<div class="interactive-maps" />')
    var $mapWrapper = $('.interactive-maps');
    $sidebar.after($sidebar.find($mapWrapper));
  }

  // CASE STUDIES - DATABASE ITEM
  // Make the first photo of gallery visible
  var $links = $('#links');
  $links.children('.gallery-hide').eq(0).css('display', 'block');

  $(document).keyup(function(e) {
    if (e.keyCode === 27) {
      // get the maximum number of slices
      var nr_of_slices = $links.children('.gallery-hide').length;
      $links.children('.gallery-hide').slice(1, nr_of_slices).css('display', 'none');
    }
  });

  // Display events for gallery close
  $('#blueimp-gallery').on('click', function(event) {
    if (event.target.className == "slide " ||
      event.target.className == "close"  ||
      event.target.className == "slide") {
      // get the maximum number of slices
      var nr_of_slices = $('#links').children('.gallery-hide').length
      $('#links').children('.gallery-hide').slice(1, nr_of_slices).css('display', 'none');
    }
  });

  // remove inline styles
  $('.ace-content-column p,' +
   '.ace-content-column ul,' +
   '.ace-content-column li' +
   '.column p').removeAttr('style');

  // move case studies gallery
  var $aceSidebar = $('.aceitem_page .col-md-3');
  $aceSidebar.before($aceSidebar.find('.case-studies-illustrations'));
  $aceSidebar.before($aceSidebar.find('.sidebar_files'));

  // HELP: Use cases
  // use the table last column data as a tooltip on hover on each case;
  // this last column is not visible for the visitor,
  // only visible for the editors on compose/edit section
  var $tr = $('.use-cases-listing tbody tr');
  $tr.each(function() {
    var $this = $(this);
    var useCaseTitle = $this.find('td:last-child').text();
    $this.find('td:first-child').append($('<span class="use-case-tooltip"/>'));
    $this.find('.use-case-tooltip').text(useCaseTitle);
  });

  $('.use-cases-listing tr td:nth-child(2)').hover(function() {
    $(this).siblings().find('.use-case-tooltip').css('display', 'block');
  }, function() {
    $(this).siblings().find('.use-case-tooltip').css('display', 'none');
  });

  // Show subnational regions on checkbox click
  $("input[type='checkbox']").on('click', function(){
    var faja = $(this).parents('.subnationals-checkbox-ul');
    if (faja[0]) {
      if (this.checked) {
        $('#subnationals').children().each(function(index, domObject){
          var cc = $(this).val();
          if(domObject.text.indexOf(cc) !== -1) {
            $(domObject).show();
          }
        }.bind(this));
      }
      else {
        $('#subnationals').children().each(function(index, domObject){
          var cc = $(this).val();
          if(domObject.text.indexOf(cc) !== -1) {
            $(domObject).hide();
          }
        }.bind(this));
      }
    }
  });

  // Hide empty tiles
  var $tile = $('.tile');
  $tile.each(function() {
    $this = $(this);
    if ($this.children().length === 0) {
      $this.hide();
    }
  });

  // Open external links in new tab
  $('a').each(function() {
    var $this = $(this);
    var notHeaderLink = $this.parents('.header').length == 0;
    if (notHeaderLink) {
      var a = new RegExp('/' + window.location.host + '/');
      if (!a.test(this.href)) {
        $this.attr('target', '_blank');
      }
    }
  });

  // Fix image map links on UAST pages
  var imageMapArea = $('#uast-image-map').children('area');
  imageMapArea.each(function() {
    this.href = this.href.replace('/tools', '/knowledge/tools');
  });

  $('.acecontent_filtering_tile select').on('change', function(event){
    $(this).parents('form').submit();
  });

  // Remove main navigation subitems hover state
  // if doesn't have href attribute
  $('.sub-menu-link').each(function() {
    var $this = $(this);
    if(!$this.attr('href')) {
      $this.hover(function() {
        $this.css('color', '#3a3a3a');
      });
      $this.css('color', '#3a3a3a');
    }
  });

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

});
