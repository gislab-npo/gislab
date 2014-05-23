var measure_style_config = {
	"Point": {
		pointRadius: 4,
		graphicName: "square",
		fillColor: "white",
		fillOpacity: 1,
		strokeWidth: 1,
		strokeOpacity: 1,
		strokeColor: "#333333"
	},
	"Line": {
		strokeWidth: 3,
		strokeOpacity: 1,
		strokeColor: "#666666",
		strokeDashstyle: "dash"
	},
	"Polygon": {
		strokeWidth: 2,
		strokeOpacity: 1,
		strokeColor: "#666666",
		fillColor: "white",
		fillOpacity: 0.3
	}
	};
var measure_style = new OpenLayers.Style();
measure_style.addRules([new OpenLayers.Rule({symbolizer: measure_style_config})]);

var WebgisStyles = {
	drawing_style: new OpenLayers.StyleMap({
		'default':{
			label: '${title}',
			fontSize: '12px',
			fontWeight: 'bold',
			labelAlign: 'lb',
			strokeColor: '#AA0000',
			strokeOpacity: 1,
			strokeWidth: 1.5,
			fillColor: '#FF0000',
			fillOpacity: 0.5,
			pointRadius: 6,
			labelYOffset: '6',
			labelXOffset: '6',
			fontColor: '#AA0000',
			labelOutlineColor: 'white',
			labelOutlineWidth: 2.5,
			labelOutlineOpacity: 0.5,
		},
		'select': {
			label: '${title}',
			fontSize: '12px',
			fontWeight: 'bold',
			labelAlign: 'lb',
			strokeColor: '#66CCCC',
			strokeOpacity: 1,
			strokeWidth: 1.5,
			fillColor: '#66CCCC',
			fillOpacity: 0.4,
			pointRadius: 6,
			labelYOffset: '6',
			labelXOffset: '6',
			fontColor: '#306060',
			labelOutlineColor: 'white',
			labelOutlineWidth: 2.5,
			labelOutlineOpacity: 0.5,
		},
		'modify': {
			label: '',
			fillColor: '#66CCCC',
			fillOpacity: 0.3,
			strokeColor: '#66CCCC',
			strokeOpacity: 1,
			strokeWidth: 2,
		}
	}),
	featureinfo_style: new OpenLayers.StyleMap({
		'default':{
			strokeColor: '#AA0000',
			strokeOpacity: 1,
			strokeWidth: 1.5,
			fillColor: '#FF0000',
			fillOpacity: 0.5,
			pointRadius: 6,
		},
		'select': {
			strokeColor: '#66CCCC',
			strokeOpacity: 1,
			strokeWidth: 1.5,
			fillColor: '#66CCCC',
			fillOpacity: 0.4,
			pointRadius: 6,
			fontColor: '#306060',
		},
	}),
	measure_style: new OpenLayers.StyleMap({"default": measure_style})
}
