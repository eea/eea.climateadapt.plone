jQuery(document).ready(function(){
    $("#keywords-admin button.more-links").click(function(){
        $('span', this).toggleClass('glyphicon glyphicon-zoom-in');
        $('span', this).toggleClass('glyphicon glyphicon-zoom-out');
        var $placeholder = $(this).parent().find('.links');

        if ($(this).hasClass('opened')){
            $(this).removeClass('opened');
            $placeholder.empty();
            return;
        }

        $(this).addClass('opened');

        var keyword = $(this).parent().find('input').val();
        $.post('keyword-objects', {'keyword':keyword}, function(data){
            var $ul = $("<ul>");
            $(data).each(function(index, value){
                var $link = $('<a>').attr({'href': value, 'target':'_blank'}).html(value);
                var $li = $("<li>").append($link);
                $ul.append($li);
            });
            $placeholder.append($ul);
        }, 'json');
    });

    $(".rename-keyword-button").click(function(){
        var keyword = $(this).parent().find('input').val();
        var dial = $(this).siblings('.rename-keyword-dialog').dialog({
            height: 100,
            width: 400,
        });
        dial.find('.input-keyword').val(keyword)

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

    $("#keywords-admin").DataTable();
});
