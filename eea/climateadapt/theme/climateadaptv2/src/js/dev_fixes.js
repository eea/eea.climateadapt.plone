jQuery(function($) {

  // modify urls to remove base href from menu links
  var url = window.location.origin + '/cca/';
  var base_url = $("base").attr('href');
  if (!base_url) {
    return;
  }

  // var base_url_length = base_url.length;
  // $(".sub-menu-link, .sub-sub-menu-link, .main-nav-item > a").each(function(idx, el) {
  //    var el_url = el.href;
  //    var url_length = el_url.length;
  //    var last_value = el_url.substr(base_url_length, url_length);
  //    el.href =  url + last_value;
  // })
});

$(document).ready(function() {
  var label_html = $('#formfield-form-widgets-ipcc_category label[for=form-widgets-ipcc_category]').html();
  var link = "<a href='https://www.ipcc.ch/report/ar5/wg2/adaptation-needs-and-options'>IPCC adaptation options categories</a>";
  if (label_html) {
    label_html = label_html.replace('IPCC adaptation options categories', link);
    $('#formfield-form-widgets-ipcc_category label[for=form-widgets-ipcc_category]').html(label_html);
  }
});
