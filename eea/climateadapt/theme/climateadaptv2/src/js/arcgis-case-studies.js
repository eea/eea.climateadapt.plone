// global: $
window.requirejs.config({
  baseUrl: "https://js.arcgis.com/4.18/"
});
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
  const url = "./case-studies-map.arcgis.json";

  const template = {
    title: "<strong>{title}</strong> <a href='{url}'>open DB</a>",
    //location: centerPoint,
    outFields: ["*"],
    content: popupContent
  };

  function popupContent(feature) {
    var geo = feature.graphic.geometry;   // .latitude, .longitude
    /*
    1->8
    2->7
    3->4
    4->2
    5->1
    6->0.9
    7->0.9
    8->0.2
    9->0.1
    10->0.05
    11->0.4
    12->0.2
    */
    zoomAdjustment = [8, 7, 4, 2, 1, 0.9, 0.7, 0.2, 0.1, 0.05, 0.04, 0.02 ];
    viewZoom = parseInt(view.zoom, 10);
    if (viewZoom && zoomAdjustment.length > viewZoom) {
        view.goTo({center:[geo.longitude, geo.latitude-zoomAdjustment[viewZoom-1]]});
    } else {
        view.goTo({center:[geo.longitude, geo.latitude]});
    }

    var div = document.createElement("div");

    var sectors = feature.graphic.attributes.sectors_str;
    var impacts = feature.graphic.attributes.impacts_str;
    var adaptation_options = feature.graphic.attributes.adaptation_options_links;

    if (feature.graphic.attributes.image.length) {
      div.innerHTML += '<span style="background-color:#ddd;display:block;margin-bottom:10px;"><center><img style="max-height:133px;" src="'+feature.graphic.attributes.image+'" /></center></span>';
    }
    if (sectors.length) {
      div.innerHTML += '<p style="font-size:13px;margin-bottom:10px;""><span style="color:#069;">Adaptation sectors:</span> '+sectors.split(',').join(', ')+'</p>';
    }
    div.innerHTML += '<p style="font-size:13px;margin-bottom:10px;""><span style="color:#069;">Climate impacts:</span> '+impacts+'</p>';
    if (adaptation_options.length) {
      div.innerHTML += '<p class="cs_adaptation_casestudies" style="font-size:13px;margin-bottom:5px;""><span style="color:#069;">Adaptation options:</span> '+adaptation_options.split('<>').join('; ')+'</p>';
    }
    $('.esri-component.esri-popup').css('display', 'block');
    return div;
  }

  function onShow(feature) {
    feature.graphic.visible = false;
    var geo = feature.graphic.geometry;   // .latitude, .longitude

    $('.esri-component.esri-popup').css('display', 'none');
    //view.center = geo;
    view.goTo({center:[geo.longitude, geo.latitude],animation: true});
    zoomValue = Math.min(view.zoom + 1, 12);
    view.zoom = zoomValue;

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
            title: "hello4",
            content: onShow
        },
        labelingInfo: [{
            labelExpressionInfo: {
                expression: "Text($feature.cluster_count, '#,###')",
            },
            symbol: {
                type: "text",
                color: "#ffffff",
                borderLineSize: 0,
                font: {
                    weight: "bold",
                    family: "Noto Sans",
                    size: "16px"
                },
            },
            labelPlacement: "center-center",
        }],
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
        },
        visualVariables: [{
            type: "color",
            field: "origin_adaptecca",
            stops: [
                { value: 10, color: "#00FFFF" },
                { value: 20, color: "#005c96" }
            ]
        }],
    },
    popupTemplate: template
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
      //dockEnabled: false,
      alignment: "bottom-center",
      dockOptions:{
          buttonEnabled: false
      }
    }
  });

  window.iugMapView = view;
  window.iugPoint = Point;

  view.filter = {
    where: "portal_type 'casestudy'"
  };

  view.whenLayerView(geojsonLayer).then(function(layerView) {
    window.mapview = layerView;
    updateItems()
    //layerView.filter = {
    //  where: "portal_type LIKE 'casestudy' and (sectors LIKE '%URBAN%')"
    //};

  });
});

var changeSkipClicks = false;
$( document ).ready(function() {
  $('#arcgis_case_study_form input[name="impacts"], #arcgis_case_study_form input[name="sectors"], #arcgis_case_study_form input[name="ipccs"], #arcgis_case_study_form input[name="ktms"]').change(function(){
    if (!changeSkipClicks) {
      buttonReset();
      updateItems();
    }
    changeSkipClicks = false;
  });
  $('#arcgis_case_study_form h4').click(function() {
      filterDisplayMode(this);
  })
  $(".case-study-row .case-study-div a.reset").click(function() {
      $(".case-study-row .case-study-div input:checked").click();
      $(".case-study-row .case-study-div h4").removeClass('active');
      $(".case-study-row .case-study-div form p").hide();
      return false;
  });
  buttonReset();

  elements = $('#arcgis_case_study_form h4');
  for (i=0;i<elements.length;i++) {
    //filterDisplayMode(elements[i]);
  };

  pageLoadMap();
});

function pageLoadMap() {
    params = new URLSearchParams(window.location.search);
    sectorsData = params.get('sectors');
    if (sectorsData) {
      sectors = sectorsData.split(',');
      if (sectors.length) {
        $('.cs_filter_sector_div h4').click();
        changeSkipClicks = true;
      }
      for (i=0;i<sectors.length;i++) {
        $('.cs_filter_sector_div input[value="'+sectors[i]+'"]').click();
      }
    }
}

function buttonReset() {
    if ($(".case-study-row .case-study-div input:checked").length >0) {
        $(".case-study-row .case-study-div a.reset").show();
    } else {
        $(".case-study-row .case-study-div a.reset").hide();
    }
}

function filterDisplayMode(element) {
    if ($(element).hasClass('active')) {
        $(element).removeClass('active').parent().find('p').hide();
    } else {
        $(element).addClass('active').parent().find('p').show();
    }
}
function updateItems(type) {
  const where = [];
  const whereImpacts = [];
  const whereSectors = [];
  const whereIpccs = [];
  const whereKtms = [];

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

  const ipccs = $("#arcgis_case_study_form input[name='ipccs']:checked");
  for (index=0; index<ipccs.length; index++) {
    whereIpccs.push( "ipccs LIKE '%"+ipccs[index].getAttribute('value')+"%'" );
  }
  if (whereIpccs.length) {
    where.push('('+whereIpccs.join(' OR ')+')');
  }

  const ktms = $("#arcgis_case_study_form input[name='ktms']:checked");
  for (index=0; index<ktms.length; index++) {
    whereKtms.push( "ktms LIKE '%"+ktms[index].getAttribute('value')+"%'" );
  }
  if (whereKtms.length) {
    where.push('('+whereKtms.join(' OR ')+')');
  }


  window.mapview.filter = {where: where.join(' AND ')};
  //console.log(window.mapview.filter);
}
