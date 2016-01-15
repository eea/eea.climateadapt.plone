CHM.Point = OpenLayers.Class(OpenLayers.Geometry.Point, {
	projection : null, 
    
    initialize : function(x, y, aProjection) {
        OpenLayers.Geometry.Point.prototype.initialize.apply(this, arguments);
        
        this.projection = aProjection;
    },
    
    getProjection : function() {
    	return this.projection;
    },  
    
    setProjection : function(aProjection) {
    	this.projection = aProjection;
    } 
});