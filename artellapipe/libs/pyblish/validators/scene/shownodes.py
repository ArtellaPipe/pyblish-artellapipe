#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains scene visibility validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import pyblish.api

import tpDcc as tp


class ShowAllNodes(pyblish.api.Action):
    label = 'Show All Nodes'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Show All Nodes Action is only available in Maya!')

        transforms = tp.Dcc.list_nodes(node_type='transform')
        for node in transforms:
            tp.Dcc.show_node(node)

        return True


class ValidateHidedNodes(pyblish.api.ContextPlugin):
    """
    Checks if current scene has garbage nodes ('hyperLayout', 'hyperView, empty partitions, empty objectSets, etc)
    """

    label = 'Scene - Hide Nodes'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False
    actions = [ShowAllNodes]

    def process(self, context):

        hide_nodes = list()
        transforms = tp.Dcc.list_nodes(node_type='transform')
        for node in transforms:
            is_visible = tp.Dcc.get_attribute_value(node, 'visibility')
            if not is_visible:
                hide_nodes.append(node)

        assert not hide_nodes, 'Hided nodes found in current scene: {}'.format(hide_nodes)
