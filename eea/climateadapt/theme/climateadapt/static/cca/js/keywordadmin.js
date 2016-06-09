jQuery(document).ready(function(){
    $("#keywords-admin button").click(function(){
        console.log('triggered', this);
        $('span', this).toggleClass('glyphicon glyphicon-zoom-in');
        $('span', this).toggleClass('glyphicon glyphicon-zoom-out');
        var $placeholder = $(this).parent().find('.links');

        if ($(this).hasClass('opened')){
            $(this).removeClass('opened');
            $placeholder.empty();
            return;
        }

        $(this).addClass('opened');

        console.log('placeholder', $placeholder);
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

    $("#keywords-admin").DataTable();

});
