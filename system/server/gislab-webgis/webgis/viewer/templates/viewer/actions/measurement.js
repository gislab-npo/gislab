
var length = new OpenLayers.Control.Measure(OpenLayers.Handler.Path, {
	immediate: true,
	persist: true,
	geodesic: true, //only for projected projections
	eventListeners: {
		measurepartial: function(evt) {
			Ext.getCmp('measurement-info').setText('Length: ' + evt.measure.toFixed(2) + evt.units);
		},
		measure: function(evt) {
			Ext.getCmp('measurement-info').setText('Length: ' + evt.measure.toFixed(2) + evt.units);
		}
	}
});
var area = new OpenLayers.Control.Measure(OpenLayers.Handler.Polygon, {
	immediate: true,
	persist: true,
	geodesic: true, //only for projected projections
	eventListeners: {
		measurepartial: function(evt) {
			Ext.getCmp('measurement-info').setText('Area: ' + evt.measure.toFixed(2) + evt.units + '<sup>2</sup>');
		},
		measure: function(evt) {
			Ext.getCmp('measurement-info').setText('Area: ' + evt.measure.toFixed(2) + evt.units + '<sup>2</sup>');
		}
	}
});

mappanel.map.addControl(length);
mappanel.map.addControl(area);

var length_button = new Ext.Button({
	enableToggle: true,
	toggleGroup: 'tools',
	iconCls: 'length-measure-icon',
	toggleHandler: function(button, toggled) {
		if (toggled) {
			length.activate();
		} else {
			length.deactivate();
			Ext.getCmp('measurement-info').setText('');
		}
	},
	tooltip: 'Measure length'
});

var area_button = new Ext.Button({
	enableToggle: true,
	toggleGroup: 'tools',
	iconCls: 'area-measure-icon',
	toggleHandler: function(button, toggled) {
		if (toggled) {
			area.activate();
		} else {
			area.deactivate();
			Ext.getCmp('measurement-info').setText('');
		}
	},
	tooltip: 'Measure area'
});
mappanel.getTopToolbar().add(length_button, area_button);
