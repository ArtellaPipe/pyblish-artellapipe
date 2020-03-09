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

import tpDcc as tp

import pyblish.api


class CleanShaders(pyblish.api.Action):
    label = 'Clean Shaders'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Clean Shaders Action is only available in Maya!')
            return False

        import tpDcc.dccs.maya as maya

        extra_shaders = context.data.get('extra_shaders', None)
        assert extra_shaders, 'No extra shaders found in current context: {}'.format(context)

        shaders_to_delete = list()

        maya.cmds.undoInfo(openChunk=True)

        try:
            for shading_group in extra_shaders:
                shader_shapes = maya.cmds.listConnections(shading_group, type='mesh')
                if shader_shapes:
                    maya.cmds.sets(shader_shapes, edit=True, forceElement='initialShadingGroup')
                shaders_to_delete.append(shading_group)
                shaders_to_delete.extend(maya.cmds.listConnections(shading_group, type='surfaceShader') or list())
            shaders_to_delete = list(set(shaders_to_delete))
            for shader_to_delete in shaders_to_delete:
                if not maya.cmds.objExists(shader_to_delete):
                    continue
                tp.Dcc.delete_object(shader_to_delete)
        except Exception as exc:
            self.log.error('Error while cleaning shaders from scene: {}'.format(exc))
        finally:
            maya.cmds.undoInfo(closeChunk=True)


class SelectShaders(pyblish.api.Action):
    label = 'Select Shaders'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Select Shaders Action is only available in Maya!')
            return False

        import tpDcc.dccs.maya as maya

        extra_shaders = context.data.get('extra_shaders', None)
        assert extra_shaders, 'No extra shaders found in current context: {}'.format(context)

        shaders_to_select = list()
        for shading_group in extra_shaders:
            shaders_to_select.extend(maya.cmds.listConnections(shading_group, type='surfaceShader'))
        shaders_to_select = list(set(shaders_to_select))
        tp.Dcc.select_object(shaders_to_select)


class ValidateNoShadersInScene(pyblish.api.ContextPlugin):
    """
    Checks if current scene has shaders (apart from the standard ones)
    """

    label = 'Shaders - Check Scene Shaders'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False
    actions = [SelectShaders, CleanShaders]

    def process(self, context):

        import maya.cmds as cmds

        shading_nodes = cmds.ls(type='shadingEngine')
        extra_shaders = list()
        for shading_node in shading_nodes:
            if shading_node not in ['initialParticleSE', 'initialShadingGroup']:
                if shading_node not in extra_shaders:
                    extra_shaders.append(shading_node)

        if extra_shaders:
            context.data['extra_shaders'] = extra_shaders

        assert not extra_shaders, 'Current scene has non default shaders: "{}"'.format(extra_shaders)
