CHM.Control.Map.Map = OpenLayers.Class(OpenLayers.Map, {

	location : null,
	
	feature: null,
	
	tooltip: null,
	
	caseStudiesSimilarAreasVectorLayer: null,
	
	caseStudiesDissimilarAreasVectorLayer: null,
	
	similarAreasVectorLayer: null,
	
	offsetX: null,
	
	offsetY: null,
	
    selectionSymbolizer: {
        'Polygon': {fillColor: '#FF0000', stroke: false},
        'Line': {strokeColor: '#FF0000', strokeWidth: 2},
        'Point': {graphicName: 'square', fillColor: '#FF0000', pointRadius: 5}
    },

    initialize: function(options) {
		OpenLayers.Map.prototype.initialize.apply(this, arguments);
		
		this.projection = new OpenLayers.Projection("EPSG:900913");
		
		this.units = "m";
		
		this.maxResolution = 156543.0339;
		
		this.maxExtent = new OpenLayers.Bounds(-2680799.4555375, 3150551.002161, 5244191.63565, 10799431.180210993);
        
		this.restrictedExtent = new OpenLayers.Bounds(-3680799.4555375, 3150551.002161, 5253975.5752687, 10799431.180210993);
        
        this.addControl(new OpenLayers.Control.LayerSwitcher());
        
        session.events.register('locationChanged', this, this.handleLocationChanged);
        
        session.events.register('riskChanged', this, this.handleRiskChanged);
        
        session.events.register('sectorChanged', this, this.handleSectorChanged);
        
        this.events.register('moveend', this, this.handleMoveEnd);
	},
	
	handleMoveEnd: function(event) {
		if (this.caseStudiesDissimilarAreasVectorLayer != null) {
			this.caseStudiesDissimilarAreasVectorLayer.setExtent(this.getExtent());
		}
		
		if (this.caseStudiesSimilarAreasVectorLayer != null) {
			this.caseStudiesSimilarAreasVectorLayer.setExtent(this.getExtent());
		}
	}, 
	
	handleLocationChanged: function(event) {
		this.setLocation(session.location);
	}, 
	
	handleRiskChanged: function(event) {
		this.setRisk(session.risk);
	}, 
	
	handleSectorChanged: function(event) {
		this.setSector(session.sector);
	}, 
	
	addBingLayers : function() {
        var road = new OpenLayers.Layer.VirtualEarth("Road", {
            sphericalMercator: true,
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
            type: VEMapStyle.Road
        });
        
        var shaded = new OpenLayers.Layer.VirtualEarth("Shaded", {
            sphericalMercator: true,
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
            type: VEMapStyle.Shaded
        });
        
        var hybrid = new OpenLayers.Layer.VirtualEarth("Hybrid", {
            sphericalMercator: true,
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
            type: VEMapStyle.Hybrid
        });
        
        var aerial = new OpenLayers.Layer.VirtualEarth("Aerial", {
            sphericalMercator: true,
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
            type: VEMapStyle.Aerial
        });

        this.addLayers([road, shaded, hybrid, aerial]);
        
        this.setCenter(new OpenLayers.LonLat(9.150066, 50.17437).transform(
        	    new OpenLayers.Projection("EPSG:4326"),
        	    this.getProjectionObject()
        	), zoomLevel);
	},
	
	addSATLayers : function() {
		location_vector_layer = new OpenLayers.Layer.Vector('Location',	{
	    	displayInLayerSwitcher: true,
	    	styleMap: new OpenLayers.StyleMap({
	    	    "default": new OpenLayers.Style({
	    	        pointRadius: 24,
	    	        graphicZIndex: 1,
			        externalGraphic: root + 'js/chm/markers/location.png'
	    	    }),
	    	})
	    });
		
		similar_areas_image_layer = new OpenLayers.Layer.WMS('Biogeographical regions', 
			geoserverUrl + wms + '?', 
			{layers: areasLayer, format: 'image/png', transparent: 'true'}, 
			{visibility: true}, 
			{tileOptions: {maxGetUrlLength: 2048}}, 
			{isBaseLayer: false}
		);
		
		this.similarAreasVectorLayer = new OpenLayers.Layer.Vector("Selected area", {
		    // strategies: [new OpenLayers.Strategy.BBOX()],
		    protocol: new OpenLayers.Protocol.WFS({
		      	version: '1.1.0',
		        url: proxyUrl + geoserverUrl + wfs + '?', 
		        featureType: areasFeatureType,
		        featureNS: featureNamespace,
		        geometryName: geometryColumn,
		        maxFeatures: 1,
		        srsName: this.projection,
		        propertyNames: ["biogeo"]
		    })
		});
        
        select = new OpenLayers.Layer.Vector(
        	"Selection", 
        	{
        		styleMap: new OpenLayers.Style(OpenLayers.Feature.Vector.style["select"]),
        		displayInLayerSwitcher: false
        	}
        );

		similar_areas_image_layer.mergeNewParams({'CQL_FILTER': "biogeo = 'JustToMakeSureThatNoAreasAreShownAtStartUp' "});
		
		this.addLayers([similar_areas_image_layer, this.similarAreasVectorLayer, select, location_vector_layer]);
            
		locationcontrol = new CHM.LocationControl({satCHMMap: this});
		
		this.addControl(locationcontrol);
				
		locationcontrol.activate();
	}, 
	
	setArea : function(aArea) {
		similar_areas_image_layer.mergeNewParams({'CQL_FILTER': "biogeo = '" + aArea + "' "});
		
		this.caseStudiesSimilarAreasVectorLayer.setArea(aArea);
			
		this.caseStudiesDissimilarAreasVectorLayer.setArea(aArea);
	},
	
	setRisk : function(aRisk) {
		this.caseStudiesSimilarAreasVectorLayer.setRisk(aRisk);
			
		this.caseStudiesDissimilarAreasVectorLayer.setRisk(aRisk);
	},
	
	setSector : function(aSector) {
		this.caseStudiesSimilarAreasVectorLayer.setSector(aSector);
			
		this.caseStudiesDissimilarAreasVectorLayer.setSector(aSector);
	},
	
	setLocation : function(aLocation) {
		this.location = this.transform(aLocation, this.projection);
		
        if (this.location != null) {
        	this.setFeature(new OpenLayers.Feature.Vector(this.location));
        	
            this.setCenter(new OpenLayers.LonLat(this.location.x, this.location.y));
        } else {
        	this.setFeature(null);
        }
	},
	
	transform : function(aLocation, aProjection) {
		var sourceprojection = aLocation.getProjection();

		var targetprojection = aProjection;

		var result = new CHM.Location(aLocation.x, aLocation.y, targetprojection);

		result.transform(sourceprojection, targetprojection);
		
		return result;
	},
	
	getFeature : function() {
		return this.feature;
	}, 
	
	setFeature : function(aFeature) {
		if (this.feature != null) {
			location_vector_layer.removeFeatures([this.feature]); 
		}
		
		this.feature = aFeature;		
		
		if (this.feature != null) {
			location_vector_layer.addFeatures([this.feature]); 
			
			var filter = new OpenLayers.Filter.Spatial({
		        type: OpenLayers.Filter.Spatial.INTERSECTS,
		        value: this.feature.geometry
		    });
			
			this.similarAreasVectorLayer.protocol.read({
				filter: filter,
				callback: function(result) {
					if (result.success()) {
						if (result.features.length == 1) {
							var feature = result.features[0];
							
							this.setArea(feature.attributes.biogeo);
						} else {
							this.setArea(null);
						}
					}
				},
				scope: this
			});
		}
	},
	
	setSimilarAreasCasestudiesVector: function(aVector) {
		if (this.caseStudiesSimilarAreasVectorLayer != null) {
			this.removeLayer(this.caseStudiesSimilarAreasVectorLayer); 
		}
		
		this.caseStudiesSimilarAreasVectorLayer = aVector;

		if (this.caseStudiesSimilarAreasVectorLayer != null) {
			this.addLayer(this.caseStudiesSimilarAreasVectorLayer); 
			
			this.caseStudiesSimilarAreasVectorLayer.extent = this.getExtent();
		}
	}, 
	
	setDissimilarAreasCasestudiesVector: function(aVector) {
		if (this.caseStudiesDissimilarAreasVectorLayer != null) {
			this.removeLayer(this.caseStudiesDissimilarAreasVectorLayer); 
		}
		
		this.caseStudiesDissimilarAreasVectorLayer = aVector;

		if (this.caseStudiesDissimilarAreasVectorLayer != null) {
			this.addLayer(this.caseStudiesDissimilarAreasVectorLayer); 
			
			this.caseStudiesDissimilarAreasVectorLayer.extent = this.getExtent();
		}
	}, 
	
	setOffsetX: function(aOffsetX) {
		this.offsetX = aOffsetX;
		
		if (this.caseStudiesSimilarAreasVectorLayer != null) {
			this.caseStudiesSimilarAreasVectorLayer.offsetX = aOffsetX;
		}

		if (this.caseStudiesDissimilarAreasVectorLayer != null) {
			this.caseStudiesDissimilarAreasVectorLayer.offsetX = aOffsetX;
		}
	},
	
	setOffsetY: function(aOffsetY) {
		this.offsetY = aOffsetY;
		
		if (this.caseStudiesSimilarAreasVectorLayer != null) {
			this.caseStudiesSimilarAreasVectorLayer.offsetY = aOffsetY;
		}

		if (this.caseStudiesDissimilarAreasVectorLayer != null) {
			this.caseStudiesDissimilarAreasVectorLayer.offsetY = aOffsetY;
		}
	}
});
