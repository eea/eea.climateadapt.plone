CHM.Control.Legend.LegendControl = Ext.extend(Ext.Panel, {
	
	legend: 'Legend',
	
	legendLabel: null,
	
	legendPanel: null,
	
    initComponent : function() {
    	this.layout = 'anchor';
    	
    	this.id = 'csst-legend';
    	
    	this.cls = 'csst-panel';
    	
    	this.legendLabel = new Ext.form.Label({html: '<h1 class="portlet-title"><span class="portlet-title-text">' + this.legend + '</span></h1>'});
    	
    	this.legendPanel = new Ext.Panel({preventBodyReset: true, border: false});
    	
		this.legendPanel.html = '';
		
		this.legendPanel.html += '<table>';
		
		this.legendPanel.html += '<tr>';
		
		this.legendPanel.html += '<td class="csst-legend-image"><img src="' + root + 'js/chm/markers/location_fit.png"></td>';
		
		this.legendPanel.html += '<td class="csst-legend-text">Your selected location</td>';
		
		this.legendPanel.html += '</tr>';
		
		this.legendPanel.html += '<tr>';
		
		this.legendPanel.html += '<td class="csst-legend-image"><img src="' + root + 'js/chm/markers/similar_featured_fit.png"></td>';
		
		this.legendPanel.html += '<td class="csst-legend-text">Featured case study in similar biogeographical region</td>';
		
		this.legendPanel.html += '</tr>';
		
		this.legendPanel.html += '<tr>';
		
		this.legendPanel.html += '<td class="csst-legend-image"><img src="' + root + 'js/chm/markers/similar_fit.png"></td>';
		
		this.legendPanel.html += '<td class="csst-legend-text">Case study in similar biogeographical region</td>';
		
		this.legendPanel.html += '</tr>';
		
		this.legendPanel.html += '<tr>';
		
		this.legendPanel.html += '<td class="csst-legend-image"><img src="' + root + 'js/chm/markers/dissimilar_featured_fit.png"></td>';
		
		this.legendPanel.html += '<td class="csst-legend-text">Featured case study in non-similar biogeographical region</td>';
		
		this.legendPanel.html += '</tr>';

		this.legendPanel.html += '<tr>';
		
		this.legendPanel.html += '<td class="csst-legend-image"><img src="' + root + 'js/chm/markers/dissimilar_fit.png"></td>';
		
		this.legendPanel.html += '<td class="csst-legend-text">Case study in non-similar biogeographical region</td>';
		
		this.legendPanel.html += '</tr>';
		
		this.legendPanel.html += '<tr>';
		
		this.legendPanel.html += '<td class="csst-legend-image"><img src="' + root + 'js/chm/markers/similar_area.png"></td>';
		
		this.legendPanel.html += '<td class="csst-legend-text">Your biogeographical region</td>';
		
		this.legendPanel.html += '</tr>';
		
		this.legendPanel.html += '</table>';
    	
    	this.border = false;
    	
    	this.items = [this.legendLabel, this.legendPanel];
    	
    	CHM.Control.Legend.LegendControl.superclass.initComponent.call(this);
    },
    
    applicationInitialized: function() {
    	
	} 
});
