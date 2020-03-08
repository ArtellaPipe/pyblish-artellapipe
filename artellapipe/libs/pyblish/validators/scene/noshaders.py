#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains no shaders check validator
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import pyblish.api


class ValidateNoShadersInScene(pyblish.api.ContextPlugin):
    """
    Checks if current scene has shaders (apart from the standard ones)
    """

    label = 'Check Scene Shaders'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False

    def process(self, context):

        import maya.cmds as cmds

        shading_nodes = cmds.ls(type='shadingEngine')
        extra_shaders = list()
        for shading_node in shading_nodes:
            if shading_node not in ['initialParticleSE', 'initialShadingGroup']:
                if shading_node not in extra_shaders:
                    extra_shaders.append(shading_node)

        assert not extra_shaders, 'Current scene has non default shaders: "{}"'.format(extra_shaders)
