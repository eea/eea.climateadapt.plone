var _selectedMapSection = null;
var _mapTooltip = null;

function makeid() {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

  for (var i = 0; i < 5; i++)
    text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
}

function filterCountriesByNames(countries, filterIds) {
  var features = {
    type: 'FeatureCollection',
    features: []
  };
  countries.forEach(function(c) {
    if (filterIds.indexOf(c.properties.SHRT_ENGL) === -1) {
      return;
    }
    features.features.push(c);
  });
  return features;
}

function setCountryFlags(countries, flags) {
  // annotates each country with its own flag property
  // debugger;
  countries.forEach(function(c) {
    var name = c.properties.SHRT_ENGL;
    if (!name) {
      console.log('No flag for', c.properties);
      return;
    }
    var cname = name.replace(' ', '_');
    console.log('cname', cname);
    flags.forEach(function(f) {
      if (f.url.indexOf(cname) > -1) {
        c.url = f.url;
      }
    });
  });
}

// function getCountryMetadata(name, countrySettings) {
//   var countryMetadata = countrySettings[name];
//   return countryMetadata;
// }

function drawCountries(countrySettings, countries) {
  var svg = d3
    .select("body")
    .select("#countries-map svg")
  ;

  svg.selectAll("*").remove();

  var globalMapProjection = d3.geoAzimuthalEqualArea();   // azimuthalEquidistant conicEquidistant()
  // var globalMapProjection = d3.geoConicEquidistant();   // azimuthalEquidistant ()

  globalMapProjection
    .scale(1)
    .translate([0, 0])
  ;

  var path = d3.geoPath().projection(globalMapProjection);   // the path transformer

  var focusCountryNames = Object.keys(countrySettings);

  var focusCountriesFeature = filterCountriesByNames(
    countries, focusCountryNames
  );

  var width = Math.round($(svg.node()).width());
  var height = 500;
  var b = path.bounds(focusCountriesFeature);

  var zoomLevel = 0.9;

  var x = 0;
  var y = 0;

  // var vRatio = window.vRatio;
  var cwRatio = (b[1][0] - b[0][0]) / width;    // bounds to width ratio
  var chRatio = (b[1][1] - b[0][1]) / height;   // bounds to height ratio
  var s = zoomLevel / Math.max(cwRatio, chRatio);
  var t = [
    (width - s * (b[1][0] + b[0][0])) / 2 + x,
    (height - s * (b[0][1] + b[1][1])) / 2 + y
  ];

  globalMapProjection.scale(s).translate(t);

  var g = svg
    .append('g')
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

  g
    .append('g')
    .attr('class', 'graticule')
    .selectAll('path')
    .data(d3.geoGraticule().step([20,10]).lines())
    .enter()
    .append('path')
    .attr('d', path)
  ;
  g
    .append('g')
    .attr('class', 'semi-graticule')
    .selectAll('path')
    .data(d3.geoGraticule().step([5,5]).lines())
    .enter()
    .append('path')
    .attr('d', path)
  ;

  var cprectid = makeid();

  g
    .append('g')
    .selectAll('path')
    .data(countries)
    .enter()
    .append('path')
    .attr('class', function(d) {
      var k = 'country-outline';
      if (focusCountryNames.indexOf(d.properties.SHRT_ENGL) !== -1) {
        k += ' country-selected';
      }

      var meta = countrySettings[d.properties.SHRT_ENGL];
      if (meta && meta[0] && meta[0][_selectedMapSection]) {
        k += ' country-green';
      }
      return k;
    })
    .attr('id', function(d) {
      return 'c-' + cprectid + '-' + d.id;
    })
    .attr('d', path)
    .attr('x', x)
    .attr('y', y)
  ;

  var defs = svg.append('defs');

  // define clipping paths for all focused countries
  defs
    .selectAll('clipPath')
    .data(countries)
    .enter()
    .append('clipPath')
    .attr('id', function(d) {
      return 'cp-' + cprectid + '-' + d.id;
    })
    .append('path')
    .attr('d', path)
    .attr('x', x)
    .attr('y', y)
  ;

  var imgs = svg.append('g');
  imgs
    .attr('class', 'flag-images')
    .selectAll('image')
    .attr('class', 'country-flags')
    .data(focusCountriesFeature.features)
    .enter()
    .append('image')
    .attr('href', function(d) {
      return d.url;
    })
    .attr('class', 'country-flag')
    .attr('clip-path', function(d) {
      return 'url(#cp-' + cprectid + '-' + d.id + ')';
    })
    .attr("x", function (d) {
      var pbox = d3.select('#c-' + cprectid + '-' + d.id).node().getBBox();
      return pbox.x;
    })
    .attr("y", function (d) {
      var pbox = d3.select('#c-' + cprectid + '-' + d.id).node().getBBox();
      return pbox.y;
    })
    .attr("width", function (d) {
      var pbox = d3.select('#c-' + cprectid + '-' + d.id).node().getBBox();
      return pbox.width;
    })
    .attr("height", function (d) {
      var pbox = d3.select('#c-' + cprectid + '-' + d.id).node().getBBox();
      return pbox.height;
    })
    .attr("preserveAspectRatio", "none")

    .attr('opacity', function() {
      return window.isHeaderMap ? '1' : '0';
    })
    .on('mouseover', function(d) {
      if (window.isHeaderMap) {
        $('.country-flag').css('cursor', 'unset');
        return;
      }
      d3.select(this).attr('opacity', 1);
      if (window.isGlobalMap) {
        return tooltip
        .style("visibility", "visible")
        .html(d.SHRT_ENGL);
      }
    })
    .on('mousemove', function(d) {
      if (window.isGlobalMap) {
        return tooltip
        .style("visibility", "visible")
        .style("top", (d3.event.pageY) + "px")
        .style("left", (d3.event.pageX + 10) + "px")
        .html(d.SHRT_ENGL);
      }
    })
    .on('mouseout', function(d) {
      if (window.isHeaderMap) return;
      d3.select(this).attr('opacity', 0);
      if (window.isGlobalMap) {
        return tooltip
        .style("visibility", "hidden");
      }
    })
    .on('click', function(d) {
      var coords = [d3.event.pageY, d3.event.pageX];
      var info = countrySettings[d.properties.SHRT_ENGL];
      var content = info[0];
      var url = info[1];

      console.log(info);
      if (content) toggleTooltip({
        'coords': coords,
        content: content,
        name: d.properties.SHRT_ENGL,
        url: url
      });
    })
  ;
}

function toggleTooltip(opts) {
  console.log('OPts:', opts);
  var x = opts['coords'][0];
  var y = opts['coords'][0];
  var content = opts['content'][_selectedMapSection];
  var name = opts['name'];
  var url = opts['url'];

  $('#map-tooltip').remove();
  var style = 'top:' + x + 'px; left: ' + y + 'px';
  var tooltip = $("<div id='map-tooltip'>")
    .attr('style', style)
    .append(content)
  ;
  $('body').append(tooltip);
}


function createSectionsSelector(sections, countries, callback) {
  var container = $("#countries-map");

  var widget = $("<div class='sections-selector' />");

  sections.forEach(function(key, index) {
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

  $('input', widget).on('change', function() {
    var selectedSection = $(this).attr('value');
    window._selectedMapSection = selectedSection;
    callback();
  });

  var select = $('<select>');
  select.append("<option value=''>Choose a country</option>");

  var countryNames = Object.keys(countries);
  countryNames.sort();
  countryNames.forEach(function(name) {
    select.append($("<option>").append(name));
  });
  widget.prepend(select);

  container.parent().append(widget);
  callback();
}

function initmap(metadata, world, flags) {
  console.log(flags);
  var countrySettings = metadata[0];
  var sections = metadata[1];

  var countries = world.features;
  setCountryFlags(countries, flags);
  console.log('The countries now', countries);

  $(window).resize(function() {
    drawCountries(countrySettings, countries);
  });

  createSectionsSelector(
    sections,
    countrySettings,
    function() {
      drawCountries(countrySettings, countries);
    }
  );

  // drawCountries(countrySettings, countries);
}


jQuery(document).ready(function() {

  // initialize the countries map
  var cpath = '++theme++climateadapt/static/countries/tmp.geojson';
  // var cpath = '++theme++climateadapt/static/countries/countries.geo.json';
  // var cpath = '++theme++climateadapt/static/countries/world-110m.json';
  var fpath = '++theme++climateadapt/static/countries/countries.tsv';

  d3.json(cpath, function(world){
    $.get('@@countries-metadata-extract', function(metadata) {
      d3.tsv(fpath, function(flags) {
        initmap(metadata, world, flags);
      });
    });
  });

});
