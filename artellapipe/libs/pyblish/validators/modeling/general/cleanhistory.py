#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains clean history validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import tpDcc as tp

import pyblish.api


class CleanHistory(pyblish.api.Action):
    label = 'Clean History'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Clean History Action is only available in Maya!')
            return False

        for instance in context:
            if not instance.data['publish']:
                continue

            node = instance.data.get('node', None)
            assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

            tp.Dcc.delete_history(node)

        return True


class ValidateCleanHistory(pyblish.api.InstancePlugin):
    """
    Checks if a geometry node has clean history
    """

    label = 'General - Clean History'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False
    actions = [CleanHistory]

    def process(self, instance):

        import maya.cmds as cmds

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        history = dict()
        for node in nodes_to_check:
            shape = cmds.listRelatives(node, shapes=True, fullPath=True)
            if shape and cmds.nodeType(shape[0]) == 'mesh':
                shape_history = cmds.listHistory(shape)
                history_size = len(shape_history)
                if history_size > 1:
                    history[node] = shape_history
                    history.append(node)

        assert not history, 'Non cleaned history found in following geometry nodes: {}'.format(history)

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
