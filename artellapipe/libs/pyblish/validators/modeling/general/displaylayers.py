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


class ValidateGeometryDisplayLayers(pyblish.api.InstancePlugin):
    """
    Checks if current scene has geometries added to a display layer
    """

    label = 'Geometry - Display Layers'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False

    def process(self, instance):

        import maya.cmds as cmds

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        layers = dict()
        for node in nodes_to_check:
            layer = cmds.listConnections(node, type='displayLayer')
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
