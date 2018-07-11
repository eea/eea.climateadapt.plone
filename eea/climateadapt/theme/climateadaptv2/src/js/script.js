$(document).ready(function() {

  // HOMEPAGE: initialize slick slider
  $('.slider').slick({
    infinite: true,
    speed: 500,
    fade: true,
    slidesToShow: 1,
    dots:  true,
    autoplay: true,
    autoplaySpeed: 4000,
  });


  // HOMEPAGE: move slick slider dots to slider caption area
  $(".slick-dots").prependTo(".slider-bottom-caption");

  // HOMEPAGE: align slider caption and slider arrows to the main content area
  function getPageContainerPadding() {
    var cw = $(".content-container").width();
    var ww = $(window).width();
    var cwRight = (ww - cw) / 2;
    return cwRight;
  }

  $('.slider .slick-prev').css('left', function() {
    return getPageContainerPadding() +  'px';
  });
  $('.slider .slick-next').css('left', function() {
    return getPageContainerPadding() + 45 +  'px';
  });
  $('.slider-caption').css('right', function() {
    return getPageContainerPadding() +  'px';
  });

  $(window).resize(function() {
    $('.slider .slick-prev').css('left', function() {
      return getPageContainerPadding() +  'px';
    });
    $('.slider .slick-next').css('left', function() {
      return getPageContainerPadding() + 45 +  'px';
    });
    $('.slider-caption').css('right', function() {
      return getPageContainerPadding() +  'px';
    });
  });

  // HOMEPAGE: Tabs functionality
  $("ul.nav-tabs a").click(function (e) {
    e.preventDefault();
    $(this).tab('show');
  });

  // HOMEPAGE: Dynamic area:
  // on click center tab items on small screen sizes
  $(".main-tab-heading ul li a").click(function() {
    var $parent = $(this).parent();
    centerTabItem($parent, '.main-tab-heading ul');
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
    $(this).hover(function() {
      if ($(this).hasClass('regional-btn')) {
        $(this).siblings('.action-bubble').toggleClass('regional-bubble');
      }
      if ($(this).hasClass('transnational-btn')) {
        $(this).siblings('.action-bubble').toggleClass('transnational-bubble');
      }
      if ($(this).hasClass('national-btn')) {
        $(this).siblings('.action-bubble').toggleClass('national-bubble');
      }
    })
  })


  // HOMEPAGE: Dynamic area - Adaptation support tool:
  // Highlight steps on hover
  $(".ast-step-wrapper").hover(function() {
    $(this).children('.ast-circle').css({
      'background-color': '#FFD554',
      'border': '2px solid #F2C94C',
      'transform': 'scale(1.08)',
      'color': '#4F4F4F'
    });
    $(this).children('.step-text').css({
      'background-color': '#FFD554',
      'transform': 'scale(1.08)',
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
  $(".close-tab-pane").click(function() {
    var $contentParent = $(this).closest('.policies-tab-content');
    var $mainParent = $(this).closest('.sub-tab-section');
    $mainParent.find('.action-flex-item').removeClass('active');
    $contentParent.removeClass('active');
  });

  // mobile menu button on click event
  $('.mobile-menu i').on('click', function() {
    $('body').toggleClass('no-ovf');
    $(this).toggleClass('fa-bars fa-times');
    $('.header').toggleClass('mobile-header');
    $('.nav-menu-wrapper, .top-menu-content').toggleClass('nav-toggle');

    return false;
  });

  // mobile - show submenus on click
  $('.menu-toggle').on('click', function(e) {
    $(this).siblings('.main-sub-menu-wrapper').toggle();
    $(this).parent().siblings('li').find('.main-sub-menu-wrapper').hide();
    e.stopPropagation();
  });

});
