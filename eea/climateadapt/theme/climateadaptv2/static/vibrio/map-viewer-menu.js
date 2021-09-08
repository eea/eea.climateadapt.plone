$(document).ready(function () {
    $(".slide").hide();
    link1();
    link2();
    link3();
});

function link1() {
    $("#link1").click(function () {
        $(".slide").slideToggle("fast");

        $('#imgArrow').toggleClass("rotated")

    });
}


function link2() {
    $("#link2").click(function () {
        if (!$(".slide").is(":visible")) {
            $(".slide").slideDown("fast");
        }
        $("#capa1").show();
        $("#capa2").hide();

    });
}

function link3() {
    $("#link3").click(function () {
        if (!$(".slide").is(":visible")) {
            $(".slide").slideDown("fast");
        }
        $("#capa2").show();
        $("#capa1").hide();
    });
}
