  var map;
  var capita;
  var symboler = null;
  var styleGenerator = null;
  var thematicField = "";

  require([
    "esri/map",
    "esri/arcgis/utils",
    "esri/layers/FeatureLayer",
    "esri/symbols/SimpleFillSymbol",
    "esri/symbols/SimpleLineSymbol",
    "esri/renderers/SimpleRenderer",
    "esri/graphic",
    "esri/lang",
    "esri/Color",
    "dojo/number",
    "dojo/dom-style",
    "dijit/TooltipDialog",
    "dijit/popup",
    "esri/dijit/HomeButton",
    "esri/dijit/Search",
    "esri/dijit/Legend",
    "esri/tasks/query",
    "esri/tasks/QueryTask",
    "esri/renderers/UniqueValueRenderer",
    "esri/symbols/SimpleMarkerSymbol",
    "esri/renderers/ClassBreaksRenderer",
    "dojo/domReady!"
  ], function(Map, arcgisUtils, FeatureLayer, SimpleFillSymbol, SimpleLineSymbol, SimpleRenderer, Graphic, esriLang, Color, number, domStyle, TooltipDialog, dijitPopup, HomeButton, Search, Legend, Query, QueryTask, UniqueValueRenderer, SimpleMarkerSymbol, ClassBreaksRenderer) {

    /*var startExtent = new esri.geometry.Extent(-9011008.390480462, 2469896.302801029, 9011008.390480462, 12253835.923300989,
      new esri.SpatialReference({wkid:102100}) );
    map = new Map("mapDiv", { basemap: "streets", extent: startExtent, slider: true });
    */

    map = new Map("mapDiv", {
      //basemap: new esri.layers.ArcGISTiledMapServiceLayer("http://bio.discomap.eea.europa.eu/arcgis/rest/services/Internal/GetRestMap_Boundaries_WM/MapServer"),
      basemap: "streets",
      center: [
        12, 55
      ],
      zoom: 3,
      slider: true
    });

    //http://bio.discomap.eea.europa.eu/arcgis/rest/services/Internal/GetRestMap_Boundaries_WM/MapServer http://land.discomap.eea.europa.eu/arcgis/rest/services/Background/Background_Cashed_WGS84/MapServer

    /*
    map = new Map("mapDiv", {
      basemap: "streets",
      center: [0, 55],
      zoom: 4,
      slider: true
    });
    */
    //var baseMapLayer = new esri.layers.ArcGISTiledMapServiceLayer("http://bio.discomap.eea.europa.eu/arcgis/rest/services/Internal/GetRestMap_Boundaries_WM/MapServer"); map.addLayer(baseMapLayer);

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

    var highlightSymbol = new SimpleFillSymbol(SimpleFillSymbol.STYLE_SOLID, new SimpleLineSymbol(SimpleLineSymbol.STYLE_SOLID, new Color([255, 0, 0]), 3), new Color([125, 125, 125, 0.35]));

    var paises = new FeatureLayer("https://services.arcgis.com/LcQjj2sL7Txk9Lag/arcgis/rest/services/COUNTRIES_MA_LIG/FeatureServer/0", {
      mode: FeatureLayer.MODE_SNAPSHOT,
      outFields: [
        "COUNTRY_1",
        "LINK",
        "NATIONAL_ADA",
        "PLANS",
        "IMPACTS",
        "CLIMATE",
        "WEB_PORTAL",
        "PLATFORM",
        "UNFCCC"
      ]
    });

    var kosovo = new FeatureLayer("https://services.arcgis.com/LcQjj2sL7Txk9Lag/arcgis/rest/services/Kosovo/FeatureServer/0", {
      mode: FeatureLayer.MODE_SNAPSHOT,
      outFields: [
        "COUNTRY_1",
        "LINK",
        "NATIONAL1",
        "NATIONAL2",
        "PLANS1",
        "PLANS2",
        "IMPACTS1",
        "IMPACTS2",
        "CLIMATE1",
        "CLIMATE2",
        "MINISTRIES",
        "MINISTRI_1",
        "PLATFORM1",
        "PLATFORM2",
        "UNFCCC1",
        "UNFCCC2"
      ]
    });

    //var raster = new esri.layers.ArcGISTiledMapServiceLayer("http://bio.discomap.eea.europa.eu/arcgis/rest/services/Internal/GetRestMap_Boundaries_WM/MapServer"); map.addLayer(raster);

    function criteriaFilter() {
      var pais = $("#country").val();
      paises.setDefinitionExpression("f3 like '" + pais + "'");
    }
    //document.getElementById("criteriaButton").onclick = criteriaFilter;

    function removeLayer() {
      map.removeLayer(paises);
    }
    //document.getElementById("removeButton").onclick = removeLayer;

    function addLayer() {
      map.addLayer(paises);
    }
    //document.getElementById("addButton").onclick = addLayer;

    function zoneFilter() {
      var pais = $("#country").val();
      paises.setDefinitionExpression("f3 like '" + pais + "'");
    }
    //document.getElementById("zoneButton").onclick = zoneFilter; listen for the click event on country
    paises.on("click", function(evt) {
      var t = "$\{LINK\}";
      var content = esriLang.substitute(evt.graphic.attributes, t);
      document.location.href = content;
    });

    //listen for when the onMouseOver event fires on the countiesGraphicsLayer when fired, create a new graphic with the geometry from the event.graphic and add it to the maps graphics layer
    paises.on("mouse-over", function(evt) {
      map.graphics.clear();
      aux = "$\{" + thematicField + "\}";
      //console.log("Antes de convert: " + aux);
      var convert = esriLang.substitute(evt.graphic.attributes, aux);
      var resFinal = "<b>No links.</b>";
      if (convert.length > 1) {
        resFinal = "<b>Links:</b><br/><ul>";
        //console.log("Convert: " + convert);
        var urls = convert.split("¬");
        for (var i = 0; i < urls.length; i++) {
          if (urls[0] == "NO_VALUE") {
            resFinal = "<b>No Information available for this country.</b>";
            break;
          }
          if (urls[i].length > 0) {
            if (urls[i].length > 2) {
              var texto = urls[i].split("|");
              //console.log("Texto:"); console.log(texto);
              if (texto[1] === undefined || texto[1] == "" || texto[1] == " ") {
                texto[1] = "Link " + (i + 1);
              }
              resFinal += "<li style='line-height: 15px !important;'><a target='_blank' id='colorLink' href='" + texto[0] + "'>" + texto[1] + "</a></li>";
            }
          }
        }
        resFinal += "</ul>";
      }

      var t = "<b><div style='float:left'><b><a id='colorLink' href='$\{LINK\}'>$\{COUNTRY_1\}</a></b></div><div style='float:right'><b><a id='xDialog' style='cursor: pointer;padding-right: 5px;'>X</a></b></div><br/><hr>" + resFinal + "<br>";

      evt.graphic.attributes.LINK = evt.graphic.attributes.LINK.toLowerCase();
      var content = esriLang.substitute(evt.graphic.attributes, t);
      var highlightGraphic = new Graphic(evt.graphic.geometry, highlightSymbol);
      //map.graphics.add(highlightGraphic);

      dialog.setContent(content);

      domStyle.set(dialog.domNode, "opacity", 0.85);
      dijitPopup.open({
        popup: dialog,
        x: evt.pageX,
        y: evt.pageY
      });

      document.getElementById("xDialog").onclick = function(evt) {
        map.graphics.clear();
        dijitPopup.close(dialog);
      };
    });

    //Thematics

    paises.on("load", paisesCargadas);

    var queryTask = new QueryTask("https://services.arcgis.com/LcQjj2sL7Txk9Lag/arcgis/rest/services/COUNTRIES_MA_LIG/FeatureServer/0");

    var query = new Query();

    function paisesCargadas() {
      capita = paises;

      // Thematics Select
      var thematicName = [
        "National adaptation strategy",
        "Action plans",
        "Impacts, vulnerability and adaptation assessments",
        "Climate services / Met office",
        "Adaptation platform",
        "Web portal",
        "National Communication to the UNFCCC"
      ];
      var thematicId = [
        "NATIONAL_ADA",
        "PLANS",
        "IMPACTS",
        "CLIMATE",
        "PLATFORM",
        "WEB_PORTAL",
        "UNFCCC"
      ]

      var x = document.getElementById("thematic_field");
      for (var i = 0; i < thematicName.length; i++) {
        var option = document.createElement("option");
        option.text = thematicName[i];
        option.value = thematicId[i];
        x.add(option);
      }

      x.onchange = ejectuar;

      query.returnGeometry = false;
      query.where = "1=1";
      query.outFields = [];

      paises.on("load", null);
    }

    function ejectuar() {
      var aux = document.getElementById('thematic_field').value;
      var auxiliar = aux.substring(0, aux.indexOf("|"));
      //auxiliar = aux; console.log("Auxiliar: " + auxiliar);
      query.outFields = [];
      query.outFields.push(auxiliar);
      queryTask.execute(query, showResults);
    }

    function removeOptions(selectbox) {
      var i;
      for (i = selectbox.options.length - 1; i >= 0; i--) {
        selectbox.remove(i);
      }
    }

    var opciones2 = new Array();

    function showResults(results) {
      var opciones2 = new Array();

      var resultItems = [];
      var resultCount = results.features.length;
      for (var i = 0; i < resultCount; i++) {
        var featureAttributes = results.features[i].attributes;
        for (var attr in featureAttributes) {
          //   resultItems.push("<b>" + attr + ":</b>  " + featureAttributes[attr] + "<br>");
          opciones2.push(featureAttributes[attr]);
        }

        // resultItems.push("<br>");
      }
    }

    function buttonClicked() {
      var atributosColores1 = ["null"];
      var atributosColores2 = ["#0080FF"];
      var atributosColores3 = ["#808080"];
      var renderer = null;

      // Dependiendo del tipo de geometría se usa un symbolizer u otro.
      switch (capita.geometryType) {
        case "esriGeometryPoint":
          symboler = pointSymboler;
          break;
        case "esriGeometryPolygon":
          symboler = polygonSymboler;
          break;

        default:
          break;
      }

      var campito = null;
      thematicField = document.getElementById('thematic_field').value;
      var campitoName = thematicField;
      //campitoName = thematicField; console.log("thematicField: " + thematicField); console.log("campitoName: " + campitoName);
      for (var i = 0; i < capita.fields.length; i++) {
        if (capita.fields[i].name == campitoName) {
          campito = capita.fields[i];
        }
      }

      //Depending on field type -> Renderer type.
      switch (campito.type) {
        case "esriFieldTypeString":
          styleGenerator = makeRendererUniqueValue;
          renderer = makeStyle2String(atributosColores1, atributosColores2, atributosColores3, styleGenerator, symboler);
          break;
        default:
          styleGenerator = makeStyle2Number;
          renderer = makeStyle2Number(atributosColores1, atributosColores2, atributosColores3, styleGenerator, symboler);

          break;
      }
      capita.setRenderer(renderer);
      capita.refresh();
    }

    function makeStyle2String(atributosColores1, atributosColores2, atributosColores3, styleGenerator2, symbolizer) {
      var defaultSymbol = symbolizer('#89CD66');

      var aux = document.getElementById('thematic_field').value;
      var renderer2 = styleGenerator2(defaultSymbol, aux);
      //console.log("Atributos"); console.log(atributosColores1); console.log(atributosColores2);
      for (var i = 0; i < atributosColores1.length; i++) {
        //console.log("Addvalue: " + atributosColores1[i] + "------" + symbolizer(atributosColores2[i]))
        renderer2.addValue(atributosColores1[i], symbolizer(atributosColores2[i]));
        renderer2.addValue("", symbolizer(atributosColores2[i]));
        renderer2.addValue(" ", symbolizer(atributosColores2[i]));
        renderer2.addValue("NO_VALUE", symbolizer(atributosColores3[i]));
      }
      return renderer2;
    }

    function polygonSymboler(color) {
      return (new SimpleFillSymbol().setColor(Color.fromHex(color)));
    }

    function makeRendererUniqueValue(defaultSymbol, valor) {
      //console.log("RendererUniqueValue"); console.log(defaultSymbol); console.log(valor);
      return (new UniqueValueRenderer(defaultSymbol, valor));
    }

    document.getElementById('botoncito1').onclick = buttonClicked;
    // END Thematics

    map.addLayer(paises);
    map.addLayer(kosovo);
  });

  function goCountry(combo) {
    if (combo.value != "%") {
      document.location.href = combo.value.toLowerCase();
    }
  }

  function loadCountries() {
    var z = document.getElementById("country");
    for (var j = 0; j < capita.graphics.length; j++) {
      if (capita.graphics[j].attributes.NATIONAL_ADA != "NO_VALUE") {
        var option = document.createElement("option");
        option.text = capita.graphics[j].attributes.COUNTRY_1;
        option.value = capita.graphics[j].attributes.LINK;
        z.add(option);
      }
    }

    var options = $('#country option');
    var arr = options.map(function(_, o) {
      return {
        t: $(o).text(),
        v: o.value
      };
    }).get();
    arr.sort(function(o1, o2) {
      return o1.t.toUpperCase() > o2.t.toUpperCase() ? 1 : o1.t.toUpperCase() < o2.t.toUpperCase() ? -1 : 0;
    });
    options.each(function(i, o) {
      o.value = arr[i].v;
      $(o).text(arr[i].t);
    });

    $("#country").prepend("<option value=''>Choose a country</option>").val('');
  }

  function checkLayer() {
    //          debugger ;
    if (capita.graphics.length != 0) {
      //console.log("Definida, cargo combo"); console.log(capita.graphics.length);
      loadCountries();
      document.getElementById('botoncito1').click();
    } else {
      //console.log("Rellamada");
      setTimeout(checkLayer, 200);
    }
  }

  $(window).load(function() {
    setTimeout(checkLayer, 500);
  });
