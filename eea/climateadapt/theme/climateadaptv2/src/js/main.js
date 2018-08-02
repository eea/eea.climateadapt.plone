$(document).ready(function() {
  // HOMEPAGE: initialize slick slider
  if ($('.slider').slick) {
    $('.slider').slick({
      infinite: true,
      speed: 500,
      fade: true,
      slidesToShow: 1,
      dots:  true,
      autoplay: true,
      autoplaySpeed: 4000
    });
  }

  // HOMEPAGE: align slider caption and slider arrows to the main content area
  function getPageContainerPadding() {
    var cw = $(".content-container").width();
    var ww = $(window).width();
    var cwRight = (ww - cw) / 2;
    return cwRight;
  }

  var $slider = $('.slider');
  var $sliderCaption = $('.slider-caption');

  $slider.find('.slick-prev').css('left', function() {
    return getPageContainerPadding() +  'px';
  });
  $slider.find('.slick-next').css('left', function() {
    return getPageContainerPadding() + 45 +  'px';
  });
  $sliderCaption.css('right', function() {
    return getPageContainerPadding() +  'px';
  });

  // fire resize event after the browser window resizing it's completed
  var resizeTimer;
  $(window).resize(function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(doneResizing, 500);
  });

  function doneResizing() {
    $slider.find('.slick-prev').css('left', function() {
      return getPageContainerPadding() +  'px';
    });
    $slider.find('.slick-next').css('left', function() {
      return getPageContainerPadding() + 45 +  'px';
    });
    $sliderCaption.css('right', function() {
      return getPageContainerPadding() +  'px';
    });
  }

  // HOMEPAGE: Tabs functionality
  $('ul.nav-tabs a').click(function(e) {
    $(this).tab('show');
    e.preventDefault();
  });

  // HOMEPAGE: Dynamic area:
  // on click center tab items on small screen sizes
  $('.main-nav-tabs li a').click(function() {
    var $parent = $(this).parent();
    centerTabItem($parent, '.main-tab-heading .main-nav-tabs');
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

  // HOMEPAGE: Dynamic area - Getting started:
  // On button hover toggle class on the bubble section
  $('.action-btn').each(function() {
    var $this = $(this);
    $this.hover(function() {
      if ($this.hasClass('regional-btn')) {
        $this.siblings('.action-bubble').toggleClass('regional-bubble');
      }
      if ($this.hasClass('transnational-btn')) {
        $this.siblings('.action-bubble').toggleClass('transnational-bubble');
      }
      if ($this.hasClass('national-btn')) {
        $this.siblings('.action-bubble').toggleClass('national-bubble');
      }
    })
  });

  // HOMEPAGE: Dynamic area - Adaptation support tool:
  // Highlight steps on hover
  $('.dynamic-area .ast-step-wrapper').hover(function() {
    $(this).children('.ast-circle').css({
      'background-color': '#FFD554',
      'border': '2px solid #F2C94C',
      'transform': 'scale(1.08)',
      'color': '#4F4F4F'
    });
    $(this).children('.step-text').css({
      'background-color': '#FFD554',
      'transform': 'scale(1.08)'
    });

    }, function() {
    $(this).children('.ast-circle').css({
      'background-color': '#B8D42F',
      'border': '2px solid #A5BF26',
      'transform': 'scale(1)',
      'color': '#fff'
    });
    $(this).children('.step-text').css({
      'background-color': '#f5f5f5',
      'transform': 'scale(1)'
    });
  });

  // HOMEPAGE: Dynamic area - EU Sector policies:
  // Sub-tab section close functionality
  $('.close-tab-pane').click(function() {
    var $contentParent = $(this).closest('.policies-tab-content');
    var $mainParent = $(this).closest('.sub-tab-section');
    $mainParent.find('.action-flex-item').removeClass('active');
    $contentParent.removeClass('active');
  });

  // Mobile menu button on click event
  $('.mobile-menu i').click(function() {
    $('body').toggleClass('no-ovf');
    $(this).toggleClass('fa-bars fa-times');
    $('.header').toggleClass('mobile-header');
    $('.header .main-nav, .top-menu-content').toggleClass('nav-toggle');

    return false;
  });

  // Mobile - show submenus on click
  $('.angle-down-icon').click(function() {
    $(this).parent().siblings('.sub-menu-wrapper').toggle();
  });

  // Top menu login
  $('#user-name').click(function(e) {
    e.preventDefault();
  });

  // Navigation menu: align sub-menu to the right
  // if overflows the main navigation menu
  var mainMenuWidth = $('.main-nav').width();

  $('.main-nav li').mouseenter(function() {
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

  // divide the sub-menu in 2 columns if 'sub-sub-menu' exist
  var navigationItem = $('.main-nav-item');
  navigationItem.each(function() {
    var $this = $(this);
    if ($this.find('.sub-sub-menu-wrapper').length > 0) {
      $this.find('.sub-menu-wrapper').css('column-count', '2');
    }
  });

  // add primary button class to share your information
  $('.share-your-info-ace-button button').addClass('standard-button primary-button');

  // add btn class to download as pdf
  $('#document-action-download_pdf').find('a').addClass('standard-button secondary-button');
  $('#login-form .formControls input').addClass('standard-button secondary-button');

  // Add a specific class for grid layout pages
  var currentLocation = window.location.pathname;
  var lastPathName;
  var parts = currentLocation.split('/');

  if (parts[parts.length - 1].length === 0) {
    lastPathName = parts[parts.length - 2];
  } else {
    lastPathName = parts[parts.length - 1];
  }

  var policyClass = 'subsection-sector-policies-' + lastPathName;
  var regionClass = 'subsection-transnational-regions-' + lastPathName;
  var countryClass = 'subsection-countries-' + lastPathName;

  // url: .../cca/countries-regions/cities
  var citiesClass = 'subsection-' + lastPathName;

  // url: .../cca/knowledge/adaptation-information/vulnerabilities-and-risks
  var vulnerabilitiesClass = 'subsection-adaptation-information-vulnerabilities-and-risks';
  // url: .../cca/knowledge/adaptation-information/observations-and-scenarios
  var observationsClass = 'subsection-adaptation-information-observations-and-scenarios';
  // url: .../cca/knowledge/adaptation-information/adaptation-measures
  var adaptationClass = 'subsection-adaptation-information-adaptation-measures';

  var $body = $('body');
  var bodyClassList = $body.attr('class').split(/\s+/);

  var selectedClasses = [];
  selectedClasses.push(
    policyClass,
    regionClass,
    countryClass,
    citiesClass,
    vulnerabilitiesClass,
    observationsClass,
    adaptationClass
  );

  // add grid layout class for the selected pages
  for (var i = 0 ; i < bodyClassList.length; i++ ) {
    if (jQuery.inArray(bodyClassList[i],selectedClasses) > -1) {
      $body.addClass('grid-layout');
    }
  }

  $.each(bodyClassList, function(index, item) {
    if (item === policyClass) {
      $body.addClass('eu-policy-page');
    }
    if (item === regionClass) {
      $body.addClass('region-page');
    }
    if (item === countryClass) {
      $body.addClass('country-page');
    }
  });

  var isGridLayout = $('.grid-layout').length > 0;
  var isPolicyPage = $('.eu-policy-page').length > 0;
  var isRegionPage = $('.region-page').length > 0;
  var isCountryPage = $('.country-page').length > 0;
  var isDBItemPage = $('.subsection-portals').length > 0;
  var isBalticSubpage = $('.subsection-transnational-regions-baltic-sea-region-adaptation').length > 0;
  var isCarpathianSubpage = $('.subsection-transnational-regions-carpathian-mountains').length > 0;
  var isASTPage = $('.subsection-tools-adaptation-support-tool').length > 0;

  function createGridLayout() {
    if (isGridLayout) {
      var $region = $('.region-page');
      $region.find('.column.col-md-2').removeClass('col-md-2').addClass('col-md-3');
      $region.find('.column.col-md-10').removeClass('col-md-10').addClass('col-md-9');
      $region.find('#content-core .row').prepend($('.column.col-md-9'));

      $('.col-md-9').children().wrapAll('<div class="content-column"/>');
      $('.col-md-3').children().wrapAll('<div class="content-sidebar"/>');

      var $content = $('.content-column');
      $content.find('img').closest('.tile-content').addClass('main-tile-content');
      $content.children('.col-md-4').wrapAll('<div class="row"/>');

      // move pdf button and 'last modified' viewlet to the main content area
      $('#document-action-download_pdf').parent().appendTo('.content-column');
      $content.prepend($('#viewlet-below-content-title'));

      $('.main-tile-content').prepend('<div class="flex-wrapper"/>');
      $('.flex-wrapper').append([
        $('.main-tile-content img'),
        $('.read_more_first')
      ]);

      var pageTitle = $('.main-tile-content').children('h2');
      $('.main-tile-content').prepend([
        pageTitle,
        $('.main-tile-content').children().find('h2')
      ]);

      $('.content-column').find(".tile-default").addClass('tile-wrapper');
    }
  }

  // EU SECTOR POLICIES
  // url: .../cca/eu-adaptation-policy/sector-policies/agriculture
  function policyLayout() {
    if (isPolicyPage) {
      var policySubTitles = $('.read_more_second').children('h2');

      policySubTitles.each(function() {
        $(this).replaceWith($('<p><strong>' + this.innerHTML + '</strong><p>'));
      });

      // Eu sector policy factsheet
      var factsheetIMG = $('.content-sidebar .image-inline').parent();
      var factheetCategory = $('.main-tile-content h2').text();

      factsheetIMG.html(function(i,h) {
        return h.replace(/&nbsp;/g,'');
      });

      $('.column.col-md-3').prepend(factsheetIMG);
      $('.column.col-md-3 .image-inline').parent().append(
        '<div class="factsheet-pdf">' +
        '<i class="fa fa-angle-double-right"></i>' +
        '<div class="factsheet-title">Factsheet on <span>' +
        factheetCategory + '</span></div></div>');
        $('.column.col-md-3 .image-inline').hide();
      }
    }

    // TRANSNATIONAL SUBPAGES
    // url: .../cca/countries-regions/transnational-regions/baltic-sea-region
    //     .../cca/countries-regions/transnational-regions/carpathian-mountains/general
    function regionSubpageLayout() {
      if (isBalticSubpage || isCarpathianSubpage) {
        $('body').addClass('region-subpage');
        $('#content-core .column.col-md-3').remove();
        $('#content-core .column.col-md-9').removeClass('col-md-9');

        $('.tile-content').addClass('clearfix');

        // add active class on current page sub-navigation item
        $(function() {
          var current = window.location.pathname;
          current = current.substring(current.lastIndexOf('/') + 1, current.length);
          $('.cover-section_nav-tile a').each(function() {
            var getURL = $(this).attr('href');
            getURL = getURL.substring(getURL.lastIndexOf('/') + 1, getURL.length);
            if (getURL.indexOf(current) !== -1) {
              $(this).addClass('active-nav');
            }
          })
        })
      }
    }

    // COUNTRY PAGES
    // url: .../cca/countries-regions/countries/austria
    function countryPageLayout() {
      if (isCountryPage) {
        $('.column.col-md-10').parents('.row').removeClass('row').addClass('country-wrapper');
        $('.column').removeClass('col-md-2 col-md-10');
        $('.sweet-tabs').attr('id', 'country-tab');

        $('.country-wrapper .column:first-child').addClass('country-header-map');
        $('.country-wrapper .column:nth-child(2)').addClass('country-content');

        $('.country-select-tile').parent().addClass('countries-dropdown');
        $('.country-select-tile img').remove();

        $('.country-header-map').append($('<div class="country-map">'));
        $('.country-content .last-update-tile').addClass('clearfix').prependTo('.tab-pane');

        $('table').addClass('listing');
        $('#document-action-download_pdf').parent().appendTo('.tab-pane');

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
          e.stopPropagation()
        });

        $('.dd-country-title .selected-inp').on('change', function(ev) {
          var url = ev.target.value;
          var country = $(".dd-country-title li[data-value='" + url + "']").text();

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
      }
    }

    // ADAPTATION SUPPORT TOOL
    // url: .../cca/knowledge/tools/adaptation-support-tool
    function astLayout() {

      if (isASTPage) {
        $('.lfc-single-image').remove(); // remove existing AST image

        $('.col-md-8').children('.tile:nth-child(2)').addClass('tile-wrapper');

        var titleAST = $('.tile-content').children('h1');
        titleAST.each(function() {
          $('<h2>' + $(this).html() + '</h2>').replaceAll(this);
        });
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
            'color': '#4F4F4F'
          });
        }
      });
    }

  createGridLayout();
  policyLayout();
  regionSubpageLayout();
  countryPageLayout();
  astLayout();


  $('.region-page #trans-region-select').siblings('div').addClass('region-countries');

  var regionsTitle = $('.region-countries').children('strong');
  regionsTitle.each(function() {
    $(this).replaceWith($('<h5>' + this.innerHTML + '</h5>'));
  });


  // HELP PAGE: Glossary
  // url: .../cca/help/glossary
  $('.GlossaryHeader').parents(':eq(2)').addClass('glossary-table');


  /*
  * For mobile: fix table styling issues
  *
  *
  * */
  function resizehandlerforContentTables(ev){
      if (window.matchMedia("(max-width: 480px)").matches) {
          $.each( $(".content-container table"),function (indx, item) {
              if($(item).parent().prop("tagName") !== "DIV" ){
                  $(item).wrapAll('<div style="overflow-x: auto;width: 86vw; "></div>');
              } else {
                  $(item).parent().css({
                      "overflow-x": "auto",
                      "width" : "86vw"
                  });
              }
          });
      }
  }

  /*
  * added font awesome arrows for menu item section
  * */
  function DoubleAngleListStyle(){
    $.each($("#content .cover-richtext-tile.tile-content:not(aceitem-urban-menu-tile) ul > li"), function (idx, item) {
      var $item = $(item);
      var $parent = $item.parent();
      var $parent_class = $parent.attr('class');

      if( $parent_class!== undefined && !$parent_class.indexOf("menu-urban-sub")
          && !$parent_class.indexOf("menu-urban")
          && !$parent_class.indexOf("aceitem-search-tile-listing")
          && $parent.find("ul").length === 0
          && $item.find("a").length > 0
          && !$item.hasClass("fa")
          && $("subsection-sector-policies-index_html").length === 0
      ){
        $item.addClass("fa fa-angle-double-right");
      }
    });
  }

  /*
  *  Adaptation options
  * - http://climate-local.com/cca/knowledge/adaptation-information/adaptation-measures
  * - remove double list decoration
  * */
  function AdaptationOptions(){
    $(".subsection-tools-general.subsection-tools-general-index_html ul li").removeClass("fa").removeClass("fa-angle-double-right");

    $(".subsection-adaptation-information-climate-services.subsection-adaptation-information-climate-services-climate-services " +
        ".tile-content ul li.fa.fa-angle-double-right")
        .removeClass("fa").removeClass("fa-angle-double-right");


    if($(".subsection-adaptation-information-adaptation-measures-index_html").length > 0){
        $.each( $(".aceitem-search-tile li ul li"), function(idx, item){
            var ia = $(item).find("a").prop('outerHTML');
            $(item).replaceWith('<li class="fa fa-angle-double-right">'+ ia +'</li>');
        });
    }
  }

  /*
  * Adaptation Information
  * - http://climate-local.com/cca/knowledge/adaptation-information/research-projects
  * - added font awesome arrows
  * */
  function AdaptationInformation(){
    if( $(".subsection-adaptation-information-research-projects-index_html").length > 0 ){

      $.each ( $(".cover-richtext-tile.tile-content ul li") , function(idx, item){
        if( $(item).find("a").length > 0 ){
          $(item).addClass("fa").addClass("fa-angle-double-right");
        }
      });
    }
  }

  /*
  * Uncertainty Guidance:
  * - http://climate-local.com/cca/knowledge/tools/knowledge/tools/uncertainty-guidance
  * - added font awesome arrows
  * */
  function UncertaintyGuidance(){
    if($(".subsection-tools-uncertainty-guidance-index_html").length > 0){
       $.each ( $(".cover-richtext-tile.tile-content ul li") , function(idx, item){
        if( $(item).find("a").length > 0 ){
          $(item).addClass("fa").addClass("fa-angle-double-right");
        }
      });
    }
  }

  /* Share your info:
  * - http://climate-local.com/cca/help/share-your-info
  * - http://climate-local.com/help/share-your-info/general
  * - added font awesome arrows
  * - added font awesome arrows to #third-level-menu
  * */
  function ShareYourInfo(){
    if( $(".subsection-share-your-info").length > 0){
      var arr = [
          ".cover-richtext-tile.tile-content ul li",
          "#third-level-menu li"
      ];
      return arr.map(function (sel){
          $.each ( $(sel) , function(idx, item){
              if( $(item).find("a").length > 0 ){
                  $(item).addClass("fa").addClass("fa-angle-double-right");
              }
          });
      });
    }
  }

  function StylingFixes(){
    DoubleAngleListStyle();
    AdaptationOptions();
    AdaptationInformation();
    UncertaintyGuidance()
    ShareYourInfo();
  }

  resizehandlerforContentTables();
  $( window ).resize(resizehandlerforContentTables);

  StylingFixes();

});
