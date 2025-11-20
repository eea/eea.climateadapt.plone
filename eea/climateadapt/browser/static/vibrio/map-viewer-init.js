var dojoConfig = {
  parseOnLoad: true,
};

//https://geoportal.ecdc.europa.eu/vibriomapviewer/api/proxy/?https://cwcgom.aoml.noaa.gov/thredds/wms/VIBRIO_RISK/RISK.nc?SERVICE=WMS&REQUEST=GetCapabilities
var defaultStyle = "boxfill/vibrio";
var defaultColourBands = "10";
var defaultMaxValue = "28";
var extentXMin = -0.3;
var extentXMax = 27;
var extentYMin = 45;
var extentYMax = 66;

// init proxy path
proxy = "api/proxy/";
proxy = "/@@vibriomap-proxy";

// init wms list of services
oMapWMSServices = [
  {
    Title: "Daily Suitability Index",
    Url: "https://cwcgom.aoml.noaa.gov/thredds/wms/VIBRIO_RISK/RISK.nc",
    Version: "1.1.1",
  },
  {
    Title: "Suitabilty Index (last 7 days)",
    Url: "https://cwcgom.aoml.noaa.gov/thredds/wms/VIBRIO_RISK_CUMULATIVE/RISK.nc",
    Version: "1.1.1",
  },
  {
    Title: "Forecast (next 5 days)",
    Url: "https://cwcgom.aoml.noaa.gov/thredds/wms/VIBRIO_RISK_FORECAST/RISK.nc",
    Version: "1.1.1",
  },
];

// init wms list of layers
oWMSLayerTitle = [
  {
    Name: "daily_vibrio_risk",
    Title: "Daily Vibrio Risk",
  },
  {
    Name: "weekly_cumulative_vibrio_risk_maximum",
    Title: "Weekly Maximum",
  },
  {
    Name: "weekly_cumulative_vibrio_risk_mean",
    Title: "Weekly Mean",
  },
  {
    Name: "forecast_daily_vibrio_risk",
    Title: "Forecast",
  },
];

// init legend description
legendDescription =
  "> or = 16: Very High <br /> 12 - 15: High <br /> 8 - 11: Medium <br /> 4 - 7: Low <br /> 0 - 3: Very Low <br /> Black: > selected range";

var isFullScreen = false;

$(function () {
  $("#hidePanel").click(function () {
    if (!$("#capaLeft").is(":visible")) {
      $("#capaLeft").show();
      $("#leftPanel").css("width", "290px");
      $("#map").css("width", "calc(99% - 290px)");
      map.resize();
      $("#showhide").attr(
        "src",
        "/++api++/++resource++eea.climateadapt.static/vibrio/arrow_left.png"
      );
    } else {
      $("#capaLeft").hide();
      $("#leftPanel").css("width", "2%");
      $("#map").css("width", "97%");
      map.resize();
      $("#showhide").attr(
        "src",
        "/++api++/++resource++eea.climateadapt.static/vibrio/arrow_right.png"
      );
    }
  });

  $("#fullscreen").click(function () {
    if (isMobileDevice()) return;

    if (isFullScreen) {
      closeFullscreen();
      $("#map").height("600px");
    } else {
      openFullscreen(document.getElementById("mapContainer"));
      $("#map").height("97%");
    }

    $("#map").resize();
  });
  $(document).on(
    "webkitfullscreenchange mozfullscreenchange fullscreenchange MSFullscreenChange",
    function () {
      if (
        !document.webkitIsFullScreen &&
        !document.mozFullScreen &&
        !document.msFullscreenElement
      ) {
        $("#map").height("600px");
        $("#map").resize();
      }
    }
  );
});
require([
  "dojo/dom", // for inserting value in TextBox example
  //"dojo/parser", // parser because of TextBox decoration
  "dijit/form/HorizontalSlider",
  //"dijit/form/TextBox" // this we only include to make an example with TextBox
], function (dom, HorizontalSlider, TextBox) {
  // parser.parse();

  var slider = new HorizontalSlider(
    {
      name: "slider",
      value: 1,
      minimum: 0,
      maximum: 1,
      intermediateChanges: true,
      style: "width:100px;",
      onChange: function (value) {
        //dom.byId("sliderValue").value = value;
        cahngeOpacity(value);
      },
    },
    "slider"
  ).startup();
});

function isMobileDevice() {
  return (
    navigator.userAgent.match(/Android/i) ||
    navigator.userAgent.match(/webOS/i) ||
    navigator.userAgent.match(/iPhone/i) ||
    navigator.userAgent.match(/iPad/i) ||
    navigator.userAgent.match(/iPod/i) ||
    navigator.userAgent.match(/BlackBerry/i) ||
    navigator.userAgent.match(/Windows Phone/i)
  );
}
function ErrorHandler() {
  alert("Error ErrorHandler");
}

/* View in fullscreen */
function openFullscreen(elem) {
  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if (elem.mozRequestFullScreen) {
    /* Firefox */
    elem.mozRequestFullScreen();
  } else if (elem.webkitRequestFullscreen) {
    /* Chrome, Safari and Opera */
    elem.webkitRequestFullscreen();
  } else if (elem.msRequestFullscreen) {
    /* IE/Edge */
    elem.msRequestFullscreen();
  }

  isFullScreen = true;
}

/* Close fullscreen */
function closeFullscreen() {
  if (document.exitFullscreen) {
    document.exitFullscreen();
  } else if (document.mozCancelFullScreen) {
    /* Firefox */
    document.mozCancelFullScreen();
  } else if (document.webkitExitFullscreen) {
    /* Chrome, Safari and Opera */
    document.webkitExitFullscreen();
  } else if (document.msExitFullscreen) {
    /* IE/Edge */
    document.msExitFullscreen();
  }

  isFullScreen = false;
}

var $disclaimerDlg;
function showDisclaimer() {
  if (!$disclaimerDlg) {
    $disclaimerDlg = $("#disclaimerDialog").dialog({
      modal: true,
      draggable: false,
      width: "80%",
      dialogClass: "disclaimer-dialog",
    });
  }

  $disclaimerDlg.dialog("open");

  //$("#aboutMapDialog a").blur();
}
