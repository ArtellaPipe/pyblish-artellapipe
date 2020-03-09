#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains display layers check validator
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import pyblish.api

import tpDcc as tp


class RemoveDisplayLayers(pyblish.api.Action):
    label = 'Remove Display Layers'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Remove From Display Layer Action is only available in Maya!')
            return False

        import tpDcc.dccs.maya as maya

        maya.cmds.undoInfo(openChunk=True)

        try:
            display_layers = maya.cmds.ls(type='displayLayer')
            for display_layer in display_layers:
                if display_layer == 'defaultLayer':
                    continue
                maya.cmds.delete(display_layer)
        except Exception as exc:
            self.log.error('Error while removing display layers: {}'.format(exc))
        finally:
            maya.cmds.undoInfo(closeChunk=False)

        return True


class ValidateDisplayLayers(pyblish.api.ContextPlugin):
    """
    Checks if current scene has display layers
    """

    label = 'Scene - Display Layers in Scene'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False
    actions = [RemoveDisplayLayers]

    def process(self, context):

        import maya.cmds as cmds

        layers = cmds.ls(type='displayLayer')
        assert len(layers) == 1, 'Display layers found in current scene: "{}"'.format(layers)
