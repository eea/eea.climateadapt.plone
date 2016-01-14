$(document).ready(function() {
	console.log('main: document ready');
	Ext.onReady(function() {
		console.log('ext ready');
		
		dojo.require("esri.map");
		dojo.require("esri.dijit.Geocoder");
	
		dojo.ready(function() {
			console.log('dojo ready');
			
			application = new CHM.Application();
		});
	});
});
