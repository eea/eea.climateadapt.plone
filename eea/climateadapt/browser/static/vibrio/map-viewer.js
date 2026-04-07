dojo.require("dijit.dijit"); // optimize: load dijit layer
dojo.require("dojo.dom");
dojo.require("dojo.data.ItemFileWriteStore");
dojo.require("dojox.grid.DataGrid");
dojo.require("dojox.grid.cells.dijit");
dojo.require("dijit.layout.BorderContainer");
dojo.require("dijit.layout.ContentPane");
dojo.require("dijit.TitlePane");
dojo.require("esri.toolbars.navigation");
dojo.require("esri.dijit.Scalebar");
dojo.require("dijit.form.Button");
dojo.require("dijit.form.HorizontalSlider");
dojo.require("esri.layers.WMSLayer");
dojo.require("esri.layers.WMSLayerInfo");
dojo.require("esri.dijit.BasemapGallery");
dojo.require("esri.dijit.Attribution");
dojo.require("esri.IdentityManager");
dojo.require("dojo.fx");
dojo.require("esri.SpatialReference")
dojo.require("esri.geometry.Extent")
dojo.require("esri.tasks.geometry")
dojo.require("esri.dijit.OverviewMap");
dojo.require("dijit.form.Select");
dojo.require("dojo.on")
dojo.require("dijit.registry");
dojo.require("dojo.parser");
dojo.require("dojox.layout.ExpandoPane");

var map;
var grid;
var gridData;
var gridMul;
var gridSelMul;
var rainData;
var lstData;
var ndviData;
var panup;
var navToolbar;
var DynamicMapServiceLayer;
var mapService;
var layer;
var layerLoad;

var overviewMapDijit
dojo.ready(init);
var oMapServices = [];
var oMapWMSServices = [];
var oWMSLayerTitle = [];
var legendDescription = "";
var proxy = "";


dojo.ready(function() {
  dojo.declare("WMSLayerTime", esri.layers.DynamicMapServiceLayer, {
    constructor: function(url, obj) {
      this.initialExtent = this.fullExtent = new esri.geometry.Extent({"xmin":-16476154.32,"ymin":2504688.54,"xmax":-6457400.14,"ymax":7514065.62,"spatialReference":{"wkid":102100}});
      this.spatialReference = new esri.SpatialReference({wkid:102100});


      this.WMSServerURL = url;
      this.version = obj.version;
      this.colorscalerange = obj.colorscalerange;
      this.logscale = obj.logscale;
      this.numcolorbands = obj.numcolorbands;
      this.styles = obj.styles;
      this.time = obj.time;
      this.visiblelayers = obj.visiblelayers.join();


      this.loaded = true;
      this.onLoad(this);
    },

    getImageUrl: function(extent, width, height, callback) {
      var params = {
        request:"GetMap",
        transparent:true,
        format:"image/png",
        bgcolor:"0xFFFFFF",
        version: this.version,
        layers: this.visiblelayers,
        styles: this.styles,
        colorscalerange: this.colorscalerange,
        numcolorbands: this.numcolorbands,
        logscale: this.logscale,
        time: this.time,
        exceptions: "application/vnd.ogc.se_xml",

        //changing values
        bbox:extent.xmin + "," + extent.ymin + "," + extent.xmax + "," + extent.ymax,
        crs: "EPSG:3857",// + extent.spatialReference.wkid,
        width: width,
        height: height
      };      
      if (this.WMSServerURL.indexOf("?") < 0){this.WMSServerURL += "?"}
      callback(this.WMSServerURL + dojo.objectToQuery(params));

    }
  });
});



function init() {
    layerLoad = false;

    map = new esri.Map("map", {
        basemap: "topo",
        //center: [15.00, 57.00], // longitude, latitude
        extent: new esri.geometry.Extent(extentXMin, extentXMax, extentXMax, extentYMax, new esri.SpatialReference(4326)),
        zoom: 3,
        logo: false,
        showAttribution: false,
        sliderOrientation: "vertical",
        sliderPosition: "top-left",
        sliderStyle: "small",
        opacity: 0.5
    });
    
    var scalebar = new esri.dijit.Scalebar({
        map: map,
        scalebarUnit: "dual"
    }, dojo.byId("scalebar"));

    esri.config.defaults.io.proxyUrl = proxy;
    //esri.config.defaults.io.alwaysUseProxy = true
        
    overviewMapDijit = new esri.dijit.OverviewMap({
        map: map,
        visible: false
    });
    overviewMapDijit.startup();

    map.showPanArrows(panup);

    var attribution = new esri.dijit.Attribution({
        map:map
    }, "attributionDiv");
    attribution.startup();

    loadMap();
}

function DisplayURLService(){
    var serviceLayer = new esri.layers.ArcGISDynamicMapServiceLayer(URLService, {opacity:0.5});
    serviceLayer.onError(serviceLayer_loadingError)
    map.addLayer(serviceLayer);
}

function serviceLayer_loadingError(e){
    var serviceLayer = new esri.layers.WMSLayer(URLService, {opacity:0.5});
    map.addLayer(serviceLayer);    
}

function extentMap() {
    var extent = new esri.geometry.Extent(extentXMin, extentYMin, extentXMax, extentYMax, new esri.SpatialReference({ wkid: 4326 }));

    map.setExtent(extent);

    navToolbar = new esri.toolbars.Navigation(map);
}

function panTop() {
    map.panUp();
}

function pandown(){
    map.panDown();
}
function panright(){
    map.panRight();
}
function panleft() {
    map.panLeft();
}

function fullExtent() {
    navToolbar.zoomToFullExtent();
}

function cahngeOpacity(value) {
    if (map.layerIds.length > 1) {
        var currentVisibleLayer = map.getLayer(map.layerIds[1]);
        //  map.removeLayer(currentVisibleLayer);
        currentVisibleLayer.setOpacity(value);
        //map.addLayer(currentVisibleLayer);
    }
}


function changeBasemap(baseMap) {
    map.setBasemap(baseMap)
}

function overviewShow() {
    if (overviewMapDijit.visible) {
        overviewMapDijit.hide();
    } else {
        overviewMapDijit.show();
    }
}

function loadWMSLayer(oMapServices, oService) {

    oLayerWMS = new esri.layers.WMSLayer(oMapServices[oService].Url, {
        displayName: oMapServices[oService].Title,
        id: oMapServices[oService].Title,
        opacity: 0.5,
        visible: false,
        version: oMapServices[oService].Version,
        showLegend: true,
        layer: [oMapServices[oService].Layer],
        //proxyUrl: "/proxy/proxy.ashx?",
        skipGetCapabilities: true
    });
    return oLayerWMS;
}

var mapCount = 0;
var loadedServices = 0;
var arrWMSVibrio = []
function loadVibrioMap(){
    mapCount = oMapWMSServices.length;
    for (var i=0; i < mapCount; i++){
        arrWMSVibrio.push(null)
    }

    for (var i in oMapWMSServices) {
        var service = oMapWMSServices[i];
        parseWMS(service.Url, service.Title, parseInt(i, 10) + 1);
    }


    fillColourBands();
    fillScaleMethods();
    fillMinValues();
    fillMaxValues();
    $( "#dateTo" ).datepicker();
    $( "#dateFrom" ).datepicker();
}

function parseWMS(url, title, index){
    $.ajax({
        type: "GET",
        url: proxy + "?" + url + "?SERVICE=WMS&REQUEST=GetCapabilities",
        dataType: "xml",
        success: function(xml) {
            var WMSVibrio = {};
            WMSVibrio.title = title;
            WMSVibrio.url = url;
            WMSVibrio.layers = [];            
            $(xml).find("Layer").each(function(){
                if ($(this).children("Name").text() != ""){
                    var WMSLayer = {}
                    WMSLayer.id = $(this).children("Name").text();
                    WMSLayer.name = getLayerTitle($(this).children("Name").text());
                    var arrStyles = [];
                    var aStyle = {};   
                    var layer = $(this).find("Name").parent();
                    layer.find("Style").each(function(){
                        aStyle = {}
                        aStyle.name = $(this).find("Name").text();
                        aStyle.image = $(this).find("OnlineResource").attr("xlink:href");
                        arrStyles.push(aStyle);
                    }); 
                    WMSLayer.styles = arrStyles;
                    var dimensions = layer.find("Dimension").text().replace(/(\r\n|\n|\r)/gm,"").trim().split(",");     
                    $.each( dimensions, function( index, value ){
                        dimensions[index] = new Date(value.split("-")[0], parseInt(value.split("-")[1])-1, value.split("-")[2].substring(0, 2))
                    });
                    WMSLayer.dimensions = dimensions;
                    WMSVibrio.layers.push(WMSLayer)
                }  
            })
            arrWMSVibrio.splice(index - 1, 1, WMSVibrio)
            fillControls();
        }
    });
}

function getLayerTitle(str){
    switch(str){
        case "daily_vibrio_risk":
            return "Daily Vibrio Risk";
            break;
        case "weekly_cumulative_vibrio_risk_maximum":
            return "Weekly Maximum";
            break;
        case "weekly_cumulative_vibrio_risk_mean":
            return "Weekly Mean";
            break;
        case "forecast_daily_vibrio_risk":
            return "Forecast"
            break;
    }
}

function fillControls(){
    loadedServices++;
    if (loadedServices == mapCount){
        var radioHTML = "";
        for (i in arrWMSVibrio){
            radioHTML += "<span>" + arrWMSVibrio[i].title + "</span>";
            for (j in arrWMSVibrio[i].layers){
                radioHTML += "<div>";
                radioHTML += "<input type='radio' data-i='"+i+"' data-j='"+j+"' name='mapType' id='"+ arrWMSVibrio[i].layers[j].id +"'/>";
                radioHTML += "<label for='"+ arrWMSVibrio[i].layers[j].id +"'>"+ arrWMSVibrio[i].layers[j].name +"</label>";
                radioHTML += "</div>";               
            }
        }
        $("#controls").append(radioHTML);
        $('input[type=radio][name=mapType]')[0].click()
        addListeners();
    }
}
function fillColourBands(){
    $("#colourBands").empty();
    $("#colourBands").append("<option value='10'>10</option>");
    $("#colourBands").append("<option value='16'>16</option>");
    $("#colourBands").append("<option value='20'>20</option>");
    $("#colourBands").append("<option value='32'>32</option>");
    $("#colourBands").append("<option value='50'>50</option>");
    $("#colourBands").append("<option value='100'>100</option>");
    $("#colourBands").append("<option value='254'>254</option>");
    $('#colourBands').val(defaultColourBands);
}

function fillScaleMethods(){
    $("#scaleMethod").empty();
    $("#scaleMethod").append("<option value='linear'>linear</option>");
    $("#scaleMethod").append("<option value='log'>log</option>");    
}
function fillMinValues(){
    $('#minValue').empty();
    for (i=0; i <= 42; i += 2){
        $("#minValue").append("<option value='" + i + "'>" + i + "</option>");    
    }
    $('#minValue').val(0);
}

function fillMaxValues(){
    $('#maxValue').empty();
    for (i=2; i <= 44; i += 2){
        $("#maxValue").append("<option value='" + i + "'>" + i + "</option>");    
    }
    $('#maxValue').val(defaultMaxValue);      
}
function setSlider(){ 
    if ($("#timeSlider").slider()){
        $("#timeSlider").slider( "destroy" );
    }
    $("#timeSlider").slider({
        min: 0,
        max: selectedDatesArray.length - 1,
        value: selectedDatesArray.length - 1
    });   

    var startDate = selectedDatesArray[0];
    var endDate = selectedDatesArray[selectedDatesArray.length - 1];

    // use the dates choosen in the calendar, if defined
    var fromDateCalendar = $("#dateFrom").datepicker("getDate");
    var toDateCalendar = $("#dateTo").datepicker("getDate");
    if (fromDateCalendar)
        startDate = fromDateCalendar;
    if (toDateCalendar)
        endDate = toDateCalendar;

    $("#sliderDateFrom").text($.datepicker.formatDate('yy/mm/dd', startDate));
    $("#sliderDateTo").text($.datepicker.formatDate('yy/mm/dd', endDate));

    $("#sliderCurrentDate").text($.datepicker.formatDate('yy/mm/dd', endDate));     
    $("#sliderLayer").text(selectedService.title + " (" + selectedLayer.name + ")")
}

function setColourPalette(){
    if (dijit.registry.byId("colourPalette")){dijit.registry.byId("colourPalette").destroyRecursive();}
    var options = [];
    var style = {};
    for (var i = 0; i < selectedLayer.styles.length; i++){
        style = {};
        style.label = "<img src='"+selectedLayer.styles[i].image + "&COLORBARONLY=true&WIDTH=20&HEIGHT=20" +"'/><span style='padding:4px;'>" + selectedLayer.styles[i].name + "</span>"; 
        style.value = selectedLayer.styles[i].name;
        if (selectedLayer.styles[i].name == defaultStyle) { style.selected = true } else { style.selected = false }
        options.push(style)
    }
    var setColourPalette = new dijit.form.Select({
        id: "colourPalette",
        options: options, style:{width:'150px'}
    }).placeAt("colourPaletteDiv");
    setColourPalette.startup();
    dojo.on(setColourPalette, 'change', function(newValue){
        changeMap();
    });
}

var clickListener;
function identifyVibrio(){
    clickListener = map.on("click", vibrioClickListener);
    $("#imgidentifybutton").css("background-color", "beige");
    $("#imgidentifybutton").css("border", "1px solid black");
}

var $aboutMapDlg;
function showAboutMapInfo() {
    if (!$aboutMapDlg) {
        $aboutMapDlg = $("#aboutMapDialog").dialog({
            width: 700,
            position: {
                my: 'top',
                at: 'top',
                of: $('#containerMap')
            }
        });
    }

    $aboutMapDlg.dialog("open");
    $("#aboutMapDialog a").blur(); 
}

function vibrioClickListener(e) {
    $("#loadingImg").css("display", "block");
    var screenPoint = new esri.geometry.Point(e.offsetX, e.offsetY, map.spatialReference);
    var mapPoint = map.toMap(screenPoint)


    var url;
    url = selectedService.url;
    if (url.indexOf("?") < 0){
        url += "?";
    }
    url += "&service=WMS";
    url += "&version=1.3.0";
    url += "&LAYERS=" + selectedLayer.id;
    url += "&CRS=EPSG:3857";
    url += "&REQUEST=GetFeatureInfo";
    url += "&WIDTH=" + map.width;
    url += "&HEIGHT=" + map.height;
    url += "&BBOX=" + map.extent.xmin + "," + map.extent.ymin + "," + map.extent.xmax + "," + map.extent.ymax;
    url += "&INFO_FORMAT=text/xml";
    url += "&I=" + parseInt(e.offsetX);
    url += "&J=" + parseInt(e.offsetY);
    url += "&QUERY_LAYERS=" + selectedLayer.id;
    url += "&TIME=" + $.datepicker.formatDate('yy-mm-dd', selectedDatesArray[$("#timeSlider").slider( "value" )]) + "T12:00:00.000Z"


    $.ajax({
        type: "GET",
        url: proxy + "?" + url,
        dataType: "xml",
        success: function (xml) {
            $(xml).find("FeatureInfoResponse").each(function () {
                var longitude, latitude, time, value;
                if ($(this).children("longitude").text() != "") {
                    longitude = $(this).children("longitude").text();
                }
                if ($(this).children("latitude").text() != "") {
                    latitude = $(this).children("latitude").text();
                }
                if ($(this).children("FeatureInfo").text() != "") {
                    if ($(this).children("FeatureInfo").children("time").text() != "") {
                        time = $(this).children("FeatureInfo").children("time").text();
                    }
                    if ($(this).children("FeatureInfo").children("value").text() != "") {
                        value = $(this).children("FeatureInfo").children("value").text();
                    }
                }
                var content = "<b>Longitude</b>: " + longitude
                    + "<br/><b>Latitude</b>: " + latitude
                    + "<br/><br/><b>Time</b>: " + time.substring(0, 10)
                    + "<br/><b>Value</b>: " + value;

                map.infoWindow.setTitle("Get Value result");
                map.infoWindow.setContent(content);
                map.infoWindow.show(mapPoint, map.getInfoWindowAnchor(mapPoint))
                $("#loadingImg").css("display", "none");
            })
        },
        error: function (textStatus, errorThrown) {
            $("#loadingImg").css("display", "none");
            alert("Error getting the data");
        }
    });
    dojo.disconnect(clickListener)
    $("#imgidentifybutton").css("background-color", "transparent");
    $("#imgidentifybutton").css("border", "none");
}
function addListeners(){

    $("#colourBands").on('change', function (e) {
        changeMap();     
    });
    $("#scaleMethod").on('change', function (e) {
        changeMap();     
    });  
    $("#minValue").on('change', function (e) {
        if (parseInt($("#minValue").val()) >= parseInt($("#maxValue").val())){
            $("#maxValue").val(parseInt($("#minValue").val()) + 2)
        }
        changeMap();
    });        
    $("#maxValue").on('change', function (e) {
        if (parseInt($("#maxValue").val()) <= parseInt($("#minValue").val())){
            $("#minValue").val(parseInt($("#maxValue").val()) - 2)
        }
        changeMap();
    });  
    $("#colourPalette").on('change', function(newValue){
        alert(newValue);
    }); 
}
function changeMap(){
    map.infoWindow.hide();
    if (map.layerIds.length > 1){
        map.removeLayer(map.getLayer(map.layerIds[1]))
    }
    var o = new WMSLayerTime(selectedService.url,getMapOptions());
    map.addLayer(o);
    getLegendURL();
}
function getMapOptions(){
    var options = {};
    options.version = "1.3.0";
    options.visiblelayers = [selectedLayer.id];
    options.styles = dijit.byId('colourPalette').attr('value');
    options.colorscalerange = $("#minValue").val() + "," + $("#maxValue").val();
    options.numcolorbands = $("#colourBands").val();
    if ($("#scaleMethod").val() == "linear"){
        options.logscale = false;
    }else{
        options.logscale = true;
    }
    options.time = $.datepicker.formatDate('yy-mm-dd', selectedDatesArray[$("#timeSlider").slider( "value" )]) + "T12:00:00.000Z"
    return options;
}
function getLegendURL(){
    var url = "";
    url = $.grep(selectedLayer.styles, function(e){ return e.name == dijit.byId('colourPalette').attr('value'); })[0].image;;
    url += "&COLORSCALERANGE=" + $("#minValue").val() + "," + $("#maxValue").val();
    url += "&NUMCOLORBANDS=" + $("#colourBands").val();
    if ($("#scaleMethod").val() == "linear"){
        url += "&LOGSCALE=false";
    }else{
        url += "&LOGSCALE=true";
    }    
    $("#imageLegend").attr("src", url)

}
var selectedLayer;
var selectedService;
var selectedDatesArray;
$(document).ready(function () {
    $(document).on('click', 'input[type=radio][name=mapType]', function(){
        var i = $(this).data("i");
        var j = $(this).data("j");
        //arrWMSVibrio[i].layers[j]
        selectedService = arrWMSVibrio[i];
        selectedLayer = arrWMSVibrio[i].layers[j];
        selectedDatesArray = arrWMSVibrio[i].layers[j].dimensions;

        setColourPalette();
        var startDate = arrWMSVibrio[i].layers[j].dimensions[0];
        var endDate = arrWMSVibrio[i].layers[j].dimensions[arrWMSVibrio[i].layers[j].dimensions.length - 1];

        $("#dateFrom").datepicker("destroy");     
        // a date can be selected only by using the calendar, so prevent the usage of Enter key
        $("#dateFrom").bind('keydown', function (e) {
            if (e.which == 13)
                e.stopImmediatePropagation();
        }).datepicker({
            dateFormat: "yy-mm-dd",
            firstDay: 1,
            minDate: startDate,
            maxDate: endDate,
            defaultDate: startDate,
            onSelect: function(selectedDate){
                $("#dateTo").datepicker("option", "minDate", selectedDate);
                $("#sliderDateFrom").text(selectedDate);
                var dates = [];
                selectedDate = new Date(selectedDate.split("-")[0], selectedDate.split("-")[1] - 1, selectedDate.split("-")[2])

                var toDate = $("#dateTo").datepicker("getDate");
                $.each( selectedLayer.dimensions, function( index, value ){
                    if (value >= selectedDate && value <= toDate){
                        dates.push(value);
                    }
                });
                selectedDatesArray = dates;

                setSlider();           
            }
        });
        $("#dateFrom").datepicker("setDate", startDate);

        $("#dateTo").datepicker("destroy");       
        $("#dateTo").bind('keydown', function (e) {
            if (e.which == 13)
                e.stopImmediatePropagation();
        }).datepicker({
            dateFormat: "yy-mm-dd",
            firstDay: 1,
            minDate: startDate,
            maxDate: endDate,
            defaultDate:endDate,
            onSelect: function(selectedDate){
                $("#dateFrom").datepicker("option", "maxDate", selectedDate);
                $("#sliderDateTo").text(selectedDate);
                var dates = [];
                selectedDate = new Date(selectedDate.split("-")[0], selectedDate.split("-")[1] - 1, selectedDate.split("-")[2])

                var fromDate = $("#dateFrom").datepicker("getDate");
                $.each(selectedLayer.dimensions, function (index, value) {
                    if (value <= selectedDate && value >= fromDate) {
                        dates.push(value);
                    }
                });   
                selectedDatesArray = dates;
                setSlider()
            }
        });
        $("#dateTo").datepicker("setDate", endDate);


        setSlider();
        changeMap();     
    });    

    $(document).on("slidestop", "#timeSlider", function(event, ui) {
        $("#sliderCurrentDate").text($.datepicker.formatDate('yy/mm/dd', selectedDatesArray[ui.value]));
        changeMap()
    }); 
    $(document).on("click", "#sliderLeft", function(event, ui) {
        var s = $("#timeSlider"), val = s.slider("value"), step = s.slider("option", "step");
        s.slider("value", val - 1);
        $("#sliderCurrentDate").text($.datepicker.formatDate('yy/mm/dd', selectedDatesArray[s.slider("value")]))
        changeMap()
    });
    $(document).on("click", "#sliderRight", function(event, ui) {
        var s = $("#timeSlider"), val = s.slider("value"), step = s.slider("option", "step");
        s.slider("value", val + 1);
        $("#sliderCurrentDate").text($.datepicker.formatDate('yy/mm/dd', selectedDatesArray[s.slider("value")]))
        changeMap()
    });
});



function loadMap() {
    loadVibrioMap();
    $("#divLegendDesc").html(legendDescription);
    extentMap();
}


