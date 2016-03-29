var map;
var matrix = new Object();
var citiesUrl = new Array();
 // Get field layer name of Climate Impacts and Adaptation Sectors
function setMatrix(){
matrix["Droughts"] = "f6";
matrix["Extreme Temperatures"] = "f7";
matrix["Flooding"] = "f8";
matrix["Forest Fires"] = "f9";
matrix["Ice and Snow"] = "f10";
matrix["Sea Level Rise"] = "f11";
matrix["Storms"] = "f12";
matrix["Water Scarcity"] = "f13";
matrix["Agriculture and Forest"] = "f17";
matrix["Biodiversity"] = "f18";
matrix["Coastal areas"] = "f19";
matrix["Disaster Risk Reduction"] = "f20";
matrix["Financial"] = "f21";
matrix["Health"] = "f22";
matrix["Infrastructure"] = "f23";
matrix["Marine and Fisheries"] = "f24";
matrix["Energy"] = "f25";
matrix["Tourism"] = "f26";
matrix["Urban"] = "f27";
matrix["Water Management"] = "f28";
}

function getMatrix(key){
return matrix[key];
}

require([
"esri/map",
"esri/arcgis/utils", "esri/layers/FeatureLayer",
      "esri/symbols/SimpleFillSymbol", "esri/symbols/SimpleLineSymbol",
      "esri/renderers/SimpleRenderer", "esri/graphic", "esri/lang",
      "esri/Color", "dojo/number", "dojo/dom-style",
      "dijit/TooltipDialog", "dijit/popup", "esri/dijit/HomeButton", "esri/dijit/Search", "esri/dijit/Legend","dojo/domReady!"
], function(Map, arcgisUtils, FeatureLayer,
      SimpleFillSymbol, SimpleLineSymbol,
      SimpleRenderer, Graphic, esriLang,
      Color, number, domStyle,
      TooltipDialog, dijitPopup, HomeButton, Search, Legend){

  map = new Map("mapDiv", {
        basemap: "streets",
        center: [12, 55],
        zoom: 3,
        slider: true
      });

  var home = new HomeButton({
    map: map
    }, "HomeButton");
    home.startup();
    /*
       var s = new Search({
          map: map
       }, "search");
       s.startup();
  */
      dialog = new TooltipDialog({
        id: "tooltipDialog",
        style: "position: absolute; width: 250px; font: normal normal normal 10pt Helvetica;z-index:100"
      });
      dialog.startup();



      var highlightSymbol = new SimpleFillSymbol(
        SimpleFillSymbol.STYLE_SOLID,
        new SimpleLineSymbol(
          SimpleLineSymbol.STYLE_SOLID,
          new Color([255,0,0]), 3
        ),
        new Color([125,125,125,0.35])
      );

  // Layer of cities.
      var ciudades = new FeatureLayer("http://services.arcgis.com/LcQjj2sL7Txk9Lag/arcgis/rest/services/Efnau/FeatureServer/0", {
        mode: FeatureLayer.MODE_SNAPSHOT,
    outFields: ["f1", "f2", "f3", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f20", "f21", "f22", "f23", "f24", "f25", "f26", "f27", "f28"]
      });

  // Filter cities based on criterias (Adaptation sectors, Climate Impacts, Stage of implementation)
  function criteriaFilter() {
    var sectors = $("#sectors option:selected").text();
    var impacts = $("#impacts option:selected").text();
    var stages = $("#stage option:selected").text();
    var cities = "";

    if(sectors == "All"){ sectors="";}
    if(impacts == "All"){ impacts="";}
    if(stages == "All"){ stages="";}

    //Fill the combo of cities with cities that have these criteria
    //url: "http://adapt-test.eea.europa.eu/api/jsonws/Mayors-ADAPT-portlet.data/get-cities-by-criteria?countries=&sectors=" + sectors + "&impacts=" + impacts + "&stages=" + stages,
    $.ajax({
    url: "/@@citiesxyz?countries=&sectors=" + sectors + "&impacts=" + impacts + "&stages=" + stages,
    processData: true,
    async: true,
    type: "GET",
    dataType: "json",
    success: function (jsonObject) {
      // var rows = $(response);
      // var jsonObject = eval(response);
      var selectObject = $("#city");
      selectObject.empty();
      var i=1;
      selectObject[0].options[0] = new Option("Select city","");
      for (var key in jsonObject){
        var value="", text="";
        cities += "'" + key + "',";
        selectObject[0].options[i++] = new Option(key,jsonObject[key]);
      }
      if(cities.length >0){
        cities = cities.substring(0,cities.length-1);
      }

      //console.log("Cities:" + cities);
      //ciudades.setDefinitionExpression("f1 in (" + cities + ")");
      var defExpresion = "";
      if(sectors != ""){
        defExpresion += getMatrix(sectors) + "='Yes'";
      }
      if(impacts != ""){
        if (defExpresion.length > 0)
           defExpresion += " AND ";
        defExpresion += getMatrix(impacts) + "='Yes'";
      }
      if(stages != ""){
        if (defExpresion.length > 0)
           defExpresion += " AND ";
        if(stages.indexOf(".") > 0){
          stages = stages.substring(0,stages.length-1);
        }
        defExpresion += "f14 = '" + stages + "'";
      }

      // Apply filter to layer
      //console.log("Filtro: " + defExpresion);
      ciudades.setDefinitionExpression(defExpresion);
    },
    error: function (jqxhr, textStatus) {
      if (textStatus != "abort" && jqxhr.status != 403 && jqxhr.status != 901 && jqxhr.readyState != 0) {
        alert("ERROR loading " + url_ws);
      }
    }
    });
  }
  //document.getElementById("criteriaButton").onclick = criteriaFilter;
  document.getElementById("impacts").onchange = criteriaFilter;
  document.getElementById("sectors").onchange = criteriaFilter;
  document.getElementById("stage").onchange = criteriaFilter;

  //Fill the other combo of cities with cities of the country selected
  function zoneFilter() {
    var pais = $("#country option:selected").text();
    if(pais == "All"){ pais="%";}
    ciudades.setDefinitionExpression("f3 like '" + pais + "'");
    if(pais == "%"){ pais="";}
    //Fill the combo with cities of this country
    $.ajax({
    url: "/@@citiesxyz?countries=" + pais + "&sectors=&impacts=&stages=",
    processData: true,
    async: true,
    type: "GET",
    dataType: "json",
    success: function (jsonObject) {
      // var rows = $(response);
      // var jsonObject = eval(response);
      var selectObject = $("#cityCountry");
      selectObject.empty();
      var i=1;
      selectObject[0].options[0] = new Option("Select city","");
      for (var key in jsonObject){
        var value="", text="";
        selectObject[0].options[i++] = new Option(key,jsonObject[key]);
      }

    },
    error: function (jqxhr, textStatus) {
      if (textStatus != "abort" && jqxhr.status != 403 && jqxhr.status != 901 && jqxhr.readyState != 0) {
        alert("ERROR loading " + url_ws);
      }
    }
    });

  }
  //document.getElementById("zoneButton").onclick = zoneFilter;
  document.getElementById("country").onchange = zoneFilter;

  /*
  // On cities mouse-out close the tooltip
  ciudades.on("mouse-out", function(evt){
      map.graphics.clear();
        dijitPopup.close(dialog);
  });
  */
  function closeTooltip(){
    map.graphics.clear();
    dijitPopup.close(dialog);
  }

      //listen for when the onMouseOver event fires on the countiesGraphicsLayer
      //when fired, create a new graphic with the geometry from the event.graphic and add it to the maps graphics layer
      ciudades.on("mouse-over", function(evt){
    var cImpacts="", aSectors="";
    var filterFunction = function(value) {
      if ((value !== ' ') & (value !== 'No')) {

      return true;
      };
    };

    var filteredResults = esriLang.filter(evt.graphic.attributes, filterFunction);
    // Construct the tooltip only with the city's criteria
    for (att in filteredResults) {
      switch (att) {
        case "f6":
          cImpacts = cImpacts + "<b>&nbsp;&nbsp;Droughts</b><br>";
          break;
        case "f7":
          cImpacts = cImpacts + "<b>&nbsp;&nbsp;Extreme Temperatures</b><br>";
          break;
        case "f8":
          cImpacts = cImpacts + "<b>&nbsp;&nbsp;Flooding</b><br>";
          break;
        case "f9":
          cImpacts = cImpacts + "<b>&nbsp;&nbsp;Forest Fires</b><br>";
          break;
        case "f10":
          cImpacts = cImpacts + "<b>&nbsp;&nbsp;Ice and Snow</b><br>";
          break;
        case "f11":
          cImpacts = cImpacts + "<b>&nbsp;&nbsp;Sea Level Risk</b><br>";
          break;
        case "f12":
          cImpacts = cImpacts + "<b>&nbsp;&nbsp;Storms</b><br>";
          break;
        case "f13":
          cImpacts = cImpacts + "<b>&nbsp;&nbsp;Water Scarcity</b><br>";
          break;
        case "f17":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Agriculture and Forest</b><br>";
          break;
        case "f18":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Biodiversity</b><br>";
          break;
        case "f19":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Coastal areas</b><br>";
          break;
        case "f20":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Disaster Risk Reduction</b><br>";
          break;
        case "f21":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Financial</b><br>";
          break;
        case "f22":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Health</b><br>";
          break;
        case "f23":
            aSectors = aSectors + "<b>&nbsp;&nbsp;Infrastructure</b><br>";
            break;
        case "f24":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Marine and Fisheries</b><br>";
          break;
        case "f25":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Energy</b><br>";
          break;
        case "f26":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Tourism</b><br>";
          break;
        case "f27":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Urban</b><br>";
          break;
        case "f28":
          aSectors = aSectors + "<b>&nbsp;&nbsp;Water management</b><br>";
          break;
        default:
          break;
      }
      //console.log("ATT: " + att + " -- " + filteredResults[att] + ".");
    };

          var t = "<b><div style='float:left'>$\{f1\}</div><div style='float:right'><b><a id='xDialog' style='cursor: pointer;padding-right: 5px;'>X</a></b></div><br/></b><hr>Local Authority: <b>$\{f2\}</b><br>Country: <b>$\{f3\}</b><br>Climate Impacts:<br>" + cImpacts + "Adaptation Sectors:<br>" + aSectors + "Stage of implementation cycle: <b>$\{f14\}</b><br>Adaptation strategy adopted?: <b>$\{f15\}</b><br>Good practice/Spotlight Item: <b>$\{f16\}</b><br><a id='linkCity' href='enlaceCiudad'>Full city profile</a><br>";

        var content = esriLang.substitute(evt.graphic.attributes,t);
    var inicio = content.indexOf("enlaceCiudad");
    var fin = content.indexOf("'>Full");

      var cityName = "$\{f1\}";
    var ciudad = esriLang.substitute(evt.graphic.attributes,cityName);
      content = content.substring(0,inicio) + citiesUrl[ciudad] + content.substring(fin);

        var highlightGraphic = new Graphic(evt.graphic.geometry,highlightSymbol);
        map.graphics.add(highlightGraphic);

        dialog.setContent(content);

        domStyle.set(dialog.domNode, "opacity", 0.85);
        dijitPopup.open({
          popup: dialog,
          x: evt.pageX,
          y: evt.pageY
        });

    document.getElementById("xDialog").onclick= function(evt){
      map.graphics.clear();
      dijitPopup.close(dialog);
    };
      });


      map.addLayer(ciudades);

  var legend = new Legend({
    map: map,
    layerInfos:[
          {
            layer: ciudades, title: "Stage of implementation"
          }
    ]}, "legendDiv");
  legend.startup();
});

  // First load of all cities
function loadAllCities(combo){
  $.ajax({
  // url: "/api/jsonws/Mayors-ADAPT-portlet.data/get-cities-by-criteria?countries=&sectors=&impacts=&stages=&cmd={%22%2FMayors-ADAPT-portlet.data%2Fget-cities-by-criteria%22%3A{}}",
  url: "/@@citiesxyz",
  // processData: true,
  dataType: "json",
  async: true,
  type: "GET",
  dataType: "json",
  success: function (jsonObject) {
  // var rows = $(response);
  // var jsonObject = eval(response);
  // var jsonObject = response;
    var selectObject = $("#"+combo);
    selectObject.empty();;
    var i=1;
    selectObject[0].options[0] = new Option("Select city","");
    for (var key in jsonObject){
      var value="", text="";
      citiesUrl[key] = jsonObject[key];
      selectObject[0].options[i++] = new Option(key,jsonObject[key]);
    }
  },
  error: function (jqxhr, textStatus) {
    if (textStatus != "abort" && jqxhr.status != 403 && jqxhr.status != 901 && jqxhr.readyState != 0) {
      alert("ERROR loading Cities");
    }
  }
  });
}

  // Load of criterias combos
function loadCombo(element,url_ws){
  $.ajax({
    url: "/@@" + url_ws,
    processData: true,
    async: true,
    type: "GET",
    dataType: "json",
    success: function (jsonObject) {
      // debugger;
      // var rows = $(response);
      // var jsonObject = eval(response);
      var selectObject = $("#"+element);
      selectObject[0].options[0] = new Option("All","%");
      var i=1;
        for (var key in jsonObject){
          var value="", text="";
        selectObject[0].options[i++] = new Option(jsonObject[key][1],jsonObject[key][0]);
        }

    },
    error: function (jqxhr, textStatus) {
      if (textStatus != "abort" && jqxhr.status != 403 && jqxhr.status != 901 && jqxhr.readyState != 0) {
          alert("ERROR loading " + url_ws);
    }
    }
  });
}

// Show/hide the legend
function toogleLegend(){
  $("#legendDiv").toggle();
  $("#xButton").toggle();
}


$(window).load(function() {
// First of all load the criterias' combos and the cities' combo
loadCombo("country", "a_m_country");
loadCombo("impacts", "b_m_climate_impacts");
loadCombo("sectors", "b_m_sector");
loadCombo("stage", "c_m_stage_of_the_implementation_cycle");
loadAllCities("cityCountry");
loadAllCities("city");
setMatrix();

// If user select a city go to city's page
$("#cityCountry").change(function() {
  var item=$(this);
  var city = item.val();
  //document.location.href = "http://adapt-test.eea.europa.eu/city-profile/-/asset_publisher/d2NDUiwKMV83/content/" + city.toLowerCase();
  document.location.href = city;
});

$("#city").change(function() {
  var item=$(this);
  var city = item.val();
  //document.location.href = "http://adapt-test.eea.europa.eu/city-profile/-/asset_publisher/d2NDUiwKMV83/content/" + city.toLowerCase();
  document.location.href = city;
});

});
