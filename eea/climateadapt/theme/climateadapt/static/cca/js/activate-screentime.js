var handler = undefined;
var previous_hash = undefined;
var count = 0;

$(document).ready(function() {
    if (window.location.pathname === "/data-and-downloads") {
        handler = setInterval(search_handler, 1000)
    }
    else {
        $("#content").screentimeAnalytics();
    }
});

function search_handler() {
    if ($('#faceted-results').children().children().length > 1 && count === 0) {
        $("#content").screentimeAnalytics();
        previous_hash = window.location.hash;
        count += 1;
    }

    if (previous_hash !== undefined) {
        if (previous_hash !== window.location.hash) {
            if ($('#faceted-results').children().children().length > 1) {
                $("#content").screentimeAnalytics();
                previous_hash = window.location.hash;
            }
        }
    }
}
