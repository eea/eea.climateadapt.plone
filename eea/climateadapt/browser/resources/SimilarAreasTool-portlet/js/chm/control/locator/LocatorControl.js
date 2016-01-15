CHM.Control.Locator.LocatorControl = Ext.extend(Ext.Panel, {
	
	address: 'Address',
	
	location: 'Enter location',
	
	// Text displayed in the button
	locate: '',
	
	panel: null,
	
	button: null,
	
	locationTextField: null,
	
	spacer: null,
	
	candidatesColumnModel: null,
	
	candidatesSelectionModel: null,
	
	candidatesPanel: null,
	
    initComponent : function() {
    	this.id = 'csst-locator';
    	
    	this.cls = 'csst-panel';
    	
    	this.layout = 'anchor';
    	
    	this.border = false;
    	
    	this.locationTextField = new Ext.form.TextField({
    		columnWidth: 1, 
    		enableKeyEvents: true, 
    		value: this.location,
    		id: 'locator-textfield',
    		cls: 'csst-input',
    		x: 0,
    		y: 0,
    		anchor: '100%'
    	});
    	
    	this.locationTextField.addListener('keyup', this.handleLocationTextFieldKeyUp, this);
    	
    	this.locationTextField.addListener('focus', this.focus, this);
    	
    	this.button = new Ext.Button({iconCls: 'x-search', text: this.locate, id: 'locate-button'});
    	
    	this.button.addListener('click', this.handleLocateButtonClick, this);
    	
    	this.panel = new Ext.Panel({
    		anchor: '100%', 
    		border: false, 
    		items: [this.locationTextField, this.button], 
    		layout: 'absolute'
    	});
    	
    	this.panel.addListener('resize', this.resize, this);
    	
    	this.spacer = new Ext.Spacer({height: 2});
    	
	    this.candidatesColumnModel = new Ext.grid.ColumnModel({
	        defaults: {sortable: true},
	        columns: [
  	            {id: 'address', header: this.address, dataIndex: 'address'}
	        ]
	    });
	    
	    this.candidatesSelectionModel = new Ext.grid.RowSelectionModel();
	    
	    this.candidatesSelectionModel.addListener('rowselect', this.handleRowSelect, this);
	    
    	this.candidatesPanel = new Ext.grid.GridPanel({
    		anchor: '100%',
   	    	border: false,
   	    	cm: this.candidatesColumnModel,
   	    	store: session.candidatesStore,
            sm: this.candidatesSelectionModel,
            autoExpandColumn: 'address',
            border: false,
            id: 'locator-results',
            hideHeaders: true
   	    });
    	
    	this.locator = new CHM.Control.Locator.Locator();
    	
    	this.items = [this.panel, this.spacer, this.candidatesPanel];
    	
    	CHM.Control.Locator.LocatorControl.superclass.initComponent.call(this);
    },
    
    resize: function() {
    	if (this.panel.getHeight() === 0) {
    		this.panel.setHeight(this.locationTextField.getHeight());
    	}
    	
    	this.candidatesPanel.setHeight(this.getHeight() - this.panel.getHeight() - this.spacer.getHeight());
    	
    	this.button.setPosition(this.getWidth() - this.button.getWidth());
    }, 
    
    focus: function() {
    	this.locationTextField.setValue("");
    }, 
    
    handleRowSelect: function(aSelectionModel, aRowIndex, aRecord) {
    	session.setLocation(new CHM.Location(aRecord.get('x'), aRecord.get('y'), new OpenLayers.Projection('EPSG:4326')));
    }, 
    
    applicationInitialized: function() {

    },
    
    handleLocateButtonClick: function() {
    	this.locator.locate(this.locationTextField.getValue());
    },
    
    handleLocationTextFieldKeyUp: function(field, e) {
        var k = e.getKey();
        
        if (k == e.RETURN) {
            e.stopEvent();
            
            this.locator.locate(this.locationTextField.getValue());
        } 
	} 
});