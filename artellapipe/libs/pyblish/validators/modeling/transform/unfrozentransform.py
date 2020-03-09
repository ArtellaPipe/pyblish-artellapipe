#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains unfrozen transform validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import tpDcc as tp

import pyblish.api


class FreezeTransforms(pyblish.api.Action):
    label = 'Freeze Transforms'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Freeze Transforms Action is only available in Maya!')
            return False

        for instance in context:
            if not instance.data['publish']:
                continue

            node = instance.data.get('node', None)
            assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

            tp.Dcc.freeze_transforms(node, clean_history=True)


class ValidateUnfrozenTransforms(pyblish.api.InstancePlugin):
    """
    Checks if a geometry node has unfrozen transforms
    """

    label = 'Transform - Unfrozen Transforms'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False
    actions = [FreezeTransforms]

    def process(self, instance):

        import tpDcc.dccs.maya as maya

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        unfrozen_transforms = list()
        for node in nodes_to_check:
            translation = maya.cmds.xform(node, query=True, worldSpace=True, translation=True)
            rotation = maya.cmds.xform(node, query=True, worldSpace=True, rotation=True)
            scale = maya.cmds.xform(node, query=True, worldSpace=True, scale=True)
            if not translation == [0.0, 0.0, 0.0] or not rotation == [0.0, 0.0, 0.0] or not scale == [1.0, 1.0, 1.0]:
                unfrozen_transforms.append(node)

        assert not unfrozen_transforms, 'Unfrozen transforms found in following geometry nodes: {}'.format(
            unfrozen_transforms)

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
