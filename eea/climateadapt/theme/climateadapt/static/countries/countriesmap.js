var _selectedMapSection = null;
var _mapTooltip = null;
var countrySettings = {};   // country settings extracted from ajax json


jQuery(document).ready(function () {

  // initialize the countries map
  var cpath = '++theme++climateadapt/static/countries/euro-countries.geojson';
  var fpath = '++theme++climateadapt/static/countries/countries.tsv';

  d3.json(cpath, function (world) {
    $.get('@@countries-metadata-extract', function (metadata) {
      d3.tsv(fpath, function (flags) {
        initmap(metadata, world, flags);
      });
    });
  });

});


function initmap(metadata, world, flags) {
  countrySettings = metadata[0];
  var sections = metadata[1];

  var world = world.features;

  setCountryFlags(world, flags);

  createSectionsSelector(
    sections,
    countrySettings,
    function () {
      drawCountries(world);
    }
  );
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

  var defs = svg.append('defs');

  defs    // rectangular clipping path for the whole drawn map
    .append('clipPath')
    .attr('id', cprectid)
    .append('rect')
    .attr('x', x)
    .attr('y', y)
    .attr('height', height)
    .attr('width', width)
  ;

  var g = svg   // the map will be drawn in this group
    .append('g')
    .attr('clip-path', 'url(#' + cprectid + ')')
    ;

  g     // the world sphere, acts as ocean
    .append("path")
    .datum(
    {
      type: "Sphere"
    }
    )
    .attr("class", "sphere")
    .attr("d", path)
    ;

  g     // draw primary graticule lines
    .append('g')
    .attr('class', 'graticule')
    .selectAll('path')
    .data(d3.geoGraticule().step([20, 10]).lines())
    .enter()
    .append('path')
    .attr('d', path)
    ;
  g   // draw secondary graticule lines
    .append('g')
    .attr('class', 'semi-graticule')
    .selectAll('path')
    .data(d3.geoGraticule().step([5, 5]).lines())
    .enter()
    .append('path')
    .attr('d', path)
    ;

  g     // draw a path for each country
    .append('g')
    .selectAll('path')
    .data(world)
    .enter()
    .append('path')
    .attr('class', function (d) {
      var k = 'country-outline';
      var available = countries.names.indexOf(d.properties.SHRT_ENGL) !== -1;
      if (available) k += ' country-selected';

      var meta = countrySettings[d.properties.SHRT_ENGL];
      if (available && meta && meta[0] && meta[0][_selectedMapSection]) {
        k += ' country-green';
      }
      return k;
    })
    .attr('id', function (d) {
      return 'c-' + cprectid + '-' + d.properties.id;
    })
    .attr('d', path)
    .attr('x', x)
    .attr('y', y)
    ;

  // define clipping paths for all focused countries
  var defs = svg.append('defs');
  defs
    .selectAll('clipPath')
    .data(countries.feature.features)
    .enter()
    .append('clipPath')
    .attr('id', function (d) {
      return 'cp-' + cprectid + '-' + d.properties.id;
    })
    .append('path')
    .attr('d', path)
    .attr('x', x)
    .attr('y', y)
    ;

  function id(d) {
    return '#c-' + cprectid + '-' + d.properties.id;
  }

  function countryBBox(d) {
    // console.log('ID', d.properties.id);
    // console.log(globalMapProjection, path);
    return d3.select(id(d)).node().getBBox();

    // if (d.properties.id == 'PT') debugger;
    // var b = path.bounds(d);
    // console.log('Bounds', b);
    // return {
    //   x: b[0][0],
    //   y: b[1][0],
    //   width: b[1][0] - b[0][0],
    //   height: b[1][1] - b[0][1],
    // }
  }

  var imgs = svg.append('g');
  imgs
    .selectAll('image')
    .data(countries.feature.features)
    .enter()
    .append('image')
    .attr('href', function (d) {
      return d.url;
    })
    .attr('class', 'country-flag')
    .attr('clip-path', function (d) {
      return 'url(#cp-' + cprectid + '-' + d.properties.id + ')';
    })
    .attr("x", function (d) {
      return countryBBox(d).x;
    })
    .attr("y", function (d) {
      return countryBBox(d).y;
    })
    .attr("width", function (d) {
      return countryBBox(d).width;
    })
    .attr("height", function (d) {
      return countryBBox(d).height;
    })
    .attr("preserveAspectRatio", "none")
    .attr('opacity', '0')
    .on('mouseover', function (d) {
      $('.country-flag').css('cursor', 'unset');
      d3.select(this).attr('opacity', 1);
    })
    .on('mousemove', function (d) {})
    .on('mouseout', function (d) {
      d3.select(this).attr('opacity', 0);
    })
    .on('click', showMapTooltip)
  ;

  var foci = [],
    labels = [];

  // Store the projected coordinates of the places for the foci and the labels
  countries.feature.features.forEach(function(d, i) {
    if (
      // these are very small countries that we will create a maplet for;
      d.properties.SHRT_ENGL === 'Liechtenstein' ||
      d.properties.SHRT_ENGL === 'Luxembourg' ||
      d.properties.SHRT_ENGL === 'Malta'
    ) return;
    var c = path.centroid(d);
    foci.push({x: c[0], y: c[1]});
    labels.push({
      x: c[0],
      y: c[1],
      label: d.properties.SHRT_ENGL,
      properties: d.properties
    })
  });

  var simulation = d3
    .forceSimulation()
    .force("charge", d3.forceManyBody().strength(-1))
    .force("collide", d3.forceCollide().strength(2).radius(8).iterations(1))
    .nodes(labels)
  ;

  setTimeout(function() {

    // var node = svg.append("g")
    //   .attr("class", "node")
    //   .selectAll("circle")
    //   .data(labels)
    //   .enter().append("circle")
    //   .attr("r", function(d) { return 10; })
    //   .attr("fill", 'red')
    //   .attr("cx", function(d){ return d.x; })
    //   .attr("cy", function(d){ return d.y; })
    // ;
    //
    // var node = svg.append("g")
    //   .attr("class", "node")
    //   .selectAll("circle")
    //   .data(foci)
    //   .enter().append("circle")
    //   .attr("r", function(d) { return 3; })
    //   .attr("fill", 'black')
    //   .attr("cx", function(d){ return d.x; })
    //   .attr("cy", function(d){ return d.y; })
    // ;

    var placeLabels = svg.selectAll('.place-label-overlay')
      .data(labels)
      .enter()
      .append('text')
      .attr('class', 'place-label')
      .attr('id', function(d) {
        return 'pl-' + d.index;
      })
      .attr('x', function(d) { return d.x; })
      .attr('y', function(d) { return d.y; })
      .attr('text-anchor', 'middle')
      .text(function(d) { return d.label.toUpperCase(); })
      .on('click', showMapTooltip)
    ;

    function getPLBbox(d) {
      var b = $('#pl-' + d.index).get(0).getBBox();
      b.x -= 1;
      b.y -= 1;
      b.width += 2;
      b.height += 2;
      return b;
    }

    var placeBgs = svg.selectAll('.place-label-bg')
      .data(labels)
      .enter()
      .append('rect')
      .attr('class', 'place-label-bg')
      .attr('x', function(d) { return getPLBbox(d).x; })
      .attr('y', function(d) { return getPLBbox(d).y; })
      .attr('width', function(d) { return getPLBbox(d).width; })
      .attr('height', function(d) { return getPLBbox(d).height; })
      .on('click', showMapTooltip)
    ;

    d3.selectAll('.place-label').raise();

  }, 100);



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

  countries.forEach(function(name, index) {
    var feature = filterCountriesByNames(world, [name]);
    var boxw = 50;
    var boxh = 50;
    var space = 10;

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
      'world': world,
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
      'zoom': 0.5
    };
    drawMaplet(zo);
  });
}

function drawMaplet(opts) {
  var svg = opts.svg;

  var msp = opts.coordinates;
  svg
    .append('rect')
    .attr('class', 'maplet-outline')
    .attr('x', msp.x)
    .attr('y', msp.y)
    .attr('width', msp.width)
    .attr('height', msp.height)
  ;

  var countryName = opts.focusCountries.names[0];
  var label = svg.append('text')
    .attr('x', 0)
    .attr('y', 0)
    .attr('class', 'country-focus-label')
    .attr('text-anchor', 'middle')
    .text(countryName)
  ;

  var lbbox = label.node().getBBox();
  var textboxh = lbbox.height + lbbox.height / 4;

  label
    .attr('x', msp.x + msp.width/2)
    .attr('y', msp.y + msp.height - textboxh / 3)   //  - textboxh / 3
  ;

  renderCountriesBox(opts);
  label.raise();
}

function drawCountries(world) {
  var svg = d3
    .select("body")
    .select("#countries-map svg")
    ;
  svg.selectAll("*").remove();
  var filter = '<filter id="dropshadow" height="130%">'
    + '<feGaussianBlur in="SourceAlpha" stdDeviation="3"/>'
    + '<feOffset dx="2" dy="2" result="offsetblur"/>'
    + '<feComponentTransfer>'
    + '<feFuncA type="linear" slope="0.5"/>'
    + '</feComponentTransfer>'
    + '<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>'
    + '</filter>'
  ;
  $(svg.node()).append($('<defs>' + filter + '</defs>'));

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
  }
  drawMaplets(mo);
}

function showMapTooltip(d) {
  var coords = [d3.event.pageY, d3.event.pageX];
  var info = countrySettings[d.properties.SHRT_ENGL];
  var content = info[0];
  var url = info[1];

  if (content) createTooltip({
    coords: coords,
    content: content,
    name: d.properties.SHRT_ENGL,
    url: url
  });

  // TODO: are there multiple onclick handlers here??
  $("body").on('click', function() {
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
  var content = opts['content'][_selectedMapSection];
  var name = opts['name'];
  var url = opts['url'];

  $('#map-tooltip').remove();
  var style = 'top:' + x + 'px; left: ' + y + 'px';
  var content_div = $('<div>')
    .attr('id', 'tooltip-content')
    .append(content)
  ;
  var h3_name = $('<h3>')
    .append(name)
  ;
  var link_tag = $('<a>')
    .attr('href', url)
    .append(h3_name)
  ;
  var name_div = $('<div>')
    .attr('id', 'country-name')
    .append(link_tag)
  ;
  var tooltip = $("<div id='map-tooltip'>")
    .attr('style', style)
    .append(name_div)
    .append(content_div)
    ;
  $('body').append(tooltip);
}


function createSectionsSelector(sections, countries, callback) {
  var container = $("#countries-map-selector");

  var widget = $("<div class='sections-selector' />");

  sections.forEach(function (key, index) {
    var label = $("<label>");
    var inp = $("<input type='radio'>")
      .attr('style', 'float: left; margin-right: 0.3em')
      .attr('name', 'country-map-section')
      .attr('value', key)
      ;
    if (index === 0) {
      window._selectedMapSection = key;
      inp.attr('checked', 'checked');
    }

    label
      .append(inp)
      .append(key)
      ;
    widget.append($("<div>").append(label));
  });

  $('input', widget).on('change', function () {
    var selectedSection = $(this).attr('value');
    window._selectedMapSection = selectedSection;
    callback();
  });

  var select = $('<select>');
  select.append("<option value=''>Choose a country</option>");

  var countryNames = Object.keys(countries);
  countryNames.sort();
  countryNames.forEach(function (name) {
    select.append($("<option>").append(name));
  });
  widget.prepend(select);

  container.append(widget);
  callback();

  $(window).resize(function () {
    drawCountries(world);
  });

}


function makeid() {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

  for (var i = 0; i < 5; i++)
    text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
}


function travelToOppositeMutator(start, viewport, delta) {
  // point: the point we want to mutate
  // start: starting point (the initial anchor point)
  // viewport: array of width, height
  // delta: array of dimensions to travel

  var center = [viewport[0] / 2, viewport[1] / 2];

  var dirx = start[0] > center[0] ? -1 : 1;
  var diry = start[1] > center[1] ? -1 : 1;

  return function(point) {
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
