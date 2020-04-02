/* eslint-env jquery */
/* global d3 */

var _selectedMapSection = null;
var countrySettings = [];   // country list extracted from ajax json

window._world = {};

// $(document).ready(function() {});

function initCountriesMapTile() {
  // initialize the countries map
  var cpath = '++theme++climateadaptv2/static/countries/euro-countries-simplified.geojson';
  var fpath = '++theme++climateadaptv2/static/countries/countries.tsv';

  var $sw = $('.svg-fp-container');
  var $load = $('<div class="map-loader">' +
    '<div class="loading-spinner"></div>' +
    '<span class="loading-text">Loading map ...</span></div>');
  $sw.append($load);

  d3.json(cpath, function (world) {
    $.get(window.portal_url + '/@@countries-tile-metadata', function (metadata) {
      d3.tsv(fpath, function (flags) {
        window._world = world;
        window.countrySettings = metadata;
        window._flags = flags;

        // monthly change the active tab;
        var d = new Date();
        var month = d.getMonth();

        var monthR = month % 5;
        var $list = $('ul.main-nav-tabs');
        var item = $list.children('li')[monthR];
        if (item) {
          var $hrefs = $('a', item);
          $hrefs.length && $hrefs.tab('show');
        }

      });
    });
  });

  $('.main-tab-item > a').on('shown.bs.tab', function (e) {
    var tab = e.target; // newly activated tab
    console.log('shown', tab);
    // var extab = e.relatedTarget; // previous active tab

    function drawMap() {    // width
      drawCountries(world);
    }

    function doneResizing() {
      drawMap(width);
    }

    if ($(tab).data('tab') == 'countries') {
      var world = window._world.features;
      if (world) {
        $('.map-loader').fadeOut(600);

        // fire resize event after the browser window resizing it's completed
        var resizeTimer;
        $(window).resize(function() {
          clearTimeout(resizeTimer);
          resizeTimer = setTimeout(doneResizing, 500);
        });

        var width = $('.svg-fp-container svg').width();
        drawMap(width);
      }
    }
  })

}


function renderGraticule(container, klass, steps, pathTransformer) {
  container     // draw primary graticule lines
    .append('g')
    .attr('class', klass)
    .selectAll('path')
    .data(d3.geoGraticule().step(steps).lines())
    .enter()
    .append('path')
    .attr('d', pathTransformer)
    ;
}

function getCountryClass(country, countries) {
  var k = 'country-outline';
  var available = countries.names.indexOf(country.properties.SHRT_ENGL) !== -1;
  if (available) k += ' country-available';

  var meta = countrySettings[country.properties.SHRT_ENGL];
  if (available && meta && meta[0] && meta[0][_selectedMapSection]) {
    k += ' country-green';
  }
  return k;
}

function renderCountry(map, country, path, countries, x, y) {

  var cprectid = makeid();    // unique id for this map drawing
  var klass = getCountryClass(country, countries);
  var cId = 'c-' + cprectid + '-' + country.properties.id;
  var cpId = 'cp-' + cprectid + '-' + country.properties.id;

  var available = countries.names.indexOf(country.properties.SHRT_ENGL) !== -1;

  var parent = map
    .append('g')
    .attr('class', klass)
    ;

  parent       // define clipping path for this country
    .append('defs')
    .append('clipPath')
    .attr('id', cpId)
    .append('path')
    .attr('d', path(country))
    .attr('x', x)
    .attr('y', y)
    ;

  var outline = parent       // this is the country fill and outline
    .append('path')
    .attr('id', cId)
    .attr('x', x)
    .attr('y', y)
    .attr('d', path(country))
    ;

  if (available) {
    var bbox = outline.node().getBBox();
    renderCountryFlag(parent, country, bbox, cpId);
    // renderCountryLabel(country, path);
  }
}

function renderCountryLabel(country, path, force) {
  var parent = d3.select('.svg-map-container svg');
  var klass = force ? 'country-label maplet-label' : 'country-label'
  var g = parent
    .append('g')
    .attr('class', klass)
    ;
  if (
    // these are very small countries that we will create a maplet for;
    (
      country.properties.SHRT_ENGL === 'Liechtenstein' ||
      country.properties.SHRT_ENGL === 'Luxembourg' ||
      country.properties.SHRT_ENGL === 'Malta'
    ) && !force
  ) return;

  var delta = force ? 20 : 0;

  var pId = 'pl-' + country.id;
  var center = path.centroid(country);

  var label = g
    .append('text')
    // .attr('class', 'place-label')
    .attr('id', pId)
    .attr('x', center[0])
    .attr('y', center[1] + delta)
    .attr('text-anchor', 'middle')
    .text(country.properties.SHRT_ENGL.toUpperCase())
    ;

  var bbox = label.node().getBBox();

  g
    .append('rect')
    // .attr('class', 'place-label-bg')
    .attr('x', bbox.x - 1)
    .attr('y', bbox.y - 1)
    .attr('width', bbox.width + 2)
    .attr('height', bbox.height + 2)
    ;

  label.raise();
  passThruEvents(g);
}

function renderCountryFlag(parent, country, bbox, cpId) {
  var flag = parent
    .append('image')
    .attr('class', 'country-flag')
    .attr('href', function() {
      if (getIEVersion() > 0) {
        return '++theme++climateadaptv2/static/images/fallback.svg';
      } else {
        return country.url;
      }
    })
    .attr("preserveAspectRatio", "none")
    .attr('opacity', '0')
    .attr('clip-path', 'url(#' + cpId + ')')
    .attr('x', bbox.x)
    .attr('y', bbox.y)
    .attr('height', bbox.height)
    .attr('width', bbox.width)
    .on('click', function () {
      var link = country.properties.SHRT_ENGL.toLowerCase().replace(" ", "-");
      location.href = '/countries-regions/countries/' + link;
    })
    .on('mouseover', function() {
      var countryName = country.properties.SHRT_ENGL.toUpperCase();
      d3.select(this).attr('opacity', 1);
      return countryNameTooltip
      .style("display", "block")
      .html(countryName);
    })
    .on('mousemove', function() {
      var countryName = country.properties.SHRT_ENGL.toUpperCase();
      return countryNameTooltip
      .style("display", "block")
      .style("top", (d3.event.pageY) + "px")
      .style("left", (d3.event.pageX + 10) + "px")
      .html(countryName);
    })
    .on('mouseout', function() {
      d3.select(this).attr('opacity', 0);
      return countryNameTooltip
      .style("display", "none");
    })
    ;
  return flag;
}

function renderCountriesBox(opts) {

  var coords = opts.coordinates;
  var countries = opts.focusCountries;

  var svg = opts.svg;
  var world = opts.world;
  var zoom = opts.zoom;
  var cprectid = makeid();    // unique id for this map drawing

  var globalMapProjection = d3.geoAzimuthalEqualArea();

  globalMapProjection
    .scale(1)
    .translate([0, 0])
    ;

    // var windowWidth = $(window).width();
    //
    // if (windowWidth <= 991) {
    //     globalMapProjection
    //     .scale(1)
    //     .translate([0, 0])
    //     ;
    // } else {
    //   globalMapProjection
    //   .scale(1)
    //   .translate([-0.25, 0])
    //   ;
    // }

  // the path transformer
  var path = d3.geoPath().projection(globalMapProjection);

  var x = coords.x;
  var y = coords.y;
  var width = coords.width;
  var height = coords.height;
  // var extent = [[x + 20, y + 20], [x + coords.width - 20 , y + coords.height - 20]];
  // console.log('fitting extent', extent);
  // globalMapProjection.fitExtent(extent, countries.feature);

  var b = path.bounds(countries.feature);
  var cwRatio = (b[1][0] - b[0][0]) / width;    // bounds to width ratio
  var chRatio = (b[1][1] - b[0][1]) / height;   // bounds to height ratio
  var s = zoom / Math.max(cwRatio, chRatio);
  var t = [
    (width - s * (b[1][0] + b[0][0])) / 2 + x,
    (height - s * (b[0][1] + b[1][1])) / 2 + y
  ];

  globalMapProjection.scale(s).translate(t);

  svg
    .append('defs')    // rectangular clipping path for the whole drawn map
    .append('clipPath')
    .attr('id', cprectid)
    .append('rect')
    .attr('x', x)
    .attr('y', y)
    .attr('height', height)
    .attr('width', width)
    ;

  var map = svg   // the map will be drawn in this group
    .append('g')
    // .attr('clip-path', 'url(#' + cprectid + ')')
    .attr('clip-path', opts.isMaplet ? 'url(#' + cprectid + ')': null)
    ;

  map     // the world sphere, acts as ocean
    .append("path")
    .datum(
    {
      type: "Sphere"
    }
    )
    .attr("class", "sphere")
    .attr("d", path)
    ;

  renderGraticule(map, 'graticule', [20, 10], path);
  renderGraticule(map, 'semi-graticule', [5, 5], path);

  setCountryFlags(countries.feature.features, window._flags);

  world.forEach(function (country) {
    renderCountry(map, country, path, countries, x, y);
  });

  return path;
}


function drawMaplets(opts) {
  var svg = opts.svg;
  var world = opts.world;
  var viewport = opts.viewport;
  var start = opts.start;
  var side = opts.side;

  var g = svg   // the map will be drawn in this group
    .append('g')
    .attr('class', 'maplet-container')
    ;

  var countries = opts.countries;

  countries.forEach(function (name, index) {
    var feature = filterCountriesByNames(world, [name]);
    var boxw = 50;
    var boxh = 50;
    var space = 10;

    var mapletWorld = world.filter(function(country) {
      return country.properties.SHRT_ENGL === name;
    });

    var msp = getMapletStartingPoint(
      viewport,
      start,
      index,
      side,
      space,
      [boxw, boxh],
      0
    );

    var zo = {
      'world': mapletWorld,
      'svg': g,
      'coordinates': {
        'x': msp.x,
        'y': msp.y,
        'width': boxw,
        'height': boxh
      },
      'focusCountries': {
        'names': [name],
        'feature': feature
      },
      'zoom': 0.5,
      isMaplet: true
    };
    drawMaplet(zo);
  });
}

function drawMaplet(opts) {
  var msp = opts.coordinates;
  var svg = opts.svg;
  svg
    .append('rect')
    .attr('class', 'maplet-outline')
    .attr('x', msp.x)
    .attr('y', msp.y)
    .attr('width', msp.width)
    .attr('height', msp.height)
    ;

  var path = renderCountriesBox(opts);
  renderCountryLabel(opts.focusCountries.feature.features[0], path, true);
}

function drawCountries(world) {
  var svg = d3
    .select("body")
    .select(".svg-map-container svg")
    ;
  svg.selectAll("*").remove();

  var focusCountryNames = countrySettings; // Object.keys(countrySettings);

  var focusCountriesFeature = filterCountriesByNames(
    world, focusCountryNames
  );

  var width = Math.round($(svg.node()).width());
  var height = Math.round($(svg.node()).height());

  var opts = {
    'world': world,
    'svg': svg,
    'coordinates': {
      'x': 0,
      'y': 0,
      'width': width,
      'height': height
    },
    'focusCountries': {
      'names': focusCountryNames,
      'feature': focusCountriesFeature
    },
    'zoom': 0.95
  }
  renderCountriesBox(opts);

  var mo = {
    'svg': svg,
    'world': world,
    'viewport': [width, height],
    'countries': ['Malta', 'Liechtenstein', 'Luxembourg'],
    'start': [width - 60, 10],
    'side': 'left'
    // 'size': 80,
    // 'space': 6,
  };
  drawMaplets(mo);
}

// tooltip with country names on hover
var countryNameTooltip = d3.select("body")
    .append("div")
    .attr('class', 'tooltip')
    ;


function filterCountriesByNames(countries, filterIds) {
  var features = {
    type: 'FeatureCollection',
    features: []
  };
  countries.forEach(function (c) {
    if (filterIds.indexOf(c.properties.SHRT_ENGL) === -1) {
      return;
    }
    features.features.push(c);
  });
  return features;
}


function setCountryFlags(countries, flags) {
  // annotates each country with its own flag property
  countries.forEach(function (c) {
    var name = c.properties.SHRT_ENGL;
    if (!name) {
      // console.log('No flag for', c.properties);
      return;
    }
    else if (name === 'Czechia') {
      name = 'Czech Republic';
    }
    var cname = name.replace(' ', '_');
    flags.forEach(function (f) {
      if (f.url.indexOf(cname) > -1) {
        c.url = f.url;
      }
    });
  });
}


// function createTooltip(opts) {
//   var x = opts['coords'][0];
//   var y = opts['coords'][1];
//   var content = opts['content'][_selectedMapSection];
//   var name = opts['name'];
//   var url = opts['url'];
//
//   $('#map-tooltip').remove();
//   var style = 'top:' + x + 'px; left: ' + y + 'px';
//   var content_div = $('<div>')
//     .attr('id', 'tooltip-content')
//     .append(content)
//     ;
//   var h3_name = $('<h3>')
//     .append(name)
//     ;
//   var link_tag = $('<a>')
//     .attr('href', url)
//     .append(h3_name)
//     ;
//   var name_div = $('<div>')
//     .attr('id', 'country-name')
//     .append(link_tag)
//     ;
//   var tooltip = $("<div id='map-tooltip'>")
//     .attr('style', style)
//     .append(name_div)
//     .append(content_div)
//     ;
//   $('body').append(tooltip);
// }

// function createSectionsSelector(sections, countries, callback) {
//   // var container = $("#countries-map-selector");
//   var widget = $("#sections-selector");
//
//   sections.forEach(function (key, index) {
//     var label = $("<label>");
//     var span = $("<span class='radiobtn'>");
//     var inp = $("<input type='radio'>")
//       .attr('style', 'margin-right: 0.3em')
//       .attr('name', 'country-map-section')
//       .attr('value', key)
//       ;
//     if (index === 0) {
//       window._selectedMapSection = key;
//       inp.attr('checked', 'checked');
//     }
//
//     label
//       .append(inp)
//       .append(key)
//       .append(span)
//       ;
//     widget.append($(label));
//   });
//
//   $('input', widget).on('change', function () {
//     var selectedSection = $(this).attr('value');
//     var $this = $(this);
//     var $mapType = $('.map-type');
//     if ($this.val().indexOf("NAS") != -1) {
//       $mapType.text('NAS');
//     } else if ($this.val().indexOf("NAP") != -1) {
//       $mapType.text('NAP');
//     }
//     window._selectedMapSection = selectedSection;
//     callback();
//   });
//
//   // country selector
//   var countryNames = Object.keys(countries);
//   countryNames.sort();
//   var select = $("#country-selector select");
//
//   countryNames.forEach(function (name) {
//     select
//       .append(
//       $("<option>").append(name)
//       );
//   });
//
//   select.on('change', function () {
//     var name = $(this).val();
//     if (!name) return;
//     window.location = countries[name][1];
//   })
//
//   // container.append(widget);
//
//   function drawMap(width) {
//     callback();
//   }
//
//   // fire resize event after the browser window resizing it's completed
//   var resizeTimer;
//   $(window).resize(function() {
//     clearTimeout(resizeTimer);
//     resizeTimer = setTimeout(doneResizing, 500);
//   });
//
//   var width = $('#countries-map svg').width();
//   function doneResizing() {
//     drawMap(width);
//   }
//
//   drawMap(width);
// }

function makeid() {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

  for (var i = 0; i < 5; i++)
    text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
}

function getIEVersion() {
  var sAgent = window.navigator.userAgent;
  var Idx = sAgent.indexOf("MSIE");

  // If IE, return version number.
  if (Idx > 0)
    return parseInt(sAgent.substring(Idx+ 5, sAgent.indexOf(".", Idx)));

  // If IE 11 then look for Updated user agent string.
  else if (navigator.userAgent.match(/Trident\/7\./))
    return 11;

  else
    return 0; //It is not IE
}


function travelToOppositeMutator(start, viewport, delta) {
  // point: the point we want to mutate
  // start: starting point (the initial anchor point)
  // viewport: array of width, height
  // delta: array of dimensions to travel

  var center = [viewport[0] / 2, viewport[1] / 2];

  var dirx = start[0] > center[0] ? -1 : 1;
  var diry = start[1] > center[1] ? -1 : 1;

  return function (point) {
    var res = [
      point[0] + delta[0] * dirx,
      point[1] + delta[1] * diry
    ];
    return res;
  };
}


function getMapletStartingPoint(
  viewport,   // an array of two integers, width and height
  startPoint, // an array of two numbers, x, y for position in viewport
  index,      // integer, position in layout
  side,       // one of ['top', 'bottom', 'left', right']
  spacer,     // integer with amount of space to leave between Maplets
  boxDim,      // array of two numbers, box width and box height
  titleHeight // height of title box
) {

  // return value is array of x,y
  // x: horizontal coordinate
  // y: vertical coordinate

  var bws = boxDim[0] + spacer;   // box width including space to the right
  var bhs = boxDim[1] + spacer + titleHeight;

  var mutator = travelToOppositeMutator(startPoint, viewport, [bws, bhs]);

  var mutPoint = [startPoint[0], startPoint[1]];

  for (var i = 0; i < index; i++) {
    mutPoint = mutator(mutPoint, index);
  }

  // TODO: this could be improved, there are many edge cases
  switch (side) {
    case 'top':
      mutPoint[1] = startPoint[1];
      break;
    case 'bottom':
      mutPoint[1] = startPoint[1] - bhs;
      break;
    case 'left':
      mutPoint[0] = startPoint[0];
      break;
    case 'right':
      mutPoint[0] = startPoint[0] - bws;
      break;
  }

  return {
    x: mutPoint[0],
    y: mutPoint[1]
  };
}

function passThruEvents(g) {
  g
    // .on('mousemove.passThru', passThru)
    .on('mouseover', passThru)
  // .on('mousedown.passThru', passThru)
  ;

  function passThru() {
    // console.log('passing through');
    var e = d3.event;

    var prev = this.style.pointerEvents;
    this.style.pointerEvents = 'none';

    var el = document.elementFromPoint(d3.event.x, d3.event.y);

    var e2 = document.createEvent('MouseEvent');
    e2.initMouseEvent(
      e.type,
      e.bubbles,
      e.cancelable,
      e.view,
      e.detail,
      e.screenX,
      e.screenY,
      e.clientX,
      e.clientY,
      e.ctrlKey,
      e.altKey,
      e.shiftKey,
      e.metaKey,
      e.button,
      e.relatedTarget
    );

    el.dispatchEvent(e2);

    this.style.pointerEvents = prev;
  }
}
