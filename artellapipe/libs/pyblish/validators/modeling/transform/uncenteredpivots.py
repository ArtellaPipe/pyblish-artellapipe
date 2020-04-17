#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains uncentered pivots validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import tpDcc as tp

import pyblish.api


class SelectUncenteredTransforms(pyblish.api.Action):
    label = 'Select Uncentered Transforms'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Center Pivot Action is only available in Maya!')
            return False

        for instance in context:
            if not instance.data['publish'] or not instance.data['_has_failed']:
                continue

            node = instance.data.get('node', None)
            assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

            uncentered_pivots = instance.data.get('uncentered_pivots', None)
            assert uncentered_pivots, 'No uncentered pivots found in instance: {}'.format(instance)

            tp.Dcc.select_object(uncentered_pivots, replace_selection=False)

        return True


class CenterPivot(pyblish.api.Action):
    label = 'Center Pivot'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Center Pivot Action is only available in Maya!')
            return False

        import tpDcc.dccs.maya as maya

        for instance in context:
            if not instance.data['publish']:
                continue

            uncentered_pivots = instance.data.get('uncentered_pivots', None)
            assert uncentered_pivots, 'No uncentered pivots found in instance: {}'.format(instance)

            for node in uncentered_pivots:
                maya.cmds.move(0, 0, 0, '{}.scalePivot'.format(node), '{}.rotatePivot'.format(node), absolute=True)
            for node in uncentered_pivots:
                maya.cmds.xform(node, pivots=[0, 0, 0])

        return True


class ValidateUncenteredPivots(pyblish.api.InstancePlugin):
    """
    Checks if a geometry node has uncentered pivots (pivots that are not centered to (0, 0,, 0) of the world
    Also to be valid, the geometry and all its parent MUST have their pivots centered to (0, 0, 0) of the world
    """

    label = 'Transform - Uncentered Pivots'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False
    actions = [SelectUncenteredTransforms, CenterPivot]

    def process(self, instance):

        import tpDcc.dccs.maya as maya

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        uncentered_pivots = list()
        for node in nodes_to_check:
            if maya.cmds.xform(node, query=True, worldSpace=True, rp=True) != [0, 0, 0]:
                uncentered_pivots.append(node)

        all_parents = tp.Dcc.list_node_parents(node)
        for parent_node in all_parents:
            if maya.cmds.xform(parent_node, query=True, worldSpace=True, rp=True) != [0, 0, 0]:
                uncentered_pivots.append(parent_node)

        if uncentered_pivots:
            instance.data['uncentered_pivots'] = uncentered_pivots

        assert not uncentered_pivots, 'Uncentered pivots found in following geometry nodes: {}'.format(
            uncentered_pivots)

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
