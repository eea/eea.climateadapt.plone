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
  // Get the heighest div and make equal height on every boxes
  var windowsize = $(window).width();
  var $mainBox = $('.main-box');
  var mainBoxMaxHeight = 0;

  $mainBox.each(function() {
    mainBoxMaxHeight = ($(this).outerHeight() > mainBoxMaxHeight) ? $(this).outerHeight() : mainBoxMaxHeight;
  });

  if (windowsize <= 600) {
    $mainBox.css('min-height', 'auto');
  } else {
    $mainBox.css('min-height', mainBoxMaxHeight);
  }

  // Mobile menu button on click event
  $('.mobile-menu i').click(function() {
    $body.toggleClass('no-ovf');
    $(this).toggleClass('fa-bars fa-times');
    $('.header').toggleClass('mobile-header');
    $('.header .main-nav, .top-menu-content').toggleClass('nav-toggle');

    return false;
  });

  // Mobile - show submenus on click
  $('.toggle-down').click(function() {
    $(this).parent().siblings('.sub-menu-wrapper').toggle();
    $(this).parent().parent().siblings().children('.sub-menu-wrapper').hide();
    return false;
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
      var submenuwrapper = $this.find('.sub-menu-wrapper');
      var submenucols = submenuwrapper.find(".sub-menu").length > 1 ? submenuwrapper.find(".sub-menu").length : 2;
      submenuwrapper.css({
          'column-count': submenucols,
          '-webkit-column-count' : submenucols,
          '-moz-column-count': submenucols,
      });
    }
  });

  // GENERAL
  // add button class
  $('#document-action-download_pdf,' +
    '#login-form .formControls input,' +
    '#folderlisting-main-table .context').addClass('standard-button secondary-button');

  // Add table class
  $('.CSSTableGenerator').addClass('listing');

  var $blueButton = $('.bluebutton');
  $blueButton.addClass('standard-button primary-button');
  $blueButton.parent().css('text-align', 'left');

  // add button classes for form buttons
  var $submitButton = $('input[type=submit]');
  $submitButton.each(function () {
    if ($(this).val() === 'Save') {
      $(this).addClass('standard-button primary-button');
    } else if ($(this).val() === 'Cancel') {
      $(this).addClass('standard-button secondary-button');
    } else {
      $(this).addClass('standard-button secondary-button');
    }
  })


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
  })

  // Add a specific class for grid layout pages
  var currentLocation = window.location.pathname;
  var pathParts = currentLocation.split('/');
  var lastPathName;

  if (pathParts[pathParts.length - 1].length === 0) {
    lastPathName = pathParts[pathParts.length - 2];
  } else {
    lastPathName = pathParts[pathParts.length - 1];
  }

  if (lastPathName === 'index_html') {
    lastPathName = pathParts[pathParts.length - 3];
  } else {
    lastPathName = pathParts[pathParts.length - 1];
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


  // EU SECTOR POLICIES
  // url: .../cca/eu-adaptation-policy/sector-policies/agriculture
  function policyLayout() {
    if (isPolicyPage) {

      var policySubTitles = $('.read_more_second').children('h2');
      policySubTitles.each(function() {
        $(this).replaceWith($('<p><strong>' + this.innerHTML + '</strong><p>'));
      });

      // move eu sector policy factsheet
      var $sidebar = $('.column.col-md-3');
      $sidebar.before($sidebar.find('.factsheet-pdf').parent());
      }
    }

    // TRANSNATIONAL SUBPAGES (two specific subpages)
    // move detailed content under the sidebar (baltic sea, central europe)
    var $sidebar = $('.subsection-transnational-regions .column.col-md-3');
    $sidebar.after($sidebar.find('.detailed-content').parentsUntil('.tile-default'));

    // url: .../cca/countries-regions/transnational-regions/baltic-sea-region
    //     .../cca/countries-regions/transnational-regions/carpathian-mountains/general
    function regionSubpageLayout() {
      if (isBalticSubpage || isCarpathianSubpage) {
        $body.addClass('region-subpage');
        $('#content-core .column.col-md-3').remove();
        $('#content-core .column.col-md-9').removeClass('col-md-9');

        $('.tile-content').addClass('clearfix');
      }
    }

    // COUNTRY PAGES
    // url: .../cca/countries-regions/countries/austria
    function countryPageLayout() {
      if (isCountryPage) {
        $('.country-select-tile').closest('.row').css('margin', '0');
        $('.sweet-tabs').attr('id', 'country-tab');

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

  // Remove double angle '»' from 'Search result' listings
  $(".aceitem-search-tile-listing li ul li").each(function() {
    var $this = $(this);
    $this.html($this.html().replace('»', ''));
  });

  // Fix floating button
  $('.share-your-info-ace-button').wrapAll('<div class="clearfix"/>');

  $('.news-item').parent().parent().children('h2').addClass('news-title');

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

  var $pdfButton = $('#document-action-download_pdf');
  // Urban AST export section pdf button
  if (currentLocation.indexOf('/tools/urban-ast') !== -1 && currentLocation.indexOf('pdf.body') === -1) {
    var $sectionPDF = '<a href="/tools/urban-ast/download.pdf"' +
    'class="standard-button ast-section-pdf">' +
    'Download section as PDF</a>';
    $pdfButton.parent().before($sectionPDF);
  }

  // AST export section pdf button
  if (currentLocation.indexOf('/tools/adaptation-support-tool') !== -1 && currentLocation.indexOf('pdf.body') === -1) {
    var $sectionPDF = '<a href="/tools/adaptation-support-tool/download.pdf"' +
    'class="standard-button ast-section-pdf">' +
    'Download section as PDF</a>';
    $pdfButton.parent().before($sectionPDF);
  }

  // fix tiles edit button
  $('.tile-container').each(function() {
    var $this = $(this);
    var tileName = $this.find('.tile-type-name');
    var editbtn = $this.children('a');
    var contentWrapper = $this.children('div');
    if (tileName.text() == 'Relevant AceContent') {
      tileName.detach().appendTo(contentWrapper);
    }
    if (editbtn.text() == 'Edit') {
      editbtn.detach().appendTo(contentWrapper);
    }
  });

  // Toggle text on accordion
  var $panelTitle = $('.panel-title a');
  $panelTitle.click(function() {
    var $this = $(this);
    var panelTitleText = $this.text().toLowerCase();
    if (panelTitleText.indexOf('read more') > -1 || panelTitleText.indexOf('read less') > -1) {
      $this.text(function (a, b) {
        return (b == 'Read more' ? 'Read less' : 'Read more');
      });
    }
  });

  // Hide the download pdf on the search page
  if (window.location.href.indexOf("data-and-downloads") > -1) {
    $("#document-action-download_pdf").parent().hide();
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
  var $aceSidebar = $('.subsection-case-studies .aceitem_page .col-md-3');
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

});
