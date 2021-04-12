window.requirejs.config({
  baseUrl: "https://js.arcgis.com/4.18/"
});
//console.log(requirejs.s.contexts._.config);
//console.log(requirejs);
window.requirejs([
  "esri/Map",
  "esri/layers/GeoJSONLayer",
  "esri/views/MapView",
  "esri/geometry/Point"
], function (
  Map,
  GeoJSONLayer,
  MapView,
  Point
) {
  // If GeoJSON files are not on the same domain as your website, a CORS enabled server
  // or a proxy is required.
  const url = "/case-studies-map.arcgis.json";

  const template = {
    title: "{title} <a href='{url}'>open DB</a>",
    outFields: ["*"],
    content: popupContent
  };

  function popupContent(feature) {
      var div = document.createElement("div");
      // calculate the population percent change from 2010 to 2013.
      let sectors = feature.graphic.attributes.sectors_str;
      let impacts = feature.graphic.attributes.impacts_str;
      let adaptation_options = feature.graphic.attributes.adaptation_options_links;

      if (feature.graphic.attributes.image.length) {
          div.innerHTML += '<p><img src="'+feature.graphic.attributes.image+'" /></p>';
      }
      /*if (feature.graphic.attributes.description) {
          div.innerHTML += feature.graphic.attributes.description + '<br>';
      }*/
      if (sectors.length) {
          div.innerHTML += '<p style="font-size:14px;"><strong style="color:#069;">Sectors:</strong><br>'+sectors+'</p>';
      }
      div.innerHTML += '<p style="font-size:14px;"><strong style="color:#069;">Climate impacts:</strong><br>'+impacts+'</p>';
      if (adaptation_options.length) {
          div.innerHTML += '<p style="font-size:14px;"><strong>Adaptation options:</strong></p><ul><li>'+adaptation_options.split('<>').join('</li><li>')+'</li></ul>';
      }
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
        clusterRadius: "60px",
        labelPlacement: "center-center",
        clusterMinSize: "20px",
        clusterMaxSize: "40px",
        labelingInfo: [{
          // turn off deconfliction to ensure all clusters are labeled
          //deconflictionStrategy: "none",
          labelExpressionInfo: {
            expression: "Text($feature.cluster_count, '#,###')",
          },
          symbol: {
            type: "text",
            color: "#ffffff",
            borderLineSize: 0,
            //backgroundColor: "#005c96",
            font: {
              weight: "bold",
              family: "Noto Sans",
              size: "16px"
            },
          },
          labelPlacement: "center-center",
      }]
    },
    renderer: {
      type: "simple",
      symbol: {
        type: "simple-marker",
        size: 4,
        color: "#005c96"
      }
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
    center: [2, 53],
    zoom: 3,
    map: map
  });

  window.iugMapView = view;
  window.iugPoint = Point;

  geojsonLayer.on("click", function (event) {
      console.log('CLICK');
      /*
      view.center = event.mapPoint;
      zoomValue = Math.min(view.zoom + 1, 12);
      view.zoom = zoomValue;
      */
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
    //console.log(window.mapview.filter);
}
