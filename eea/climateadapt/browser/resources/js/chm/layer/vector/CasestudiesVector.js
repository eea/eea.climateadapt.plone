CHM.Layer.Vector.CasestudiesVector = OpenLayers.Class(OpenLayers.Layer.Vector, {
	
	protocol: null,
	
	type: null, 
	
	marker: null, 
	
	featuredMarker: null,
	
	radius: null,
	
	extent: null,
	
	area: null,
	
	risk: null,
	
	sector: null,
	
	offsetX: null,
	
	offsetY: null,
	
	initialize: function(options) {
		OpenLayers.Layer.Vector.prototype.initialize.apply(this, arguments);
		
        protocol = new OpenLayers.Protocol.WFS({
	       	version: '1.1.0',
			url:  proxyUrl + geoserverUrl + wfs + '?', 
	        featureType: caseStudiesFeatureType,
	        featureNS: featureNamespace,
	        featurePrefix: "chm",
	        geometryName: geometryColumn,
	        srsName: 'EPSG:900913'
        });
        
        
        var style = new OpenLayers.Style(
                {
                	pointRadius: this.radius, 
    		        graphicZIndex: 1,
                },
                {
                    rules: [
                        new OpenLayers.Rule({
                            filter: new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: "featured", 
                                value: "no"
                            }),
                            symbolizer: {
                                externalGraphic: this.marker
                            }
                        }),
                        new OpenLayers.Rule({
                            filter: new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: "featured",
                                value: "yes"
                            }),
                            symbolizer: {
                                externalGraphic: this.featuredMarker
                            }
                        }),
                        new OpenLayers.Rule({
                            elseFilter: true,
                            symbolizer: {
                                externalGraphic: this.marker
                            }
                        })
                    ]
                }
            );
        
        this.styleMap = new OpenLayers.StyleMap(style);
        
        this.events.register('featureselected', this, this.handleFeatureSelected);
        
        if ((typeof Range !== "undefined") && !Range.prototype.createContextualFragment)
        {
        	Range.prototype.createContextualFragment = function(html)
        	{
        		var frag = document.createDocumentFragment(), 
        		div = document.createElement("div");
        		frag.appendChild(div);
        		div.outerHTML = html;
        		return frag;
        	};
        }        
	},
	
	handleFeatureSelected: function(event) {
	    Ext.QuickTips.init();
	    
		if (session.tooltip != null) {
			session.tooltip.destroy();
		}
		
	    var description = event.feature.attributes.desc;
		if (description == undefined) {
			description = '';
		}
		
		var featured = event.feature.attributes.featured;
		
		var newitem = event.feature.attributes.newitem;
		
		pixel = this.map.getViewPortPxFromLonLat(event.feature.geometry.getBounds().getCenterLonLat());
		
		var html = '<table width="100%" class="csst-tooltip-table">';
		html += '<tr><td class="csst-tooltip-td">' + description + '</td></tr>';
        html += '<tr><td class="csst-tooltip-td"><a href="/viewmeasure?ace_measure_id=' + event.feature.attributes.measureid + '" target="_blank">read more</a></td></tr>'; 
		html += '<tr><td class="csst-tooltip-td">';
		
		if (featured === 'yes') {
			html += '<img src="' + root + 'js/chm/markers/featured-icon.png' + '" alt="Featured case study"/>&nbsp;';
		}
		
		if (newitem === 'yes') {
			html += '<img src="' + root + 'js/chm/markers/new-en.gif' + '" alt="New case study"/>';
		}

		html += '</td></tr>';
		html += '</table>';
        
		session.tooltip = new Ext.ToolTip({        
            title: event.feature.attributes.itemname,
            anchor: 'left',
            cls: 'csst-tooltip', 
            html: html,
            width: 275,
            autoHide: false,
            closable: true,
            listeners: {
                'render': function(){
                    this.header.on('click', function(e){
                        e.stopEvent();
                    }, this, {delegate:'a'});
                }
            }
        });
		
		session.tooltip.showAt([pixel.x + this.offsetX, pixel.y + this.offsetY]);
        
		return true;
	},
	
	setExtent: function(aExtent) {
		if ((this.extent == null && aExtent != null) || (! this.extent.equals(aExtent))) {
			this.extent = aExtent;
			
			this.applyFilters();
		}
	},
	
	setArea : function(aArea) {
		this.area = aArea;
		
		this.applyFilters();
	},
	
	setRisk : function(aRisk) {
		this.risk = aRisk;
		
		this.applyFilters();
	},
	
	setSector : function(aSector) {
		this.sector = aSector;
		
		this.applyFilters();
	},
	
	applyFilters : function() {
        this.removeAllFeatures();
     	
		var filters = new Array();
		
		var extentfilter = null;
		
		if (this.extent != null) {
			extentfilter = this.createSpatialFilter(OpenLayers.Filter.Spatial.BBOX, 'geom', this.extent);
			
			filters.push(extentfilter);
		}
		
		var areafilter = null;
		
		if (this.area != null) {
			areafilter = this.createFilter(this.type, areaColumn, this.area);
			
			filters.push(areafilter);
		}
		
		var riskfilter = null;
			
		if (this.risk != "ALL" && this.risk != null) {
			riskfilter = this.createFilter(OpenLayers.Filter.Comparison.LIKE, 'risks', '*' + this.risk + '*');
				
			filters.push(riskfilter);
		}
		
		var sectorfilter = null;
			
		if (this.sector != "ALL" && this.sector != null) {
			sectorfilter = this.createFilter(OpenLayers.Filter.Comparison.LIKE, 'sectors', '*' + this.sector + '*');
				
			filters.push(sectorfilter);
		}
		
		var filter = new OpenLayers.Filter.Logical({
			type: OpenLayers.Filter.Logical.AND,
			filters: filters
		});
		
		if (areafilter != null) {
			// Read for both similar and dissimilar areas
		    this.read(filter);
		} else {
			// Read for dissimilar areas only
			if (this.type == OpenLayers.Filter.Comparison.NOT_EQUAL_TO) {
				this.read(filter);
			}
		}
	}, 
	
	read: function(aFilter) {
		if (aFilter == null || aFilter.length == 0) {
			protocol.read({
				callback: function(result) {
			        this.removeAllFeatures();
			     	
					if (result.success()) {
						if(result.features.length) {
							this.addFeatures(result.features);
						}
					}
				},
				scope: this
			});
		} else {
	        protocol.read({
	            filter: aFilter,
	            callback: function(result) {
	                this.removeAllFeatures();
	             	
	                if (result.success()) {
	                    if(result.features.length) {
	                    	this.addFeatures(result.features);
	                    }
	                }
	            },
	            scope: this
	        });
		}
	},
		
	createFilter : function(aType, aProperty, aValue) {
		var filter = new OpenLayers.Filter.Comparison({
       		type: aType,
           	property: aProperty,
       		value: aValue
       	});
       	
       	return filter;
	},
	
	createSpatialFilter: function(aType, aProperty, aValue) {
		var filter = new OpenLayers.Filter.Spatial({
			type: aType, 
			property: aProperty, 
			value: aValue
		});
		
		return filter;
	}
});
