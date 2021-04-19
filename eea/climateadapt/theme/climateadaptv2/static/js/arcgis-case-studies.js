// global: $

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
  const url = "./case-studies-map.arcgis.json";

  const template = {
    title: "<strong>{title}</strong> <a href='{url}'>open DB</a>",
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
      div.innerHTML += '<p><cener><img src="'+feature.graphic.attributes.image+'" /></cener></p>';
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
    $('.esri-component.esri-popup').css('display', 'block');
    return div;
  }

  // const renderer = {
  //   type: "simple",
  //   field: "mag",
  //   symbol: {
  //     type: "simple-marker",
  //     color: "orange",
  //     outline: {
  //       color: "white"
  //     }
  //   },
  //   visualVariables: [{
  //     type: "size",
  //     field: "mag",
  //     stops: [{
  //         value: 2.5,
  //         size: "4px"
  //       },
  //       {
  //         value: 8,
  //         size: "40px"
  //       }
  //     ]
  //   }]
  // };

  function onShow(feature) {
    feature.graphic.visible = false;
    var geo = feature.graphic.geometry;   // .latitude, .longitude

    $('.esri-hide2').closest('.esri-component.esri-popup').css('display', 'none');
    view.center = geo;
    zoomValue = Math.min(view.zoom + 1, 12);
    view.zoom = zoomValue;
      // view.center = event.mapPoint;
      // zoomValue = Math.min(view.zoom + 1, 12);
      // view.zoom = zoomValue;

    return "<div id='popup-cluster'><div>";
  }

  const geojsonLayer = new GeoJSONLayer({
    url: url,
    featureReduction: {
      type: "cluster",
      clusterRadius: "60px",
      labelPlacement: "center-center",
      clusterMinSize: "20px",
      clusterMaxSize: "40px",
      popupEnabled: true,
      popupTemplate: {
        title: "hello",
        content: onShow,
        actions: [
          {
            // This text is displayed as a tooltip
            title: "Zoom out",
            // The ID by which to reference the action in the event handler: {
            id: "zoom-out",
            // Sets the icon font used to style the action button
            className: "esri-hide2 esri-icon-zoom-out-magnifying-glass"
          }
        ],
        declaredClass: "esri-hide"
      },
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
        size: 8,
        color: "#005c96",
        outline: {
          width: 0
        }
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
    map: map,
    popup: {
      actions: [],
      dockEnabled: false,
      dockOptions:{buttonEnabled: false}
    }
  });

  window.iugMapView = view;
  window.iugPoint = Point;

  // view.popup.on("trigger-action", function(event){
  //   console.log('trigger');
  //   // If the zoom-out action is clicked, fire the zoomOut() function
  //   if(event.action.id === "zoom-out"){
  //     // zoomOut();
  //   }
  // });

  view.on("click", function (event) {
    console.log('CLICK', {event, view, map});
    return true;
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
  $('#arcgis_case_study_form input[name="impacts"], #arcgis_case_study_form input[name="sectors"]').change(function(){
    updateItems();
  });
});

function updateItems(type) {
  const where = [];
  const whereImpacts = [];
  const whereSectors = [];
  where.push( "portal_type LIKE 'casestudy'" );

  const impacts = $("#arcgis_case_study_form input[name='impacts']:checked");
  for (index=0;index<impacts.length;index++) {
    whereImpacts.push( "impacts LIKE '%"+impacts[index].getAttribute('value')+"%'" );
  }
  if (whereImpacts.length) {
    where.push('('+whereImpacts.join(' OR ')+')');
  }

  const sectors = $("#arcgis_case_study_form input[name='sectors']:checked");
  for (index=0; index<sectors.length; index++) {
    whereSectors.push( "sectors LIKE '%"+sectors[index].getAttribute('value')+"%'" );
  }
  if (whereSectors.length) {
    where.push('('+whereSectors.join(' OR ')+')');
  }

  window.mapview.filter = {where: where.join(' AND ')};
  //console.log(window.mapview.filter);
}
