{% load i18n %}

var pointControl = new OpenLayers.Control.Measure(OpenLayers.Handler.Point, {
	persist: true,
	geodesic: {{ projection.is_geographic|yesno:"true,false" }},
	handlerOptions: {
		layerOptions: {
			styleMap: WebgisStyles.measure_style
		}
	},
});

var lengthControl = new OpenLayers.Control.Measure(OpenLayers.Handler.Path, {
	immediate: true,
	persist: true,
	geodesic: {{ projection.is_geographic|yesno:"true,false" }},
	handlerOptions: {
		layerOptions: {
			styleMap: WebgisStyles.measure_style
		}
	},
});
var areaControl = new OpenLayers.Control.Measure(OpenLayers.Handler.Polygon, {
	immediate: true,
	persist: true,
	geodesic: {{ projection.is_geographic|yesno:"true,false" }},
	handlerOptions: {
		layerOptions: {
			styleMap: WebgisStyles.measure_style
		}
	}
});

mappanel.getTopToolbar().add(new WebGIS.MeasureAction({
	id: 'measure-action',
	map: mappanel.map,
	pointMeasureControl: pointControl,
	lengthMeasureControl: lengthControl,
	areaMeasureControl: areaControl,
	cls: 'x-btn-icon',
	iconCls: 'measure-icon',
	tooltip: '{% trans "Measure point coordinates, length or area" %}',
	enableToggle: true,
	toggleGroup: 'measure-draw',
	toggleHandler: function(action, toggled) {
		action.baseAction.toggleHandler(action, toggled);
	}
}));
