(function() {
	'use strict';

	angular
		.module('gl.layersControl')
		.controller('LayersController', LayersController);

	function LayersController($scope, $timeout, $sce, projectProvider, mapBuilder, layersControl) {
		$scope.topics = projectProvider.config.topics;
		$scope.selectedTopic = {};

		function visibleLayersHtml(layersTreeModel, topic) {
			var text = '';
			var indent = '';
			var visit_node = function(layerModel) {
				if (layerModel.layers) {
					indent += '&nbsp;&nbsp;';
					var children_content = [];
					layerModel.layers.forEach(function(childModel) {
						var child_content = visit_node(childModel);
						if (child_content) {
							children_content.push(child_content);
						}
					});
					indent = indent.slice(12);
					if (children_content.length > 0) {
						return indent+'<label class="layer-group">'+layerModel.title+'</label><br />'+children_content.join('');
					}
				} else if (topic.visible_overlays.indexOf(layerModel.name) != -1) {
					return '<span>'+indent+'- '+layerModel.title+'</span><br />';
				}
			};
			var html = [];
			layersTreeModel.forEach(function(layerModel) {
				html.push(visit_node(layerModel));
			});
			return $sce.trustAsHtml(html.join('\n'));
		}

		$scope.topicDetail = function(topic, fn) {
			if (!topic.detail) {
				//console.log('topicDetail: '+topic.title);
				topic.detail = {
					abstract: topic.abstract,
					visibleLayers: visibleLayersHtml(projectProvider.layers.tree, topic)
				}
				$timeout(function() {
					fn(topic);
				}, 15);
			} else {
				fn(topic);
			}
		}

		$scope.loadTopic = function(topic) {
			layersControl.setVisibleLayers(projectProvider.map, topic.visible_overlays);
			$scope.app.panel.layersTreeView.setSelectedNodes(topic.visible_overlays)
		}

		$scope.setBaseLayer = function(layername) {
			if (!projectProvider.map)
				return;
			layersControl.setBaseLayer(projectProvider.map, layername)
		};

		$scope.layersVisibilityChanged = function(node) {
			$scope.selectedTopic.index = null;
			var visible_layers = [];
			$scope.layers.list.forEach(function(layer_data) {
				if (!layer_data.isGroup && layer_data.visible) {
					visible_layers.push(layer_data.name);
				}
			});
			layersControl.setVisibleLayers(projectProvider.map, visible_layers);
		};

		$scope.baseLayers = projectProvider.baseLayers;
		$scope.layers = projectProvider.layers;
		$scope.layers.list.concat($scope.baseLayers.list).forEach(function(layer_data) {
			if (!layer_data.isGroup) {
				if (projectProvider.config.scales) {
					if (!angular.isDefined(layer_data.visibility_scale_max)) {
						layer_data.visibility_scale_max = projectProvider.config.scales[0];
					}
					if (!angular.isDefined(layer_data.visibility_scale_min)) {
						layer_data.visibility_scale_min = projectProvider.config.scales[projectProvider.config.scales.length-1];
					}
				}
			}
		});

		var test_base_layers = [
			{
				title: 'Group',
				layers: [
					{title: 'S1'},
					{title: 'S2'},
					{
						title: 'Subgroup',
						layers: [
							{title: 'SS1'},
							{
								title: 'Subsub-group',
								layers: [
									{title: 'SSS1'},
									{title: 'SSS2'}
								]
							},
							{title: 'Subsubitem3'},
							{
								title: 'Subsub-group',
								layers: [
									{title: 'SSS3'},
									{title: 'SSS4'},
									{title: 'SSS5', visible: true},
									{title: 'SSS6'}
								]
							},
						]
					}
				]
			},
			{title: 'I1'},
			{title: 'I2'},
		];
		//$scope.baseLayers.tree = test_base_layers;

		/* share the same reference to selected base layer in every node of tree model */
		var selectedBaseLayer = {}
		$scope.baseLayers.list.forEach(function(base_layer) {
			base_layer.selected = selectedBaseLayer;
			if (base_layer.visible) {
				selectedBaseLayer.name = base_layer.name;
			}
		});
	};
})();
