CHM.Control.Locator.Locator = OpenLayers.Class({

	location : null,

	onlocationchanged : null,

	geocodeservice : null,

	initialize: function() {
		this.geocodeservice = new esri.tasks.Locator(locatorUrl); // "http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer");
		
		dojo.connect(this.geocodeservice, "onAddressToLocationsComplete", this.handleGeocodeResult);

		dojo.connect(this.geocodeservice, "onError", this.handleGeocodeError);
	},

	locate : function(aName) {
		var extent = new esri.geometry.Extent(-31.289030, 27.637496, 44.820546, 71.154709, new esri.SpatialReference({wkid : 4326}));

		var options = {address: {"Address": aName}, outFields: [ "Loc_name" ], searchExtent: extent};

		this.geocodeservice.addressToLocations(options);
	},

	handleGeocodeResult : function(places) {
		session.candidatesStore.removeAll();
		
		if (places.length > 0) {
			// create a Record constructor from a description of the fields
			var CandidateRecord = Ext.data.Record.create([ // creates a subclass of Ext.data.Record
			    {name: 'address', mapping: 'address'},
			    {name: 'x', mapping: 'x', type: 'float'},
			    {name: 'y', mapping: 'y', type: 'float'}
			]);
			var place;

			for ( var i = 0; i < places.length; i++) {
				place = places[i];

				locname = place.attributes.Loc_name;

				if (locname == "Gaz.WorldGazetteer.POI1") {
					// create Record instance
					var candidate = new CandidateRecord(
					    {
					        address: place.address,
					        x: place.location.x,
					        y: place.location.y
					    }
					);
					
					session.candidatesStore.addCandidate(candidate);
				}
			}
		} else {

		}
	},

	handleGeocodeError : function(errorInfo) {

//	},
//
//	getLocation : function() {
//		return this.location;
//	},
//
//	setLocation : function(x, y) {
//		this.location = new CHM.Location(x, y, new OpenLayers.Projection("EPSG:4326"));
//
//		this.handleOnLocationChanged();
//	},
//
//	setOnLocationChanged : function(aFunction) {
//		this.onlocationchanged = aFunction;
//	},
//
//	handleOnLocationChanged : function() {
//		if (this.onlocationchanged != null) {
//			this.onlocationchanged();
//		}
	}
});