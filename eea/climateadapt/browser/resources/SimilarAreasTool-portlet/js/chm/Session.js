CHM.Session = OpenLayers.Class({

	events: null,
	
	location: null, 
	
	risk: null,
	
	sector: null,
	
	similarAreasCasestudiesVector: null,
	
	dissimilarAreasCasestudiesVector: null,
	
	selectFeatureControl: null,
	
	candidatesStore: null,

	tooltip: null,
	
	initialize : function(options) {
		OpenLayers.Util.extend(this, options);
		
		this.similarAreasCasestudiesVector = new CHM.Layer.Vector.CasestudiesVector(
        	'Case studies in similar areas', 
	        {
	    		displayInLayerSwitcher: true,
	        	type: OpenLayers.Filter.Comparison.EQUAL_TO, 
	        	radius: 20,
	        	marker: root + 'js/chm/markers/similar.png',
	        	featuredMarker: root + 'js/chm/markers/similar_featured.png'
	        });
		
		this.dissimilarAreasCasestudiesVector = new CHM.Layer.Vector.CasestudiesVector(
        	'Case studies in other areas', 
	        {
	    		displayInLayerSwitcher: true,
        		type: OpenLayers.Filter.Comparison.NOT_EQUAL_TO, 
        		radius: 16,
        		marker: root + 'js/chm/markers/dissimilar.png',
	        	featuredMarker: root + 'js/chm/markers/dissimilar_featured.png'
	        });
		
		this.selectFeatureControl = new OpenLayers.Control.SelectFeature([this.similarAreasCasestudiesVector, this.dissimilarAreasCasestudiesVector], {multiple: false,	hover: false,});

		this.events = new OpenLayers.Events(this, null,	['locationChanged', 'riskChanged', 'sectorChanged'], false);
		
		this.candidatesStore = new CHM.Control.Locator.Candidate.CandidatesStore();
	},
	
	getLocation: function() {
		return this.location;
	}, 
	
	setLocation: function(aLocation) {
		this.location = aLocation;
		
		this.events.triggerEvent('locationChanged', {location: aLocation});
	},
	
	getRisk: function() {
		return this.risk;
	}, 
	
	setRisk: function(aRisk) {
		this.risk = aRisk;
		
		this.events.triggerEvent('riskChanged', {risk: aRisk});
	},
	
	getSector: function() {
		return this.sector;
	}, 
	
	setSector: function(aSector) {
		this.sector = aSector;
		
		this.events.triggerEvent('sectorChanged', {sector: aSector});
	}
});