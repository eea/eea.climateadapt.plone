CHM.Control.Locator.Candidate.CandidatesStore = Ext.extend(Ext.data.Store, {

	constructor : function(config) {
		CHM.Control.Locator.Candidate.CandidatesStore.superclass.constructor.call(this, Ext.apply(config, {}));
	},

	addCandidate : function(aCandidate) {
		var candidate = this.findCandidate(aCandidate);

		if (candidate == null) {
			this.add(aCandidate);
		}
	},

	findCandidate : function(aCandidate) {
		var result = null;
		
		var address1 = aCandidate.get('address');
		
		var x1 = aCandidate.get('x');
		
		var y1 = aCandidate.get('y');

		for (var i = 0; i < this.getCount(); i ++) {
			var candidate = this.getAt(i);
			
			var address2 = candidate.get('address');
			
			var x2 = candidate.get('x');
			
			var y2 = candidate.get('y');
			
			var equal = address1 == address2 && 
				Math.round(x1 * 1000) == Math.round(x2 * 1000) && 
				Math.round(y1 * 1000) == Math.round(y2 * 1000);

			if (equal) {
				result = candidate;
				
				break;
			}
			
		}

		return result;
	}
});
