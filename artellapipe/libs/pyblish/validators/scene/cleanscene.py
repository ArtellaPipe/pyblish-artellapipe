#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains clean scene validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import pyblish.api

import tpDcc as tp


class CleanUnknownNodes(pyblish.api.Action):
    label = 'Clean Unknown Nodes'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Clean Unknown Nodes Action is only available in Maya!')

        from tpDcc.dccs.maya.core import scene

        scene.delete_unknown_nodes()

        return True


class CleanUnusedPlugins(pyblish.api.Action):
    label = 'Clean Plugin Nodes'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Clean Unused Plugins Action is only available in Maya!')

        from tpDcc.dccs.maya.core import scene

        scene.delete_unused_plugins()

        return True


class CleanTurtleNodes(pyblish.api.Action):
    label = 'Clean Turtle Nodes'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Clean Turtle Nodes Action is only available in Maya!')

        from tpDcc.dccs.maya.core import scene

        scene.delete_turtle_nodes()

        return True


class CleanGarbageNodes(pyblish.api.Action):
    label = 'Clean Garbage Nodes'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Clean Garbage Nodes Action is only available in Maya!')

        from tpDcc.dccs.maya.core import scene

        scene.delete_garbage()

        return True


class ValidateCleanUnknownNodes(pyblish.api.ContextPlugin):
    """
    Checks if current scene has unknown nodes
    """

    label = 'Scene - Unknown Nodes'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False
    actions = [CleanUnknownNodes]

    def process(self, context):
        import tpDcc.dccs.maya as maya

        unknown = maya.cmds.ls(type='unknown')

        assert not unknown, 'Unknown nodes found in current scene: {}'.format(unknown)


class ValidateCleanUnusedPlugins(pyblish.api.ContextPlugin):
    """
    Checks if current scene has unused plugins nodes
    """

    label = 'Scene - Unused Plugins'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False
    actions = [CleanUnusedPlugins]

    def process(self, context):

        import tpDcc.dccs.maya as maya

        # This functionality is not available in old Maya versions
        list_cmds = dir(maya.cmds)
        if 'unknownPlugin' not in list_cmds:
            return

        unknown_plugins = maya.cmds.unknownPlugin(query=True, list=True)

        assert not unknown_plugins, 'Unknown Plugins found in current scene: {}'.format(unknown_plugins)


class ValidateCleanTurtleNodes(pyblish.api.ContextPlugin):
    """
    Checks if current scene has turtle nodes
    """

    label = 'Scene - Turtle Nodes'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False
    actions = [CleanTurtleNodes]

    def process(self, context):

        import tpDcc.dccs.maya as maya

        turtle_nodes = list()
        plugin_list = maya.cmds.pluginInfo(query=True, pluginsInUse=True)
        for plugin in plugin_list:
            if plugin[0] == 'Turtle':
                turtle_types = ['ilrBakeLayer',
                                'ilrBakeLayerManager',
                                'ilrOptionsNode',
                                'ilrUIOptionsNode']
                turtle_nodes = maya.cmds.ls(type=turtle_types)
                break

        assert not turtle_nodes, 'Turtle Nodes found in current scene: {}'.format(turtle_nodes)


class ValidateCleanGarbageNodes(pyblish.api.ContextPlugin):
    """
    Checks if current scene has garbage nodes ('hyperLayout', 'hyperView, empty partitions, empty objectSets, etc)
    """

    label = 'Scene - Clean Garbage'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False
    actions = [CleanGarbageNodes]

    def process(self, context):

        import tpDcc.dccs.maya as maya
        from tpDcc.dccs.maya.core import helpers, node

        garbage_nodes = list()
        if helpers.get_maya_version() > 2014:
            garbage_nodes = maya.cmds.ls(type=['hyperLayout', 'hyperView'])
            if 'hyperGraphLayout' in garbage_nodes:
                garbage_nodes.remove('hyperGraphLayout')

        check_connection_node_type = ['shadingEngine', 'partition', 'objectSet']
        check_connection_nodes = list()
        for check_type in check_connection_node_type:
            nodes_of_type = maya.cmds.ls(type=check_type)
            check_connection_nodes += nodes_of_type

        nodes_to_skip = ['characterPartition', 'hyperGraphLayout']

        for n in check_connection_nodes:
            if not n or not maya.cmds.objExists(n):
                continue
            if n in nodes_to_skip:
                continue
            if node.is_empty(n):
                garbage_nodes.append(n)

        assert not garbage_nodes, 'Garbage Nodes found in current scene: {}'.format(garbage_nodes)
