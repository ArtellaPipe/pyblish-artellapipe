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


class ValidateCleanUnknownNodes(pyblish.api.InstancePlugin):
    """
    Checks if current scene has unknown nodes
    """

    label = 'Scene - Unknown Nodes'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False

    def process(self, instance):

        import maya.cmds as cmds

        unknown = cmds.ls(type='unknown')

        assert not unknown, 'Unknown nodes found in current scene: {}'.format(unknown)


class ValidateCleanUnusedPlugins(pyblish.api.InstancePlugin):
    """
    Checks if current scene has unused plugins nodes
    """

    label = 'Scene - Turtle Nodes'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False

    def process(self, instance):

        import maya.cmds as cmds

        # This functionality is not available in old Maya versions
        list_cmds = dir(cmds)
        if 'unknownPlugin' not in list_cmds:
            return

        unknown_plugins = cmds.unknownPlugin(query=True, list=True)

        assert not unknown_plugins, 'Unknown Plugins found in current scene: {}'.format(unknown_plugins)
