#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains display layers validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import tpDcc as tp

import pyblish.api


class RemoveFromDisplayLayer(pyblish.api.Action):
    label = 'Remove From Display Layer'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Remove From Display Layer Action is only available in Maya!')
            return False

        import tpDcc.dccs.maya as maya

        maya.cmds.undoInfo(openChunk=True)

        try:
            for instance in context:
                if not instance.data['publish']:
                    continue

                node = instance.data.get('node', None)
                assert node and tp.Dcc.object_exists(
                    node), 'No valid node found in current instance: {}'.format(instance)

                layer = maya.cmds.listConnections(node, type='displayLayer')
                if not layer:
                    continue

                maya.cmds.editDisplayLayerMembers('defaultLayer', node)
                layer = maya.cmds.listConnections(node, type='displayLayer')
                if layer and layer != 'defaultLayer':
                    self.log.error('Impossible to remove node from displayLayer: {}'.format(node, layer))
                    continue
        except Exception as exc:
            self.log.error('Error while removing nodes from display layers: {}'.format(exc))
        finally:
            maya.cmds.undoInfo(closeChunk=False)

        return True


class ValidateGeometryDisplayLayers(pyblish.api.InstancePlugin):
    """
    Checks if current scene has geometries added to a display layer
    """

    label = 'Geometry - Display Layers'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False
    actions = [RemoveFromDisplayLayer]

    def process(self, instance):

        import tpDcc.dccs.maya as maya

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        layers = dict()
        for node in nodes_to_check:
            layer = maya.cmds.listConnections(node, type='displayLayer')
            if layer:
                if layer not in layers:
                    layers[layer] = list()
                layers[layer].append(node)

        assert not layers, 'Geometries in display layers found: {}'.format(layers)

    def _nodes_to_check(self, node):

        valid_nodes = list()
        nodes = tp.Dcc.list_children(node=node, all_hierarchy=True, full_path=True, children_type='transform')
        if not nodes:
            nodes = [node]
        else:
            nodes.append(node)

        for node in nodes:
            shapes = tp.Dcc.list_shapes(node=node, full_path=True)
            if not shapes:
                continue
            valid_nodes.append(node)

        return valid_nodes
