CHM.LocationControl = OpenLayers.Class(OpenLayers.Control, {
	defaultHandlerOptions : {
		'single' : true,
		'double' : false,
		'pixelTolerance' : 0,
		'stopSingle' : true,
		'stopDouble' : false
	},
	
	initialize : function(options) {
		OpenLayers.Control.prototype.initialize.apply(this, arguments);

		this.handlerOptions = OpenLayers.Util.extend({}, this.defaultHandlerOptions);
		
		this.handler = new OpenLayers.Handler.Click(this, {'click' : this.trigger}, this.handlerOptions);
	},
	
	trigger : function(e) {
		var lonlat = this.map.getLonLatFromViewPortPx(e.xy);
		
		session.setLocation(new CHM.Location(lonlat.lon, lonlat.lat, this.map.projection));
	}
});
