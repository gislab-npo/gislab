
// history of saved drawings
var action = new Ext.Action({
	id: 'save-history-action',
	cls: 'x-btn-icon',
	iconCls: 'save-history-icon',
	tooltip: 'History of saved drawings',
	store: new Ext.data.ArrayStore({
		fields: [
			{name: 'title', type: 'string'},
			{name: 'time', type: 'date'},
			{name: 'link', type: 'string'},
			{name: 'info', type: 'string'},
		]
	}),

	handler: function(action) {
		// manually load local data
		//store.loadData(myData);

		// create the Grid
		var grid = new Ext.grid.GridPanel({
			id: 'save-history-grid',
			store: this.store,
			viewConfig: {
				templates: {
					cell: new Ext.Template(
						'<td class="x-grid3-col x-grid3-cell x-grid3-td-{id} x-selectable {css}" style="{style}" tabIndex="0" {cellAttr}>\
							<div class="x-grid3-cell-inner x-grid3-col-{id}" {attr}>{value}</div>\
						</td>'
					)
				}
			},
			columns: [
				{
					id       : 'title',
					header   : 'Title',
					sortable : false,
					dataIndex: 'title',
				},
				{
					id       : 'time',
					header   : 'Time',
					width    : 60, 
					sortable : false,
					dataIndex: 'time',
					renderer : Ext.util.Format.dateRenderer('H:i:s'),
				},
				{
					id       : 'link',
					header   : 'GeoJSON',
					width    : 75,
					sortable : false,
					dataIndex: 'link',
				},
				{
					id       : 'info',
					header   : 'Info',
					width    : 180,
					sortable : false,
					dataIndex: 'info'
				},
			],
			//stripeRows: true,
			autoExpandColumn: 'title',
			// config options for stateful behavior
			stateful: true,
			stateId: 'grid'
		});

		var history_window = new Ext.Window({
			title: 'History of saved drawings',
			width: 500,
			height: 400,
			layout: 'fit',
			items: [grid]
		});
		history_window.show();
		//history_window.alignTo(mappanel.getTopToolbar().getId(), 'bl', [80, 40]);
	}
});
mappanel.getTopToolbar().add(action);
