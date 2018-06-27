$(document).ready(function() {

  // initialize homepage slider
  $('.slider').slick({
    infinite: true,
    speed: 500,
    fade: true,
    slidesToShow: 1,
    dots:  true,
    autoplay: true,
    autoplaySpeed: 4000,
  });

  // move slick slider dots to slider caption area
  $(".slick-dots").prependTo(".slider-bottom-caption");

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


  $('.action-btn').each(function() {
    $(this).hover(function() {
      if ($(this).hasClass('regional-btn')) {
        $(this).siblings('.action-bubble').toggleClass('regional-bubble');
        $(this).siblings('.triangle ').toggleClass('regional-triangle-active');
      }
      if ($(this).hasClass('transnational-btn')) {
        $(this).siblings('.action-bubble').toggleClass('transnational-bubble');
        $(this).siblings('.triangle').toggleClass('transnational-triangle-active');
      }
      if ($(this).hasClass('national-btn')) {
        $(this).siblings('.action-bubble').toggleClass('national-bubble');
        $(this).siblings('.triangle').toggleClass('national-triangle-active');
      }
    })
  })

  // center tabs menu items on click on small screen sizes
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

  // homepage tabs functionality
  $("ul.nav-tabs a").click(function (e) {
    e.preventDefault();
    $(this).tab('show');
  });

  // eu policies sub-tab section close functionality
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
    $(this).siblings('.sub-menu-wrapper').toggle();
    // $(this).children('.fa').toggleClass('fa-angle-down fa-angle-up');
    $(this).parent().siblings('li').find('.sub-menu-wrapper').hide();
    e.stopPropagation();
  });

});
