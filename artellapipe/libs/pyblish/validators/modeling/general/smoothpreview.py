#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains smooth preview validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import tpDcc as tp

import pyblish.api


class ValidateGeometrySmoothPreview(pyblish.api.InstancePlugin):
    """
    Checks if mesh has smooth preview attribute disabled
    """

    label = 'General - Smooth Preview Off'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False

    def process(self, instance):

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        smooth_previews = dict()
        for node in nodes_to_check:
            shapes = tp.Dcc.list_shapes(node)
            for shape in shapes:
                is_smooth = tp.Dcc.get_attribute_value(shape, 'displaySmoothMesh') != 0
                if is_smooth:
                    if node not in smooth_previews:
                        smooth_previews[node] = list()
                    smooth_previews[node].append(shape)

        assert not smooth_previews, 'Following geometry nodes have shapes with Smooth Preview enabled: {}'.format(
            smooth_previews)

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