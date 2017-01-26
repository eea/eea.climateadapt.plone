jQuery(document).ready(function(){
    $("#tags-admin button.more-links").click(function(){
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

    $(".rename-tag-button").click(function(){
        var tag = $(this).parent().find('input').val();
        var dial = $(this).siblings('.rename-tag-dialog').dialog({
            height: 200,
            width: 400,
        });
        dial.find('.input-tag').val(tag)

        $('.ui-dialog').keydown(function(e){
            if (e.keyCode === 27) {
                dial.dialog('destroy');
                dial.css('display', 'none');
            }
        });

        $('.ui-dialog').css('z-index', '1111');
        $('.ui-dialog-titlebar-close').on('click', function() {
            dial.dialog('destroy');
            dial.css('display', 'none');
        });
    });

    $("#tags-admin").DataTable();
});
