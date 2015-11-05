Ext.namespace("GeoExt.Toolbar");

GeoExt.Toolbar.ControlDisplay = Ext.extend(Ext.Toolbar.TextItem, {

	control: null,
	map: null,

	onRender: function(ct, position) {
		this.text = this.text ? this.text : '&nbsp;';

		GeoExt.Toolbar.ControlDisplay.superclass.onRender.call(this, ct, position);
		this.control.div = this.el.dom;

		if (!this.control.map && this.map) {
			this.map.addControl(this.control);
		}
	}
});
