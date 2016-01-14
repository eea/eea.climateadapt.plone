CHM.Application = Ext.extend(Ext.Panel,  {
	
	margin: 20,
	
	titleControl: null,
	
	mapControl: null,
	
	optionsControl: null,
	
	legendControl: null,
	
	locatorControl: null,
	
	gridControl: null,
	
	help: 'Determine your location of interest by clicking in the map or by searching and selecting it through the Locate function. The tool displays case studies from the CLIMATE-ADAPT quality checked knowledge base, differentiating between case studies in and outside the similar biogeographical region.</div><div>Additionally you may choose a climate impact or adaptation sector of your interest to refine the selection. Click on a case study on the map to access its details.',
	
	helpButton: null,
	
	actionButtonPanel: null,
	
    initComponent : function() {
    	Ext.QuickTips.init();
    	
		session = new CHM.Session();
		
    	this.renderTo = 'csst_element';
		
		this.height = document.getElementById(this.renderTo).offsetHeight;
		
		this.width = document.getElementById(this.renderTo).offsetWidth;
		
		this.border = false;
    	
		this.layout = 'absolute';
    	
		this.titleControl = new Ext.form.Label();
		
		this.titleControl.html = '<h1 class="portlet-title"><span class="portlet-title-text">Case Study Search tool</span></h1>';
		
		var helptooltip = new Ext.ToolTip({   
			title: 'Case Study Search Tool',
			id: '',
            anchor: 'left',
            text: this.help,
            width: 415,
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
		
    	this.helpButton = new Ext.Button({iconCls: 'x-help', tooltip: helptooltip, id: 'help-button', disabled: false});
    	
    	var panel = new Ext.Panel({x: this.margin, y: this.margin, border: false, id: 'csst-title-help', items: [this.titleControl, {xtype: 'label', html: '&nbsp;'}, this.helpButton], layout: 'column'});
		
    	this.mapControl = new CHM.Control.Map.MapControl({width: this.width / 4 * 3 - (this.margin * 1.5), height: this.height / 8 * 3 - (this.margin / 2) - (this.margin / 2), x: this.margin, y: this.height / 8 * 1 + (this.margin / 2)});
    	
    	this.gridControl = new CHM.Control.Grid.GridControl({width: this.width / 4 * 3 - this.margin - (this.margin / 2), height: this.height / 8 * 4 - this.margin, x: this.margin, y: this.height / 8 * 4 + (this.margin * 2)});
    	
    	this.locatorControl = new CHM.Control.Locator.LocatorControl({width: this.width / 4 * 1.5 - (this.margin / 2) - this.margin, height: this.height / 8 * 1 - this.margin - (this.margin / 2), x: this.width / 4 * 2.5 + (this.margin / 2), y: this.margin * 1.5});
    	
    	this.optionsControl = new CHM.Control.Options.OptionsControl({width: this.width / 4 * 1 - (this.margin / 2) - this.margin, height: this.height / 8 * 1.5, x: this.width / 4 * 3 + (this.margin / 2), y: this.height / 8 * 1 + (this.margin / 2)});
    	
    	this.legendControl = new CHM.Control.Legend.LegendControl({width: this.width / 4 * 1 - (this.margin / 2) - this.margin, height: this.height / 8 * 2.5, x: this.width / 4 * 3 + (this.margin / 2), y: this.height / 8 * 2.5 + (this.margin / 2) + this.margin});
    	
    	this.actionButtonPanel = new Ext.Panel({width: this.width / 4 * 1 - (this.margin / 2) - this.margin, height: this.height / 8 * 0.75, x: this.width / 4 * 3 + (this.margin / 2), y: this.height / 8 * 2.8 + (this.margin / 2) + this.margin + this.margin + this.height / 8 * 2.05, html: '<a href="/share-your-info/case-studies" class="bluebutton">Share your information</a>', border: false});
    	
		this.defaults = {collapsible : false, split : true};

		this.items = [panel, this.mapControl, this.gridControl, this.locatorControl, this.optionsControl, this.legendControl, this.actionButtonPanel];
    	
    	CHM.Application.superclass.initComponent.call(this);
    	
    	this.addListener('afterrender', this.handleAfterRender, this);
    }, 

	handleAfterRender: function() {
		this.removeListener('afterrender', this.handleAfterRender, this);
		
		this.mapControl.applicationInitialized();
		
		this.optionsControl.applicationInitialized();
		
		this.gridControl.applicationInitialized();
		
		this.helpButton.x = this.margin + this.titleControl.getWidth() + this.margin;
		
		var x = this.mapControl.getPosition()[0] + 10;
		
		var y = this.mapControl.getPosition()[1] - 10;
		
		this.mapControl.setOffsetX(x);
		
		this.mapControl.setOffsetY(y);
	}
});
Ext.reg('application', CHM.Application);
