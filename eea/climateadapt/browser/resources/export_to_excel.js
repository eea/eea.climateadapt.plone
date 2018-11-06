$(function(){
  function set_export_url(){
    var params = '';
    $.each(Faceted.Query, function(crit, values){
      $.each(values, function(index, val){
        params = params + '&' + crit + '=' + val;
      });
    });
    var export_url = [location.protocol, '//', location.host, location.pathname].join('') + '/@@eea_excel_export_url?' + params;
    $.get(export_url, function(data){
      $('#plone-contentmenu-actions-export_to_excel').attr('href', data);
    });
    return $.get(export_url).responseText;
  }

  jQuery(Faceted.Events).on('FACETED-QUERY-CHANGED', function(){
    set_export_url();
  });
});
