$(document).ready(function() {
	Ext.onReady(function() {
		dojo.require("esri.map");
		dojo.require("esri.dijit.Geocoder");
		dojo.ready(function() {
			application = new CHM.Application();
		});
	});
});
