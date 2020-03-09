#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains empty groups validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import tpDcc as tp

import pyblish.api


class SelectEmptyGroups(pyblish.api.Action):
    label = 'Select Empty Groups'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Select Empty Groups Action is only available in Maya!')
            return False

        for instance in context:
            if not instance.data['publish']:
                continue

        node = instance.data.get('node', None)
        assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        empty_groups = instance.data.get('empty_groups', None)
        assert empty_groups, 'No empty groups found in instance: {}'.format(instance)

        tp.Dcc.select_object(empty_groups, replace_selection=False)


class DeleteEmptyGroups(pyblish.api.Action):
    label = 'Delete Empty Groups'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Delete Empty Groups Action is only available in Maya!')
            return False

        for instance in context:
            if not instance.data['publish']:
                continue

        node = instance.data.get('node', None)
        assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        empty_groups = instance.data.get('empty_groups', None)
        assert empty_groups, 'No empty groups found in instance: {}'.format(instance)

        tp.Dcc.delete_object(empty_groups)


class ValidateEmptyGroups(pyblish.api.InstancePlugin):
    """
    Checks any empty group that has no children
    """

    label = 'General - Empty Groups'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False
    actions = [SelectEmptyGroups, DeleteEmptyGroups]

    def process(self, instance):

        import maya.cmds as cmds

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        empty_groups = list()
        for node in nodes_to_check:
            children = cmds.listRelatives(node, ad=True, fullPath=True)
            if not children:
                empty_groups.append(node)

        if empty_groups:
            instance.data['empty_groups'] = empty_groups

        assert not empty_groups, 'Following empty group has no children: {}'.format(empty_groups)

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
