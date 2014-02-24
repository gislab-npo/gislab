//Search Action

var layers_data = {
	layers: [
{% for layer in layers %}
		{
			name: '{{ layer.name }}',
			value: '{{ layer.name }}',
			attributes: [
			{% for attrib in layer.attributes %}
				{name: '{{ attrib.name }}', type: '{{ attrib.type }}'},
			{% endfor %}
			]
		},
{% endfor %}
	]
};

var search_items = [
	{
		xtype: 'tbspacer'
	}, {
		xtype: 'combo',
		id: 'search-layer-combobox',
		width: 100,
		mode: 'local',
		triggerAction: 'all',
		forceSelection: true,
		store: new Ext.data.JsonStore({
			data: layers_data,
			storeId: 'search-layer-store',
			root: 'layers',
			fields: [{
				name: 'name',
				type: 'string'
			}, {
				name: 'value',
				type: 'string'
			}]
		}),
		valueField: 'value',
		displayField: 'name',
		listeners: {
			afterrender: function(combo) {
				if (combo.getStore().getCount() == 0) {
					return;
				}
				var recordSelected = combo.getStore().getAt(0);
				combo.setValue(recordSelected.get('name'));
				combo.fireEvent('select', combo, recordSelected, 0);
			},
			select: function (combo, record, index) {
				var attributes_combo = Ext.getCmp('search-attribute-combobox');
				attributes_combo.store.loadData(record.json);
				if (attributes_combo.getStore().getCount() > 0) {
					var record = attributes_combo.getStore().getAt(0);
					attributes_combo.setValue(record.get('name'));
					attributes_combo.fireEvent('select', attributes_combo, record, 0);
					/*
					attributes_combo.bindStore(new Ext.data.JsonStore({
						// store configs
						data: record.json,
						storeId: 'search-attributes-store',
						// reader configs
						root: 'attributes',
						fields: [{
							name: 'name',
							type: 'string'
						}]
					}));*/
				}
			}
		}
	}, {
		xtype: 'tbspacer'
	}, {
		xtype: 'combo',
		id: 'search-attribute-combobox',
		width: 120,
		mode: 'local',
		triggerAction: 'all',
		forceSelection: true,
		store: new Ext.data.JsonStore({
			data: {attributes: []},
			storeId: 'search-attributes-store',
			root: 'attributes',
			fields: [{
				name: 'name',
				type: 'string'
			}, {
				name: 'type',
				type: 'string'
			}]
		}),
		valueField: 'name',
		displayField: 'name',
		listeners: {
			select: function (combo, record, index) {
				var operators_combo = Ext.getCmp('search-operator-combobox');
				var attrib_type = record.json['type'];
				if (combo.attrib_type == attrib_type) {
					return;
				}
				combo.attrib_type = attrib_type;
				Ext.getCmp('search-value-field').setType(attrib_type);
				if (attrib_type == 'integer' || attrib_type == 'double') {
					operators = [
						{name: '<', value: '<'},
						{name: '<=', value: '<='},
						{name: '>', value: '>'},
						{name: '>=', value: '>='},
						{name: '=', value: '='},
						{name: '!=', value: '!='},
						{name: 'IN', value: 'IN'},
					]
				} else {
					operators = [
						{name: '=', value: '='},
						{name: '!=', value: '!='},
						{name: 'IN', value: 'IN'},
					]
				}
				operators_combo.store.loadData({operators: operators});
				if (operators_combo.getStore().getCount()) {
					var record = operators_combo.getStore().getAt(0);
					operators_combo.setValue(record.get('name'));
					operators_combo.fireEvent('select', operators_combo, record, 0);
				}
			}
		}
	}, {
		xtype: 'combo',
		id: 'search-operator-combobox',
		width: 40,
		mode: 'local',
		triggerAction: 'all',
		forceSelection: true,
		store: new Ext.data.JsonStore({
			data: {operators: []},
			storeId: 'search-operator-store',
			root: 'operators',
			fields: [{
				name: 'name',
				type: 'string'
			}]
		}),
		valueField: 'name',
		displayField: 'name',
		listeners: {

		}
	}, {
		xtype: 'tbspacer'
	}, {
		xtype: 'container',
		id: 'search-value-field',
		items: [],

		setType: function(type) {
			var thiz = Ext.getCmp('search-value-field');
			thiz.type = type;
			thiz.removeAll();
			var comp;
			if (type == 'integer') {
				comp = {
					xtype: 'numberfield',
					allowDecimals: false
				}
			} else if (type == 'double') {
				comp = {
					xtype: 'numberfield',
					allowDecimals: true
				}
			} else {
				comp = {
					xtype: 'textfield',
					allowDecimals: false
				}
			}
			thiz.add(comp);
			thiz.doLayout();
		},
		getValue: function() {
			return Ext.getCmp('search-value-field').get(0).getValue();
		}
	}, {
		xtype: 'tbspacer'
	}, {
		xtype: 'label',
		text: 'Limit:'
	}, {
		xtype: 'tbspacer'
	}, {
		xtype: 'combo',
		id: 'search-limit-combobox',
		width: 40,
		mode: 'local',
		triggerAction: 'all',
		forceSelection: true,
		store: new Ext.data.ArrayStore({
			data: [[5], [10], [20]],
			storeId: 'search-limit-store',
			fields: [{
				name: 'value',
				type: 'int'
			}]
		}),
		valueField: 'value',
		displayField: 'value',
		listeners: {
			afterrender: function(combo) {
				var recordSelected = combo.getStore().getAt(0);
				combo.setValue(recordSelected.get('value'));
			},
		}
	}, new Ext.Action({
		xtype: 'action',
		tooltip: 'Search',
		cls: 'x-btn-icon',
		iconCls: 'search-icon',
		format: new OpenLayers.Format.WMSGetFeatureInfo(),

		handler: function(action) {
			console.log("FEATUREINFO SEARCH");
			//Ext.urlAppend({{ ows_url }}, Ext.urlEncode({
			
			var layer = Ext.getCmp('search-layer-combobox').getValue();
			var attribute = Ext.getCmp('search-attribute-combobox').getValue();
			var operator = Ext.getCmp('search-operator-combobox').getValue();
			var value = Ext.getCmp('search-value-field').getValue();
			if (operator == 'IN') {
				// Format to proper list value string. Spaces are very important. Example: " ( 'val1' , 'val2' , ... ) "
				var list_values = [];
				Ext.each(value.split(','), function(list_value) {
					list_values.push(list_value.trim());
				});
				value = String.format(" ( '{0}' ) ", list_values.join("' , '"));
			} else {
				value = String.format("'{0}'", value);
			}
			var features_count = Ext.getCmp('search-limit-combobox').getValue();
			console.log(String.format('{0}:"{1}" {2} {3}', layer, attribute, operator, value))

			Ext.Ajax.request({
				method: 'GET',
				url: '{{ getfeatureinfo_url }}',
				params: {
					SERVICE: 'WMS',
					REQUEST: 'GetFeatureInfo',
					FEATURE_COUNT: features_count,
					INFO_FORMAT: 'application/vnd.ogc.gml',
					SRS: '{{ projection }}',
					LAYERS: layer,
					QUERY_LAYERS: layer,
					FILTER: String.format('{0}:"{1}" {2} {3}', layer, attribute, operator, value)
				},
				success: function(response) {
					var doc = response.responseXML;
					if(!doc || !doc.documentElement) {
						doc = response.responseText;
					}
					//this.format = new OpenLayers.Control.WMSGetFeatureInfo({infoFormat: 'application/vnd.ogc.gml', maxFeatures: 10}).format;
					//this.format = new OpenLayers.Format.WMSGetFeatureInfo();
					this.format = new OpenLayers.Format.GML({
						//gmlns: 'http://qgis.org/gml',
						//featureName: layer,
					});
					var features = this.format.read(doc);
					Ext.getCmp('featureinfo-panel').showFeatures(features);
				},
				failure: function(response, opts) {
					Ext.MessageBox.alert("Error", "Searching failed.");
				}
			});
		}
	}),
]
mappanel.getTopToolbar().add('-', search_items);
