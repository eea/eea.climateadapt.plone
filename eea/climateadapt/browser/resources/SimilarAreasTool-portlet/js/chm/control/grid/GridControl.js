CHM.Control.Grid.GridControl = Ext.extend(Ext.Panel, {

	searchResults: 'Case Study Search Results',
	
	searchResultsLabel: null,
	
	searchResultsPanel: null,
	
	searchResultsSimilar: 'Case studies in similar biogeographical region',
	
	searchResultsSimilarLabel: null,
	
	searchResultsSimilarPanel: null,
	
	searchResultsDissimilar: 'Case studies in non-similar biogeographical region',
	
	searchResultsDissimilarLabel: null,
	
	searchResultsDissimilarPanel: null,
	
	spacer: null,
	
	similarAreasGridPanel : null,

	dissimilarAreasGridPanel : null,

	initComponent : function() {
    	this.id = 'csst-grid';
    	
    	this.cls = 'csst-panel';
    	
		this.layout = 'anchor';

		this.frame = false;
		
    	this.border = false;
    	
		this.searchResultsLabel = new Ext.form.Label({
			html: '<h1 class="portlet-title"><span class="portlet-title-text">' + this.searchResults + '</span></h1>'
		});
		
		this.searchResultsPanel = new Ext.Panel({
			anchor : '100% 6%',
			border: false,
			items: [this.searchResultsLabel]
		});
		
		this.searchResultsSimilarLabel = new Ext.form.Label({
			html: '<h2 class="csst-grid-subheader"><span class="portlet-title-text">' + this.searchResultsSimilar + '</span></h2>'
		});
		
		this.searchResultsSimilarPanel = new Ext.Panel({
			anchor : '100% 6%',
			border: false,
			items: [this.searchResultsSimilarLabel]
		});

		this.similarAreasGridPanel = new Ext.grid.GridPanel({
			id: 'csst-search-results-similar',
			ref : 'similarAreasFeatureGrid',
			frame : false,
	    	border: false,
			sm : new GeoExt.grid.FeatureSelectionModel(),
			cm : this.createSimilarAreaColumnModel(),
			store : this.createStore(),
			autoExpandColumn : 'itemname',
			anchor : '100% 39%',
			hideHeaders : true
		});
		
		this.spacer = new Ext.Spacer({anchor: '100% 1%'});
		
		this.searchResultsDissimilarLabel = new Ext.form.Label({
			html: '<h2 class="csst-grid-subheader"><span class="portlet-title-text">' + this.searchResultsDissimilar + '</span></h2>'
		});
		
		this.searchResultsDissimilarPanel = new Ext.Panel({
			anchor : '100% 6%',
			border: false,
			items: [this.searchResultsDissimilarLabel]
		});
		
		this.dissimilarAreasGridPanel = new Ext.grid.GridPanel({
			id: 'csst-search-results-dissimilar',
			ref : 'dissimilarAreasFeatureGrid',
			frame : false,
	    	border: false,
			sm : new GeoExt.grid.FeatureSelectionModel(),
			cm : this.createDissimilarAreaColumnModel(),
			store : this.createStore(),
			autoExpandColumn : 'itemname',
			anchor : '100% 38%',
			hideHeaders : true
		});

		this.items = [ this.searchResultsPanel, this.searchResultsSimilarPanel, this.similarAreasGridPanel, this.spacer, this.searchResultsDissimilarPanel, this.dissimilarAreasGridPanel ];

		CHM.Control.Grid.GridControl.superclass.initComponent.call(this);
	},

	createSimilarAreaColumnModel : function() {
		var result = new Ext.grid.ColumnModel({
			defaults : {
				sortable : true
			},
			columns : [
					{
						id : 'measureid',
						name : 'measureid',
						header : '',
						dataIndex : 'measureid',
						width: 24,
						renderer : function(value, metaData, record, rowIndex, colIndex, store) {
							var result = '';
							
							var featured = record.data.feature.attributes.featured;
							if (featured === 'yes') {
								result = '<img src="' + root + 'js/chm/markers/similar_featured_fit.png' + '" alt="Featured case study in similar area"/>';
							} else {
								result = '<img src="' + root + 'js/chm/markers/similar_fit.png' + '" alt="Case study in similar area"/>';
							}
							
							return result;
						}
					}, {
						id : 'itemname',
						name : 'itemname',
						header : 'Name',
						dataIndex : 'itemname'
					}, {
						id : 'featured',
						name : 'featured',
						header : '',
						dataIndex : 'featured',
						width: 75,
						renderer: this.renderFeatured
					}, {
						id : 'newitem',
						name : 'newitem',
						header : '',
						dataIndex : 'newitem',
						width: 50,
						renderer: this.renderNewItem
					} 
				],
		});

		return result;
	},

	createDissimilarAreaColumnModel : function() {
		var result = new Ext.grid.ColumnModel({
			defaults : {
				sortable : true
			},
			columns : [
					{
						id : 'measureid',
						name : 'measureid',
						header : '',
						dataIndex : 'measureid',
						width: 24,
						renderer : function(value, metaData, record, rowIndex, colIndex, store) {
							var result = '';
							
							var featured = record.data.feature.attributes.featured;
							if (featured === 'yes') {
								result = '<img src="' + root + 'js/chm/markers/dissimilar_featured_fit.png' + '" alt="Featured case study in other area"/>';
							} else {
								result = '<img src="' + root + 'js/chm/markers/dissimilar_fit.png' + '" alt="Case study in other area"/>';
							}
							
							return result;
						}
					}, {
						id : 'itemname',
						name : 'itemname',
						header : 'Name',
						dataIndex : 'itemname'
					}, {
						id : 'featured',
						name : 'featured',
						header : '',
						dataIndex : 'featured',
						width: 75,
						renderer: this.renderFeatured
					}, {
						id : 'newitem',
						name : 'newitem',
						header : '',
						dataIndex : 'newitem',
						width: 50,
						renderer: this.renderNewItem
					} 
				],
		});

		return result;
	},
	
	renderFeatured: function(value, metaData, record, rowIndex, colIndex, store) {
		var result = '';

		var featured = record.data.feature.attributes.featured;
		if (featured === 'yes') {
			result = '<img src="' + root + 'js/chm/markers/featured-icon.png' + '" alt="Featured case study"/>';
		}
		
		return result;
	}, 
	
	renderNewItem: function(value, metaData, record, rowIndex, colIndex, store) {
		var result = '';

		var newitem = record.data.feature.attributes.newitem;
		if (newitem === 'yes') {
			result = '<img src="' + root + 'js/chm/markers/new-en.gif' + '" alt="New case study"/>';
		}
		
		return result;
	}, 

	createStore : function() {
		var result = new GeoExt.data.FeatureStore({
			fields : [ {
				id : 'measureid',
				name : 'measureid',
				type : 'string'
			}, {
				id : 'itemname',
				name : 'itemname',
				type : 'string'
			} ],
			proxy : new Ext.data.MemoryProxy(),
			autoLoad : false
		});

		return result;
	},

	format : function(value) {
		console.log(value);

		return value;
	},

	applicationInitialized : function() {
		this.similarAreasGridPanel.store
				.bind(session.similarAreasCasestudiesVector);

		this.similarAreasGridPanel.getSelectionModel().bind(
				session.selectFeatureControl);

		this.dissimilarAreasGridPanel.store
				.bind(session.dissimilarAreasCasestudiesVector);

		this.dissimilarAreasGridPanel.getSelectionModel().bind(
				session.selectFeatureControl);
	}
});
