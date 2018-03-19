window._selectedMapSection = null;

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
    if (filterIds.indexOf(c.properties.name) === -1) {
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
    var cname = c.properties.name.replace(' ', '_');
    flags.forEach(function(f) {
      if (f.url.indexOf(cname) > -1) {
        c.url = f.url;
      }
    });
  });
}


function drawCountries(countrySettings, countries) {
  console.log('Drawing countries');
  var svg = d3
    .select("body")
    .select("#countries-map svg")
  ;

  svg.selectAll("*").remove();

  // console.log("Country settings", countrySettings);
  // console.log("World", world);

  var graticule = d3.geoGraticule().step([20,10]);

  var globalMapProjection = d3.geoRobinson();   // azimuthalEquidistant conicEquidistant()
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

  var zoomLevel = 0.8;

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
    .data(graticule.lines())
    .enter()
    .append('path')
    .attr('d', path)
  ;

  var cprectid = makeid();

  function getSectionMetadata(name) {
    if (window._selectedMapSection) {
      var countryMetadata = countrySettings[name];
      if (countryMetadata) {
        return countryMetadata[window._selectedMapSection];
      }
    }
  }

  g
    .append('g')
    .selectAll('path')
    .data(countries)
    .enter()
    .append('path')
    .attr('class', function(d) {
      // console.log('Country', d);
      var k = 'country-outline';
      if (focusCountryNames.indexOf(d.properties.name) !== -1) {
        k += ' country-selected';
      }
      if (getSectionMetadata(d.properties.name)) k += ' country-green';
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
        .html(d.name);
      }
    })
    .on('mousemove', function(d) {
      if (window.isGlobalMap) {
        return tooltip
        .style("visibility", "visible")
        .style("top", (d3.event.pageY) + "px")
        .style("left", (d3.event.pageX + 10) + "px")
        .html(d.name);
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
      console.log(getSectionMetadata(d.properties.name));
    })
  ;
}


function createSectionsSelector(sections, callback) {
  var container = $("#countries-map");

  var widget = $("<div class='sections-selector' />");

  sections.forEach(function(key) {
    var span = $("<div>");
    var label = $("<label>").append(key);
    var inp = $("<input type='radio' style='float: left; margin-right: 0.3em' name='country-map-section' />").attr('value', key);
    label.append(inp);
    span.append(label);
    widget.append(span);
  });

  $('input', widget).on('change', function() {
    var selectedSection = $(this).attr('value');
    window._selectedMapSection = selectedSection;
    console.log("This value:", selectedSection);
    callback();
  });

  container.parent().append(widget);
  return widget;
}

function initmap(metadata, world, flags) {
  var countrySettings = metadata[0];
  var sections = metadata[1];

  var countries = world.features;
  setCountryFlags(countries, flags);

  $(window).resize(function() {
    drawCountries(countrySettings, countries);
  });

  console.log(countrySettings);
  var selectorWidget = createSectionsSelector(sections, function() {
    drawCountries(countrySettings, countries);
  });

  drawCountries(countrySettings, countries);
}


jQuery(document).ready(function() {

  // initialize the countries map
  var cpath = '++theme++climateadapt/static/countries/countries.geo.json';
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
