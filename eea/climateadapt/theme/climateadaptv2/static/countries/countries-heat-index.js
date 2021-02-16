/* eslint-env jquery */
/* global d3 heat_index_info */

var _selectedMapSection = 'hhap';   // which map type is chosen from the radio
var hhap_title = "Heat health action plans (HHAP)";
var hhws_title = "Heat health warning systems (HHWS)";

var correct_country_names = {
  "Former Yugoslav Republic of Macedonia": "North Macedonia",
  "Kosovo": "Kosovo (under UNSCR 1244/99)",
  "Bosnia and Herzegovina": "Bosnia-Herzegovina",
}

// Albania
// Bosnia-Herzegovina
// Kosovo (under UNSCR 1244/99)
// Montenegro
// North Macedonia
// Serbia

// var inverse_correct_country_names = {
//   "North Macedonia": "Former Yugoslav Republic of Macedonia",
//   "Kosovo (under UNSCR 1244/99)": "Kosovo",
// }

jQuery(document).ready(function () {

  // initialize the countries map
  var cpath = '++theme++climateadaptv2/static/countries/euro-countries-simplified.geojson';
  var fpath = '++theme++climateadaptv2/static/countries/countries.tsv';

  var $sw = $('#countries-map');
  var $load = $('<div class="map-loader">' +
    '<div class="loading-spinner"></div>' +
    '<span class="loading-text">Loading map ...</span></div>');
  $sw.append($load);

  d3.json(cpath, function (world) {
    d3.tsv(fpath, function (flags) {
      window._flags = flags;
      createSectionsSelector(function () {
        drawCountries(world.features);
      });
      // console.log(world.features);
      drawCountries(world.features);
      $('.map-loader').fadeOut(600);
    });
  });

});


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

function getCountryClass(country) {   // , countries
  var k = 'country-outline';

  // var available = countries.names.indexOf(country.properties.SHRT_ENGL) !== -1;
  // if (available) k += ' country-available';

  var countryName = correct_country_names[country.properties.SHRT_ENGL] || country.properties.SHRT_ENGL;
  // console.log('country', country.properties.SHRT_ENGL, country.properties);

  var meta = heat_index_info[countryName];
  if (!meta) {
    return k;
  }

  // console.log(countryName, meta);

  if(_selectedMapSection === 'hhap') {
    switch (meta.hhap) {
      case "National HHAP":
        k += ' country-nationalhhap'
        break
      case "Subnational or local HHAP":
        k += ' country-subnationalhhap'
        break
      case "No HHAP":
        k += ' country-no-hhap';
        break
      case "No information":
        k += ' country-none';
        break
      default:
    }
  }

  if(_selectedMapSection === 'hhws') {
    switch (meta.hhws) {
      case "HWWS exists":
        k += ' country-nationalhhap'
        break
      case "No information":
        k += ' country-none';
        break
      default:
    }
  }

  return k;
}

function renderCountry(map, country, path, countries, x, y) {
  // console.log(country.properties.SHRT_ENGL, country);

  var cprectid = makeid();    // unique id for this map drawing
  var klass = getCountryClass(country);   // , countries
  var cId = 'c-' + cprectid + '-' + country.properties.id;
  var cpId = 'cp-' + cprectid + '-' + country.properties.id;


  var countryName = correct_country_names[country.properties.SHRT_ENGL] || country.properties.SHRT_ENGL;
  var available = countries.names.indexOf(countryName) !== -1;

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
  // used to draw label under a maplet
  var parent = d3.select('svg');
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
    .text((correct_country_names[country.properties.SHRT_ENGL] || country.properties.SHRT_ENGL).toUpperCase())
    .on('click', function () {
      showMapTooltip(country);
    })
  ;

  var bbox = label.node().getBBox();

  g
    .append('rect')
  // .attr('class', 'place-label-bg')
    .attr('x', bbox.x - 1)
    .attr('y', bbox.y - 1)
    .attr('width', bbox.width + 2)
    .attr('height', bbox.height + 2)
    .on('click', function () {
      showMapTooltip(country);
    })
  ;

  label.raise();
  passThruEvents(g);
}

function renderCountryFlag(parent, country, bbox, cpId) {
  // console.log(country);
  var countryName = country.properties.SHRT_ENGL.toUpperCase();
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
      showMapTooltip(country);
    })
    .on('mouseover', function() {
      // $('.country-flag').css('cursor', 'unset');
      d3.select(this).attr('opacity', 1);
      return countryNameTooltip
        .style("display", "block")
        .html(countryName);
    })
    .on('mousemove', function() {
      var countryName = (correct_country_names[country.properties.SHRT_ENGL] || country.properties.SHRT_ENGL).toUpperCase();
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

  // renderGraticule(map, 'graticule', [20, 10], path);
  // renderGraticule(map, 'semi-graticule', [5, 5], path);

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
    .select("#countries-map svg")
  ;
  svg.selectAll("*").remove();

  // has: "Kosovo (under UNSCR 1244/99)", "North Macedonia", "Bosnia-Herzegovina"
  var focusCountryNames = Object.keys(heat_index_info);
  // console.log('focus', focusCountryNames);

  var width = Math.round($(svg.node()).width());
  var height = 500;

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
      'feature': filterCountriesByNames(
        world, focusCountryNames
      )
    },
    'zoom': 0.95
  };
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

function showMapTooltip(d) {
  if (_selectedMapSection === 'hhap') return;
  var coords = [d3.event.pageY, d3.event.pageX];

  var info = heat_index_info[d.properties.SHRT_ENGL];
  if (!info) return;

  // console.log('info', info);

  var content = jQuery('.country-tooltip-template').clone().children();

  if (info.heat_index_description) {
    jQuery('.heat_index_value .value', content).html(info.heat_index_description);
  } else {
    jQuery('.heat_index_value', content).remove();
  }

  if (info.website) {
    jQuery('.heat_index_website a', content).attr('href', info.website);
  } else {
    jQuery('.heat_index_website', content).remove();
  }

  createTooltip({
    coords: coords,
    content: content,
    name: d.properties.SHRT_ENGL,
    url: '', // url
    meta: info,
  });

  // TODO: are there multiple onclick handlers here??
  $("body").on('click', function () {
    $('#map-tooltip').remove();
  });

  d3.event.stopPropagation();
}


function filterCountriesByNames(countries, filterIds) {
  var features = {
    type: 'FeatureCollection',
    features: []
  };

  // console.log('filterids', filterIds);
  // filterIds has "Kosovo (under UNSCR 1244/99)" SHRT_ENGL is Kosovo
  // filterIds has "Bosnia-Herzegovina", SHRT_ENGL is "Bosnia and Herzegovina"

  countries.forEach(function (c) {
    var correct_name = correct_country_names[c.properties.SHRT_ENGL] || c.properties.SHRT_ENGL;
    if (filterIds.indexOf(correct_name) === -1) {
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
    // console.log('country name in flags:', name);
    // if (name.indexOf('Kosovo') > -1) debugger;
    if (!name) {
      // console.log('No flag for', c.properties);
      return;
    }
    else if (name === 'Czechia') {
      name = 'Czech Republic';
    } else if (name === 'Former Yugoslav Republic of Macedonia') {
      name = 'Macedonia';
    } if (name.indexOf('Kosovo') > -1) {
      name = 'Kosovo';
    } if (name.indexOf('Bosnia') > -1) {
      name = 'Bosnia';
    }
    var cname = name.replace(' ', '_');
    flags.forEach(function (f) {
      if (f.url.indexOf(cname) > -1) {
        c.url = f.url;
      }
    });
  });

  // console.log('countries', countries);
}

function createTooltip(opts) {
  var x = opts['coords'][0];
  var y = opts['coords'][1];

  var content = opts['content'];
  var name = opts['name'];

  $('#map-tooltip').remove();
  var style = 'top:' + x + 'px; left: ' + y + 'px';
  var content_div = $('<div>')
    .attr('id', 'tooltip-content')
    .append(content)
  ;
  var h3_name = $('<h3>')
    .append(name)
  ;
  var name_div = $('<div>')
    .attr('id', 'country-name')
    .append(h3_name)
  ;
  var tooltip = $("<div id='map-tooltip' style='width:200px !important' >")
    .attr('style', style)
    .append(name_div)
    .append(content_div)
  ;
  $('body').append(tooltip);
}

function createSectionsSelector(callback) {    // sections,
  // var container = $("#countries-map-selector");
  var widget = $("#sections-selector");
  var sections = ['hhap', 'hhws'];
  var titles = {
    hhap: "Heat health action plan (HHAP)",
    hhws: "Heat health warning systems (HHWS)"
  }

  sections.forEach(function (key, index) {
    var label = $("<label>");
    var span = $("<span class='radiobtn'>");
    var inp = $("<input type='radio'>")
      .attr('style', 'margin-right: 0.3em')
      .attr('name', 'country-map-section')
      .attr('value', key)
    ;
    if (index === 0) {    // set initial value;
      // updateSelectedMapSection(key);
      inp.attr('checked', 'checked');
    }

    label
      .append(inp)
      .append(titles[key])
      .append(span)
    ;
    widget.append($(label));
  });

  $('input', widget).on('change', function () {
    _selectedMapSection = $(this).attr('value');
    var $this = $(this);
    var $mapType = $('.map-type');

    if ($this.val().indexOf("hhap") != -1) {
      $mapType.text(hhap_title);
    } else if ($this.val().indexOf("hhws") != -1) {
      $mapType.text(hhws_title);
    }

    if (_selectedMapSection === 'hhap') {
      widget.siblings('.hhws-legend').hide();
      widget.siblings('.hhap-legend').show();
    } else {
      widget.siblings('.hhws-legend').show();
      widget.siblings('.hhap-legend').hide();
    }

    // updateSelectedMapSection(selectedSection);
    callback();
  });

  // country selector
  var countryNames = Object.keys(heat_index_info);
  countryNames.sort();
  var select = $("#country-selector select");

  countryNames.forEach(function (name) {
    select
      .append(
        $("<option>").append(name)
      );
  });

  select.on('change', function () {
    var name = $(this).val();
    if (!name) return;
    window.location = heat_index_info[name][1];
  })

  // container.append(widget);

  function drawMap() {    // width
    callback(width);
  }

  // fire resize event after the browser window resizing it's completed
  var resizeTimer;
  $(window).resize(function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(doneResizing, 500);
  });

  var width = $('#countries-map svg').width();
  function doneResizing() {
    drawMap(width);
  }

  drawMap(width);
}

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

  function passThru() {   // d
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
