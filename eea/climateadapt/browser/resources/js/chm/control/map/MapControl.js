CHM.Control.Map.MapControl = Ext.extend(GeoExt.MapPanel, {
	
	map: null,
	
    initComponent : function() {
    	this.id = 'csst-map';
    	
    	this.cls = 'csst-panel';
    	
    	this.border = false;
    	
    	this.map = new CHM.Control.Map.Map();
    	
    	CHM.Control.Map.MapControl.superclass.initComponent.call(this);
    },
    
    applicationInitialized: function() {
		this.map.addBingLayers();

		this.map.addSATLayers();
		
		this.map.setSimilarAreasCasestudiesVector(session.similarAreasCasestudiesVector);
		
		this.map.setDissimilarAreasCasestudiesVector(session.dissimilarAreasCasestudiesVector);
		
		this.map.addControl(session.selectFeatureControl);
		
		session.selectFeatureControl.activate();
    },
	
	setOffsetX: function(aOffsetX) {
		this.offsetX = aOffsetX;
		
		if (this.map != null) {
			this.map.setOffsetX(aOffsetX);
		}
	},
	
	setOffsetY: function(aOffsetY) {
		this.offsetY = aOffsetY;
		
		if (this.map != null) {
			this.map.setOffsetY(aOffsetY);
		}
    }
});
