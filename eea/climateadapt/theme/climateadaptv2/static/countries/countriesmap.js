/* global d3, $, jQuery */
var _selectedMapSection = null;
// var _mapTooltip = null;
var countrySettings = {};   // country settings extracted from ajax json

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
    $.get('/'+getCurrentLanguage()+'/countries-regions/countries/@@countries-metadata-extract?langflag=1', function (metadata) {
      d3.tsv(fpath, function (flags) {
        window._flags = flags;
//console.log(metadata);
        initmap(metadata, world, flags);
      });
    });
  });

});


function initmap(metadata, world, flags) {
  countrySettings = metadata[0];
  var sections = metadata[1];
  var sections_language = metadata[2];

  world = world.features;
  // setCountryFlags(world, flags);

  createSectionsSelector(
    sections_language,
    countrySettings,
    function () {
      drawCountries(world);
    }
  );

  $('.map-loader').fadeOut(600);
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

  // console.log('countryclass', country, countries)

  // var available = countries.names.indexOf(country.properties.SHRT_ENGL) !== -1;
  // if (available) k += ' country-available';

  var countryName = country.properties.SHRT_ENGL;

  if (countryName == 'Turkey') {
    countryName = 'Turkiye';
  }
  var meta = countrySettings[countryName];
  if (!meta) {
    return k;
  }

  var countryNoData = ["United Kingdom"]
  var discodata = meta[0];
//  console.log("Selected Map section", _selectedMapSection, discodata, countryName);

  if (_selectedMapSection === 'overview') {
//    if (Object.keys(discodata).indexOf(_selectedMapSection) > -1) {
//      k += ' country-available';
//    }

//    if (discodata[_selectedMapSection] === true) {
//      k += ' country-blue';
//    }
let discodataKeys = Object.keys(discodata);
let discodataValues = [];
for (i=0;i<discodataKeys.length;i++) {
  let key = discodataKeys[i];
  if (['nas_info','nap_info','sap_info','nas_mixed','nap_mixed','sap_mixed'].includes(key)) {
    if (discodata[key].length) {
      discodataValues.push(key);
    }
  }
}

    var {nap_info, nas_info, sap_info, notreported} = discodata;

    if (notreported) {
      // k += ' country-notreported';
      k += ' country-nas';
    } else if (discodataValues.length) {
      k += ' country-nasnap';
    } else {
      k += ' country-nodata2';
    }
    if (countryNoData.indexOf(countryName) > -1) {
      k += ' country-nodata';
    }
  }

  if (_selectedMapSection === 'climate') {
    var {cciva_info, notreported} = discodata;

    if (notreported) {
      k += ' country-notreported';
    } else if (cciva_info) {
      k += ' country-nasnap';
    } else if (!cciva_info) {
      k += ' country-none';
    }

    if (countryNoData.indexOf(countryName) > -1) {
      k += ' country-nodata';
    }

  }

  if (_selectedMapSection === 'portals') {
    var {focus_info, notreported} = discodata;

    /*
    if (notreported) {
      k += ' country-notreported';
    } else if (focus_info === 'both') {
      k += ' country-nasnap';
    } else if (focus_info === 'hazard') {
      k += ' country-nas';
    } else if (focus_info === 'adaptation') {
      k += ' country-nap';
    } else if (focus_info === 'not_specified') {
      k += ' country-not-specified';
    } else {
      k += ' country-noportal';
    }
    */
    if (notreported) {
      // k += ' country-notreported';
      k += ' country-nas';
    } else if (["both", "hazard", "adaptation", "not_specified"].includes(focus_info)) {
      k += ' country-nasnap';
    } else {
      k += ' country-noportal';
    }

    if (countryNoData.indexOf(countryName) > -1) {
      k += ' country-nodata';
    }

  }

  return k;
}

function renderCountry(map, country, path, countries, x, y) {
  var cprectid = makeid();    // unique id for this map drawing
  var klass = getCountryClass(country, countries);
  var cId = 'c-' + cprectid + '-' + country.properties.id;
  var cpId = 'cp-' + cprectid + '-' + country.properties.id;

  if (country.properties.SHRT_ENGL=='Türkiye') {
    country.properties.SHRT_ENGL = 'Turkiye';
    // console.log(countries.names);
  }
  if (country.properties.SHRT_ENGL=='Turkey') {
    country.properties.SHRT_ENGL = 'Turkiye';
    // console.log(countries.names);
  }
  var available = countries.names.indexOf(country.properties.SHRT_ENGL) !== -1;
  var parent = map
    .append('g')
    .attr('class', klass)
    ;

  var defs = parent       // define clipping path for this country
    .append('defs')
    ;

  defs.append('clipPath')
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
    .text(country.properties.SHRT_ENGL.toUpperCase())
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
      d3.select(this).attr('opacity', 0); // disable country flag
//      $(this).siblings('path').css({'stroke-width': 2});
      $(this).siblings('path').attr('class', 'selected');
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
//      $(this).siblings('path').css({'stroke-width': 1});
      $(this).siblings('path').attr('class', '');
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

  var defs = svg
    .append('defs')    // rectangular clipping path for the whole drawn map
    ;

  defs.append('clipPath')
    .attr('id', cprectid)
    .append('rect')
    .attr('x', x)
    .attr('y', y)
    .attr('height', height)
    .attr('width', width)
    ;

  // NAS + NAP + SAP
  pattern = defs.append('pattern')
    .attr('id', 'nasnapsap')
    .attr('patternUnits', 'userSpaceOnUse')
    .attr('width', '8')
    .attr('height', '5')
    .attr('patternTransform', 'scale(1) rotate(45)')
    ;
  pattern.append('rect')
    .attr('x', '0')
    .attr('y', '0')
    .attr('width', '100%')
    .attr('height', '100%')
    .attr('fill', '#007db6')
    ;
  pattern.append('line')
    .attr('x1', '0')
    .attr('y', '0')
    .attr('x2', '0')
    .attr('y2', '11')
    .attr('stroke-linecap', 'square')
    .attr('stroke-width', '1')
    .attr('stroke', 'black')
    .attr('fill', '')
    ;

  // NAS + SAP
  pattern = defs.append('pattern')
    .attr('id', 'nassap')
    .attr('patternUnits', 'userSpaceOnUse')
    .attr('width', '8')
    .attr('height', '5')
    .attr('patternTransform', 'scale(1) rotate(45)')
    ;
  pattern.append('rect')
    .attr('x', '0')
    .attr('y', '0')
    .attr('width', '100%')
    .attr('height', '100%')
    .attr('fill', '#78d9fc')
    ;
  pattern.append('line')
    .attr('x1', '0')
    .attr('y', '0')
    .attr('x2', '0')
    .attr('y2', '11')
    .attr('stroke-linecap', 'square')
    .attr('stroke-width', '1')
    .attr('stroke', 'black')
    .attr('fill', '')
    ;

  // NAP + SAP
  pattern = defs.append('pattern')
    .attr('id', 'napsap')
    .attr('patternUnits', 'userSpaceOnUse')
    .attr('width', '8')
    .attr('height', '5')
    .attr('patternTransform', 'scale(1) rotate(45)')
    ;
  pattern.append('rect')
    .attr('x', '0')
    .attr('y', '0')
    .attr('width', '100%')
    .attr('height', '100%')
    .attr('fill', '#11cbff')
    ;
  pattern.append('line')
    .attr('x1', '0')
    .attr('y', '0')
    .attr('x2', '0')
    .attr('y2', '11')
    .attr('stroke-linecap', 'square')
    .attr('stroke-width', '1')
    .attr('stroke', 'black')
    .attr('fill', '')
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
    .select("#countries-map svg")
    ;
  svg.selectAll("*").remove();

  var focusCountryNames = Object.keys(countrySettings);

  var focusCountriesFeature = filterCountriesByNames(
    world, focusCountryNames
  );

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
      'feature': focusCountriesFeature
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
  var noDataReportedMsg = 'No data reported through the reporting mechanism of the Governance Regulation. Last information is available <a href="'+countrySettings[d.properties.SHRT_ENGL][1]+'">here</a>';
  var coords = [d3.event.pageY, d3.event.pageX];
  var info = countrySettings[d.properties.SHRT_ENGL];
  if (d.properties.SHRT_ENGL=='Turkiye') {
    var noDataReportedMsg = 'Data reported in 2021 through the reporting mechanism of the Governance Regulation. Information is available <a href="'+countrySettings[d.properties.SHRT_ENGL][1]+'">here</a>';
  }
  if (!info) return;
  var content = info[0];
  var url = info[1];

  if (_selectedMapSection === 'overview') {
    var napInfo, nasInfo, sapInfo;
    if (content['nap_info']) {
      napInfo = '<span>National Adaptation Plan:</span>' + content['nap_info'];
    } else if (content['nap_mixed']) {
      napInfo = '<span>National Adaptation Plan:</span>' + content['nap_mixed'];
    } else {
      napInfo = '';
    }

    if (content['nas_info']) {
      nasInfo = '<span>National Adaptation Strategy:</span>' + content['nas_info'];
    } else if (content['nas_mixed']) {
      nasInfo = '<span>National Adaptation Strategy:</span>' + content['nas_mixed'];
    } else {
      nasInfo = '';
    }

    if (content['sap_info']) {
      sapInfo = '<span>Sectoral Adaptation Plan:</span>' + content['sap_info'];
    } else if (content['sap_mixed']) {
      sapInfo = '<span>Sectoral Adaptation Plan:</span>' + content['sap_mixed'];
    } else {
      sapInfo = '';
    }

    if (content['notreported']) {
      content = noDataReportedMsg;
    } else {
      content = (nasInfo + napInfo + sapInfo) || "NAS and NAP not reported";
    }
  }

  if (_selectedMapSection === 'climate') {
    var ccivaInfo;

    if (content['cciva_info']) {
      ccivaInfo = content['cciva_info'];
    } else {
      ccivaInfo = "No assessment reported";
    }

    if (content['notreported']) {
      content = noDataReportedMsg;
    } else {
      content = ccivaInfo;
    }
  }

  if (_selectedMapSection === 'portals') {
    var ccivportalInfo;
    if (content['ccivportal_info']) {
      ccivportalInfo = content['ccivportal_info'];
    } else {
      ccivportalInfo = "No portal or platform reported";
    }

    if (content['notreported']) {
      content = noDataReportedMsg;
    } else {
      content = ccivportalInfo;
    }
  }

  if (content) createTooltip({
    coords: coords,
    content: content,
    name: d.properties.SHRT_ENGL,
    flagUrl: d.url,
    url: url
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

function createTooltip(opts) {
  var x = opts['coords'][0];
  var y = opts['coords'][1];
  var content = opts['content'];
  var name = opts['name'];
  var url = opts['url'];
  flagUrl = opts['flagUrl'];

  $('#map-tooltip').remove();
  var style = 'top:' + x + 'px; left: ' + y + 'px';
  var content_div = $('<div>')
    .attr('id', 'tooltip-content')
    .append(content)
    ;
  var h3_name = $('<h3>')
    .append(name)
    ;
  var flag = $('<img>')
    .attr('class', 'tooltip-country-flag')
    .attr('src', function() {
      if (getIEVersion() > 0) {
        return '++theme++climateadaptv2/static/images/fallback.svg';
      } else {
        return flagUrl;
      }
    })
    .attr('height', 33)
    .attr('width', 54)
    ;
  var link_tag = $('<a>')
    .attr('href', url)
    .append(h3_name)
    ;
  var name_div = $('<div>')
    .attr('id', 'country-name')
    .append(link_tag)
    .append(flag)
    ;
  var tooltip = $("<div id='map-tooltip'>")
    .attr('style', style)
    .append(name_div)
    .append(content_div)
    ;
  $('body').append(tooltip);
}

function updateSelectedMapSection(key) {
  if (key.toLowerCase().indexOf('policy') > -1) {
    window._selectedMapSection = 'overview';
  } else if (key.toLowerCase().indexOf('climate') > -1){
    window._selectedMapSection = 'climate';
  } else {
    window._selectedMapSection = 'portals';
  }
}

function createSectionsSelector(sections, countries, callback) {
  // var container = $("#countries-map-selector");
  var widget = $("#sections-selector");
  for (index=0;index<sections.length;index++) {
    key = sections[index][0];
    label_name = sections[index][1];
    var label = $("<label>");
    var span = $("<span class='radiobtn'>");
    var inp = $("<input type='radio'>")
      .attr('style', 'margin-right: 0.3em')
      .attr('name', 'country-map-section')
      .attr('value', key)
      ;
    if (index === 0) {    // set initial value;
      updateSelectedMapSection(key);
      inp.attr('checked', 'checked');
    }

    label
      .append(inp)
      .append(label_name)
      .append(span)
      ;
    widget.append($(label));
  }

  $('input', widget).on('change', function () {
    var selectedSection = $(this).attr('value');
    var $this = $(this);
//    var $mapType = $('.map-type');

//    if ($this.val().indexOf("NAS") != -1) {
//      $mapType.text('NAS');
//    } else if ($this.val().indexOf("NAP") != -1) {
//      $mapType.text('NAP');
//    }

    if ($this.val().toLowerCase().indexOf('policy') > -1) {
      widget.siblings('.nasnap-legend').show();
      widget.siblings('.climate-legend').hide();
      widget.siblings('.portals-legend').hide();
    } else if ($this.val().toLowerCase().indexOf('climate') > -1) {
      widget.siblings('.nasnap-legend').hide();
      widget.siblings('.climate-legend').show();
      widget.siblings('.portals-legend').hide();
    } else { // portals
      widget.siblings('.nasnap-legend').hide();
      widget.siblings('.climate-legend').hide();
      widget.siblings('.portals-legend').show();
    }

    updateSelectedMapSection(selectedSection);
    callback();
  });

  // country selector
  var countryNames = Object.keys(countries);
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
    window.location = countries[name][1];
  })

  // container.append(widget);

  function drawMap(width) {
    callback();
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

  function passThru(d) {
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
