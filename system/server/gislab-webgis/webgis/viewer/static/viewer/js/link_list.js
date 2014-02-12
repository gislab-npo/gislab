Ext.namespace("WebGIS.Toolbar");

WebGIS.Toolbar.LinkList = Ext.extend(Ext.Toolbar.Item, {

	links: null,
	separator: ' ',
	textBefore: '',
	alwaysVisible: false,

	constructor: function(config) {
		WebGIS.Toolbar.LinkList.superclass.constructor.call(this, Ext.isString(config) ? {text: config} : config);
	},

	createHtml: function() {
		var link_elements = [];
		Ext.each(this.links, function(link) {
			link_elements.push(String.format('<a href="{0}">{1}</a>', link.href, link.text));
		});
		if (this.textBefore && (link_elements.length > 0 || this.alwaysVisible)) {
			return this.textBefore+' '+link_elements.join(this.separator);
		}
		return link_elements.join(this.separator);
	},

	onRender : function(ct, position) {
		html = this.createHtml()
		this.autoEl = {cls: 'xtb-text', html: html || ''};
		WebGIS.Toolbar.LinkList.superclass.onRender.call(this, ct, position);
	},

	setLinks : function(links) {
		this.links = links;
		if (this.rendered) {
			this.el.update(this.createHtml());
		}
	}
});
