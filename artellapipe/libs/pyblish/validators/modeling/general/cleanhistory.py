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

        import tpDcc.dccs.maya as maya

        for instance in context:
            if not instance.data['publish']:
                continue

            node = instance.data.get('node', None)
            assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

            tp.Dcc.delete_history(node)
            shapes = maya.cmds.listRelatives(node, shapes=True, fullPath=True) or list()
            for shape in shapes:
                shape_short = tp.Dcc.node_short_name(shape)
                tp.Dcc.delete_history(shape)

                # We remove groupdIds and clean connections to memberWireframeColors
                shape_history = maya.cmds.listHistory(shape)
                for history_node in shape_history:
                    if maya.cmds.nodeType(history_node) == 'groupId':
                        maya.cmds.delete(history_node)
                    elif maya.cmds.nodeType(history_node) == 'shadingEngine':
                        if maya.cmds.attributeQuery('memberWireframeColor', node=history_node, exists=True):
                            member_wire_color_attr = '{}.memberWireframeColor'.format(history_node)
                            shading_engine_connections = maya.cmds.listConnections(member_wire_color_attr, plugs=True)
                            if shading_engine_connections:
                                for cnt in shading_engine_connections:
                                    connected_node = cnt.split('.')[0].split(':')[-1]
                                    if connected_node != shape_short:
                                        continue
                                    maya.cmds.disconnectAttr(member_wire_color_attr, cnt)
                                    # Make sure that shapes do not loose its set
                                    maya.cmds.sets(shape, edit=True, forceElement=history_node)

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

        import tpDcc.dccs.maya as maya

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        history = dict()
        for node in nodes_to_check:
            shapes = maya.cmds.listRelatives(node, shapes=True, fullPath=True)
            if shapes and maya.cmds.nodeType(shapes[0]) == 'mesh':
                shape_history = maya.cmds.listHistory(shapes)
                history_size = len(shape_history)
                if history_size > 1:
                    history[node] = shape_history

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
