var measure_style_config = {
	"Point": {
		pointRadius: 4,
		graphicName: "square",
		fillColor: "white",
		fillOpacity: 1,
		strokeWidth: 2,
		strokeOpacity: 1,
	},
	"Line": {
		strokeWidth: 3,
		strokeOpacity: 1,
	},
	"Polygon": {
		strokeWidth: 2,
		strokeOpacity: 1,
		fillOpacity: 0.3
	}
};
var measure_style = new OpenLayers.Style();
measure_style.addRules([new OpenLayers.Rule({symbolizer: measure_style_config})]);


var drawing_style = new OpenLayers.StyleMap({
	'default':{
		label: '${title}',
		fontSize: '12px',
		fontWeight: 'bold',
		labelAlign: 'lb',
		strokeColor: '#AA0000',
		strokeOpacity: 1,
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
		strokeColor: '#66CCCC',
		fillColor: '#66CCCC',
		fillOpacity: 0.4,
		fontColor: '#306060',
	},
	'modify': {
		label: '',
		fillColor: '#66CCCC',
		fillOpacity: 0.3,
		strokeColor: '#66CCCC',
		strokeOpacity: 1,
	}
});

var default_drwing_style_config = {
	"Point": {
		strokeWidth: 2,
	},
	"Line": {
		strokeWidth: 3,
	},
	"Polygon": {
		strokeWidth: 2,
	}
};
drawing_style.styles.default.addRules([new OpenLayers.Rule({symbolizer: default_drwing_style_config})]);

var WebgisStyles = {
	drawing_style: drawing_style,
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
