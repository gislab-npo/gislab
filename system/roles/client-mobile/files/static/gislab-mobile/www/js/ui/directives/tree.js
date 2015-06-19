(function() {
	'use strict';

	angular
	.module('gl.ui')
	.directive('glTreeView', glTreeView)
	.directive('glTreeNode', glTreeNode)
	.directive('glCheckTreeView', glCheckTreeView)
	.directive('glCheckTreeNode', glCheckTreeNode)
	.directive('glTreeGroupTemplate', glTreeGroupTemplate)
	.directive('glTreeLeafTemplate', glTreeLeafTemplate);

	function glTreeView() {
		return {
			restrict: 'A',
			scope: {
				rootNodes: '=glTreeView',
				idAttribute: '@glTreeIdAttribute',
				labelAttribute: '@glTreeLabelAttribute',
				childrenAttribute: '@glTreeChildrenAttribute',
				changeHandler: '&glTreeViewChangeHandler'
			},
			transclude: true,
			link: function(scope, iElem, iAttrs, ctrl, transclude) {
				transclude(scope, function(clone) {
					iElem.append(clone);
				});
			},
			controller: ['$scope', function($scope) {
				$scope.children = function(node) {
					return node[$scope.childrenAttribute];
				};
			}]
		}
	}

	function glTreeNode() {
		return {
			restrict: 'A',
			scope: true,
			transclude: true,
			controller: ['$scope', '$compile', '$element', function($scope, $compile, $element) {
				$scope.nodeSelected = function(node) {
					$scope.changeHandler({node: node});
				}

				$scope.buildHtml = function() {
					var template = $scope.$node.isGroup? $scope.groupTemplate : $scope.leafTemplate;
					$element.append($compile(template)($scope));
				};
			}],
			compile: function(tElem, tAttrs) {
				return {
					pre: function(scope, iElem, iAttrs) {
						var nodeModel = scope.$eval(iAttrs.glTreeNode);
						scope.$node = {
							data: nodeModel,
							treeDepth: scope.$node? scope.$node.treeDepth+1 : 1,
							isGroup: nodeModel.hasOwnProperty(scope.childrenAttribute),
							isExpanded: true
						};
						scope.buildHtml();
					}
				};
			}
		}
	}

	function CheckTreeView(rootNodes, idAttribute, childrenAttribute, selectAttribute) {
		this.rootNodes = rootNodes;
		this.idAttribute = idAttribute;
		this.childrenAttribute = childrenAttribute;
		this.selectAttribute = selectAttribute;
		this._nodesElements = {};
		this._nodesParents = {};
	};

	CheckTreeView.prototype.addNode = function(node, parent, domElement) {
		this._nodesParents[node[this.idAttribute]] = parent;
		this._nodesElements[node[this.idAttribute]] = domElement;
	};

	CheckTreeView.prototype.getParentNode = function(node) {
		return this._nodesParents[node[this.idAttribute]];
	};

	CheckTreeView.prototype.isGroup = function(node) {
		return node.hasOwnProperty(this.childrenAttribute);
	};

	CheckTreeView.prototype.children = function(node) {
		return node[this.childrenAttribute];
	};

	CheckTreeView.prototype.selectAll = function(node, isSelected) {
		this.children(node).forEach(function(child) {
			if (this.isGroup(child)) {
				this.selectAll(child, isSelected);
				this.setGroupCheckState(child, isSelected);
			}
			child[this.selectAttribute] = isSelected;
		}, this);
	};

	CheckTreeView.prototype.groupCheckState = function(node) {
		var allChecked = true;
		var allUnchecked = true;
		this.children(node).forEach(function(child) {
			if (child[this.selectAttribute] !== true) {
				allChecked = false;
			}
			if (child[this.selectAttribute] !== false) {
				allUnchecked = false;
			}
		}, this);
		return allChecked? true : allUnchecked? false : null;
	};

	CheckTreeView.prototype.setGroupCheckState = function(node, isSelected) {
		this._nodesElements[node[this.idAttribute]].prop('indeterminate', isSelected === null);
		node[this.selectAttribute] = isSelected;
	}

	CheckTreeView.prototype.updateParentCheckState = function(node) {
		var parent = this.getParentNode(node);
		while(parent) {
			this.setGroupCheckState(parent, this.groupCheckState(parent));
			parent = this.getParentNode(parent);
		}
	};

	CheckTreeView.prototype.updateGroupsCheckState = function() {
		var fn = function(layers) {
			layers.forEach(function(node) {
				var children = this.children(node);
				if (children) {
					fn(children);
					this.setGroupCheckState(node, this.groupCheckState(node));
				}
			}, this);
		}.bind(this);
		fn(this.rootNodes);
	};

	CheckTreeView.prototype.setSelectedNodes = function(selectedNodes) {
		var fn = function(layers) {
			layers.forEach(function(node) {
				var children = this.children(node);
				if (children) {
					fn(children);
					this.setGroupCheckState(node, this.groupCheckState(node));
				} else {
					var visible = selectedNodes.indexOf(node[this.idAttribute]) != -1;
					node[this.selectAttribute] = visible;
				}
			}, this);
		}.bind(this);
		fn(this.rootNodes);
	};

	function glCheckTreeView($timeout, $parse) {
		return {
			restrict: 'A',
			scope: {
				rootNodes: '=glCheckTreeView',
				idAttribute: '@glTreeIdAttribute',
				selectAttribute: '@glTreeSelectedAttribute',
				childrenAttribute: '@glTreeChildrenAttribute',
				changeHandler: '&glTreeViewChangeHandler'
			},
			transclude: true,
			link: function(scope, iElem, iAttrs, ctrl, transclude) {
				transclude(scope, function(clone) {
					iElem.append(clone);
				});
				if (iAttrs.glVar) {
					$parse(iAttrs.glVar).assign(scope.$parent, scope.treeView);
				}
				$timeout(function() {
					scope.treeView.updateGroupsCheckState();
				});
			},
			controller: ['$scope', function($scope) {
				$scope.nodeSelected = function(node, isSelected) {
					if ($scope.treeView.isGroup(node)) {
						$scope.treeView.selectAll(node, isSelected);
					}
					$scope.treeView.updateParentCheckState(node);
					$scope.changeHandler({node: node});
				};
				$scope.treeView = new CheckTreeView($scope.rootNodes, $scope.idAttribute, $scope.childrenAttribute, $scope.selectAttribute);
			}]
		}
	}

	function glCheckTreeNode() {
		return {
			restrict: 'A',
			scope: true,
			controller: ['$scope', '$compile', '$element', function($scope, $compile, $element) {
				$scope.buildHtml = function() {
					var template = $scope.treeView.isGroup($scope.$node.data)? $scope.groupTemplate : $scope.leafTemplate;
					$element.append($compile(angular.element(template))($scope));
				};
			}],
			compile: function(tElem, tAttrs) {
				return {
					pre: function(scope, iElem, iAttrs) {
						var nodeModel = scope.$eval(iAttrs.glCheckTreeNode);
						if (!scope.treeView.isGroup(nodeModel) && !angular.isDefined(nodeModel[scope.selectAttribute])) {
							nodeModel[$scope.selectAttribute] = false;
						}
						scope.$node = {
							data: nodeModel,
							treeDepth: scope.$node? scope.$node.treeDepth+1 : 1,
							isExpanded: true
						};
						scope.buildHtml();
					},
					post: function(scope, iElem, iAttrs) {
						scope.treeView.addNode(scope.$node.data, scope.$parent.$node? scope.$parent.$node.data : null, angular.element(iElem.children()[0]).find('input'));
					}
				};
			}
		};
	}

	function glTreeGroupTemplate() {
		return {
			restrict: 'A',
			compile: function(tElem, tAttrs) {
				var template = tElem.html();
				return {
					pre: function(scope, iElem, iAttrs) {
						scope.groupTemplate = template;
						iElem.remove();
					}
				}
			}
		}
	}

	function glTreeLeafTemplate() {
		return {
			restrict: 'A',
			compile: function(tElem, tAttrs) {
				var template = tElem.html();
				return {
					pre: function(scope, iElem, iAttrs) {
						scope.leafTemplate = template;
						iElem.remove();
					}
				}
			}
		}
	}

	function glCheckTreeView2() {
		return {
			restrict: 'A',
			scope: {
				rootNodes: '=glCheckTreeView',
				selectAttribute: '@glTreeSelectedAttribute',
				childrenAttribute: '@glTreeChildrenAttribute',
				changeHandler: '&glTreeViewChangeHandler'
			},
			transclude: true,
			link: function(scope, iElem, iAttrs, ctrl, transclude) {
				transclude(scope, function(clone) {
					iElem.append(clone);
				});
				scope.updateGroupsCheckState();
			},
			controller: ['$scope', '$timeout', function($scope, $timeout) {
				$scope.treeDepth = 0;
				$scope.isGroup = function(node) {
					return node.hasOwnProperty($scope.childrenAttribute);
				};
				$scope.children = function(node) {
					return node[$scope.childrenAttribute];
				};

				$scope.nodeSelected = function(node, isSelected) {
					$scope.updateParentCheckState(node);
					$scope.changeHandler({node: node});
				};
				$scope.groupCheckState = function(node) {
					return $scope.children(node).some(function(child) {
						if (child[$scope.selectAttribute] === true) {
							return true;
						}
					});
				};
				$scope.updateParentCheckState = function(node) {
					var parent = this.getParentNode(node);
					while(parent) {
						parent[$scope.selectAttribute] = $scope.groupCheckState(parent);
						parent = this.getParentNode(parent);
					}
				};
				$scope.updateGroupsCheckState = function() {
					$timeout(function() {
						var fn = function(layers) {
							layers.forEach(function(node) {
								var children = $scope.children(node);
								if (children) {
									fn(children);
									node[$scope.selectAttribute] = $scope.groupCheckState(node);
								}
							});
						}
						fn($scope.rootNodes);
					});
				};
				$scope.rootNodes.updateGroupsCheckState = $scope.updateGroupsCheckState;
			}]
		}
	}
})();
