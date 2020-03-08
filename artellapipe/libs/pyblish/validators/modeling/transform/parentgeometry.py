#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains parent geometry validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import tpDcc as tp

import pyblish.api


class ValidateParentGeometry(pyblish.api.InstancePlugin):
    """
    Checks if any geometry is parented under other geometry
    """

    label = 'Transform - Parent Geometry'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False

    def process(self, instance):

        import maya.cmds as cmds

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        parent_geometry = list()
        for node in nodes_to_check:
            shape_node = False
            parents = cmds.listRelatives(node, p=True, fullPath=True)
            if parents:
                for parent in parents:
                    parents_children = cmds.listRelatives(parent, fullPath=True)
                    for children in parents_children:
                        if cmds.nodeType(children) == 'mesh':
                            shape_node = True
            if shape_node:
                parent_geometry.append(node)

        assert not parent_geometry, 'Following geometry are parented under other geometry: {}'.format(parent_geometry)

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
