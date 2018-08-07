$(document).ready(function() {
  var $body = $('body');

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

  // HOMEPAGE: Main area
  // Get heighest div and make equal heights on every boxes
  var $mainBox = $('.main-box');
  var mainBoxMaxHeight = 0;
  $mainBox.each(function() {
    mainBoxMaxHeight = ($(this).outerHeight() > mainBoxMaxHeight) ? $(this).outerHeight() : mainBoxMaxHeight;
  });
  $mainBox.css('min-height', mainBoxMaxHeight);

  // Mobile menu button on click event
  $('.mobile-menu i').click(function() {
    $body.toggleClass('no-ovf');
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

  // Divide the sub-menu in 2 columns if 'sub-sub-menu' exist
  var navigationItem = $('.main-nav-item');
  navigationItem.each(function() {
    var $this = $(this);
    if ($this.find('.sub-sub-menu-wrapper').length > 0) {
      $this.find('.sub-menu-wrapper').css('column-count', '2');
    }
  });

  // add btn class to download as pdf
  $('#document-action-download_pdf').addClass('standard-button secondary-button');
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

  var bodyClassList = $body.attr('class') !== undefined ? $body.attr('class').split(/\s+/) : [];

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

  var isPolicyPage = $('.eu-policy-page').length > 0;
  var isCountryPage = $('.country-page').length > 0;
  var isBalticSubpage = $('.subsection-transnational-regions-baltic-sea-region-adaptation').length > 0;
  var isCarpathianSubpage = $('.subsection-transnational-regions-carpathian-mountains').length > 0;
  var isASTPage = $('.subsection-tools-adaptation-support-tool').length > 0;

  var $content = $('.content-column');
  $content.find('h2').first().addClass('tile-title');


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
      var factheetCategory = $('.tile-title').text();

      factsheetIMG.html(function(i,h) {
        return h.replace(/&nbsp;/g,''); // remove whitespaces
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

    // TRANSNATIONAL SUBPAGES (two specific subpages)
    // url: .../cca/countries-regions/transnational-regions/baltic-sea-region
    //     .../cca/countries-regions/transnational-regions/carpathian-mountains/general
    function regionSubpageLayout() {
      if (isBalticSubpage || isCarpathianSubpage) {
        $body.addClass('region-subpage');
        $('#content-core .column.col-md-3').remove();
        $('#content-core .column.col-md-9').removeClass('col-md-9');

        $('.tile-content').addClass('clearfix');

        // Add active class on current page sub-navigation item
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
        $('#content-core').children().addClass('country-wrapper').removeClass('row');
        $('.sweet-tabs').attr('id', 'country-tab');

        var $countrySelect = $('.country-select-tile');
        $countrySelect.parent().addClass('countries-dropdown');
        $countrySelect.find('img').remove();

        var $tabPane = $('.tab-pane');
        $('.country-header-map').append($('<div class="country-map">'));
        $('.country-content .last-update-tile').addClass('clearfix').prependTo($tabPane);

        $('table').addClass('listing');
        $('#document-action-download_pdf').parent().appendTo($tabPane);

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

  // Remove double angle '»' from 'Search result' listings
  $(".aceitem-search-tile-listing li ul li").each(function() {
    var $this = $(this);
    $this.html($this.html().replace('»', ''));
  });

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

  resizehandlerforContentTables();
  $( window ).resize(resizehandlerforContentTables);

});
