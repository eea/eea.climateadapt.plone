jQuery(document).ready(function(){
    $("#tags-admin button").click(function(){
        $('span', this).toggleClass('glyphicon glyphicon-zoom-in');
        $('span', this).toggleClass('glyphicon glyphicon-zoom-out');
        var $placeholder = $(this).parent().find('.links');

        if ($(this).hasClass('opened')){
            $(this).removeClass('opened');
            $placeholder.empty();
            return;
        }

        $(this).addClass('opened');

        var tag = $(this).parent().find('input').val();
        $.post('special-tags-objects', {'special_tags':tag}, function(data){
            var $ul = $("<ul>");
            $(data).each(function(index, value){
                var $link = $('<a>').attr({'href': value, 'target':'_blank'}).html(value);
                var $li = $("<li>").append($link);
                $ul.append($li);
            });
            $placeholder.append($ul);
        }, 'json');
    });

    $("#tags-admin").DataTable();

});
