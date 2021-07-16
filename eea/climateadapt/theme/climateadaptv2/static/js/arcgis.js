require(["esri/Map", "esri/layers/GeoJSONLayer", "esri/views/MapView"], function (
  Map,
  GeoJSONLayer,
  MapView
) {
  // If GeoJSON files are not on the same domain as your website, a CORS enabled server
  // or a proxy is required.
  //const url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson";
  //url = "http://local.test.com/arcgis.json";
  url = "/arcgis.json";

  // Paste the url into a browser's address bar to download and view the attributes
  // in the GeoJSON file. These attributes include:
  // * mag - magnitude
  // * type - earthquake or other event such as nuclear test
  // * place - location of the event
  // * time - the time of the event
  // Use the Arcade Date() function to format time field into a human-readable format

  const template = {
    title: "{title}",
    content: "",
    fieldInfos: [
      {
        fieldName: 'time',
        format: {
          dateFormat: 'short-date-short-time'
        }
      }
    ]
  };

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
        clusterRadius: "40px",
        labelPlacement: "center-center",
        clusterMinSize: "40px",
        clusterMaxSize: "40px",
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
            }
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
    center: [8, 56],
    zoom: 3,
    map: map
  });

  view.filter = {
      where: "name  LIKE 'Ion'",
      //where: "mag >5.4",
  };

  view.whenLayerView(geojsonLayer).then(function(layerView) {
    console.log('whenLayerView', layerView);

    window.mapview = layerView;
    layerView.filter = {
      where: "where: ''",
      //where: "mag>5.4",
    };

  });
});

$( document ).ready(function() {

    $('#myArcgisTab a').click(function(){
console.log($(this).attr('data-tag'));
        updateItems($(this).attr('data-tag'));
    });
    $('#CaseStudySectors, #CaseStudyImpacts').change(function(){
        updateItems('cs');
    });
    $('#AdaptationOptionSectors, #AdaptationOptionImpacts').change(function(){
        updateItems('ao');
    });
});

function updateItems(type) {
    if (type=='ao') {
        portal_type = 'adaptationoption';
    } else {
        portal_type = 'casestudy';
    }
    where = [];
    where.push( "portal_type LIKE '"+portal_type+"'" );

    impacts = $("select[name='"+type+"_impacts']").val();
console.log('IMPACTS:', "select[name='"+type+"_impacts']", impacts);
    if (impacts.length) {
        where.push( "impacts LIKE '%"+impacts+"%'" );
    }

    sectors = $("select[name='"+type+"_sectors']").val();
console.log('SECTORS:', "select[name='"+type+"_sectors']", sectors);
    if (sectors.length) {
        where.push( "sectors LIKE '%"+sectors+"%'" );
    }


    window.mapview.filter = {where: where.join(' AND ')};
console.log(where.join(' AND '));
console.log(window.mapview.filter);
}
//window.mapview.filter = {where: "name  LIKE 'Ion' and direction LIKE 'est'"}
