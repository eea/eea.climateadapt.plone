requirejs.config({
  baseUrl: "https://js.arcgis.com/4.18/"
});
console.log(requirejs.s.contexts._.config);
console.log(requirejs);
requirejs([
  "esri/Map",
  "esri/layers/GeoJSONLayer",
  "esri/views/MapView"
], function (
  Map,
  GeoJSONLayer,
  MapView
) {
  // If GeoJSON files are not on the same domain as your website, a CORS enabled server
  // or a proxy is required.
  //const url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson";
  //url = "http://local.test.com/arcgis.json";
  const url = "/arcgis.json";

  // Paste the url into a browser's address bar to download and view the attributes
  // in the GeoJSON file. These attributes include:
  // * mag - magnitude
  // * type - earthquake or other event such as nuclear test
  // * place - location of the event
  // * time - the time of the event
  // Use the Arcade Date() function to format time field into a human-readable format

  const template = {
    title: "{title}",
    outFields: ["*"],
    content: popupContent
  };

  function popupContent(feature) {
      var div = document.createElement("div");
      // calculate the population percent change from 2010 to 2013.
      let sectors = feature.graphic.attributes.sectors_str;
      let impacts = feature.graphic.attributes.impacts_str;
      let adaptation_options = feature.graphic.attributes.adaptation_options;

      if (feature.graphic.attributes.image.length) {
          div.innerHTML += '<br><img src="'+feature.graphic.attributes.image+'" style=\"float: left;margin: 0 15px 0 0;\" />';
      }
      if (feature.graphic.attributes.description) {
          div.innerHTML += feature.graphic.attributes.description + '<br>';
      }
      if (adaptation_options.length) {
          div.innerHTML += '<br><strong>Adaptation options:</strong><ul><li>'+adaptation_options.split('<>').join('</li><li>')+'</li></ul>';
      }
      if (sectors.length) {
          div.innerHTML += '<br><strong>Sectors:</strong><ul><li>'+sectors.split(',').join('</li><li>')+'</li></ul>';
      }
      div.innerHTML += '<br><strong>Impacts:</strong><ul><li>'+impacts.split(',').join('</li><li>')+'</li></ul>';
      div.innerHTML += '<br><a href="'+feature.graphic.attributes.url+'">... read more ...</a>';
      return div;
  }

  const renderer = {
    type: "simple",
    field: "mag",
    symbol: {
      type: "simple-marker",
      color: "orange",
      outline: {
        color: "white"
      }
    },
    visualVariables: [{
      type: "size",
      field: "mag",
      stops: [{
          value: 2.5,
          size: "4px"
        },
        {
          value: 8,
          size: "40px"
        }
      ]
    }]
  };

  const geojsonLayer = new GeoJSONLayer({
    url: url,
    featureReduction: {
        type: "cluster",
        //clusterRadius: "40px",
        //labelPlacement: "center-center",
        //clusterMinSize: "40px",
        //clusterMaxSize: "120px",
        labelingInfo: [{
          // turn off deconfliction to ensure all clusters are labeled
          //deconflictionStrategy: "none",
          labelExpressionInfo: {
            expression: "Text($feature.cluster_count, '#,###')"
          },
          symbol: {
            type: "text",
            color: "#ffffff",
            font: {
              weight: "bold",
              family: "Noto Sans",
              size: "16px"
            },
          },
          labelPlacement: "center-center",
        }]
    },
    copyright: "USGS Earthquakes",
    popupTemplate: template
    //renderer: renderer //optional
  });

  const map = new Map({
    basemap: "gray-vector",
    layers: [geojsonLayer]
  });

  const view = new MapView({
    container: "arcgisDiv",
    center: [8, 53],
    zoom: 2.7,
    map: map
  });

  view.filter = {
      where: "portal_type 'casestudy'"
  };

  view.whenLayerView(geojsonLayer).then(function(layerView) {
    window.mapview = layerView;
    layerView.filter = {
      where: "portal_type LIKE 'casestudy'"
    };

  });
});

$( document ).ready(function() {
    $('#arcgis_case_study_form #CaseStudySectors, #arcgis_case_study_form #CaseStudyImpacts').change(function(){
        updateItems();
    });
});

function updateItems(type) {
    const where = [];
    where.push( "portal_type LIKE 'casestudy'" );

    const impacts = $("#arcgis_case_study_form select[name='impacts']").val();
    if (impacts.length) {
        where.push( "impacts LIKE '%"+impacts+"%'" );
    }

    const sectors = $("#arcgis_case_study_form select[name='sectors']").val();
    if (sectors.length) {
        where.push( "sectors LIKE '%"+sectors+"%'" );
    }


    window.mapview.filter = {where: where.join(' AND ')};
  console.log(window.mapview.filter);
}
//window.mapview.filter = {where: "name  LIKE 'Ion' and direction LIKE 'est'"}
