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


class ValidateDisplayLayers(pyblish.api.ContextPlugin):
    """
    Checks if current scene has display layers
    """

    label = 'Display Layers in Scene'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False

    def process(self, context):

        import maya.cmds as cmds

        layers = cmds.ls(type='displayLayer')
        assert len(layers) == 1, 'Display layers found in current scene: "{}"'.format(layers)
