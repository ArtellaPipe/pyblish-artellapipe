#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains geometry shaders validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import tpDcc as tp

import pyblish.api


class ApplyDefaultShader(pyblish.api.Action):
    label = 'Apply Default Shader'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Select Vertex Poles Action is only available in Maya!')
            return False

        import tpDcc.dccs.maya as maya

        for instance in context:
            if not instance.data['publish']:
                continue

            node = instance.data.get('node', None)
            assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

            apply_default_shader = instance.data.get('apply_default_shader', False)
            if not apply_default_shader:
                continue

            maya.cmds.undoInfo(openChunk=True)

            try:
                node_shapes = maya.cmds.listRelatives(node, shapes=True, fullPath=True)
                maya.cmds.sets(node_shapes, edit=True, forceElement='initialShadingGroup')
            except Exception as exc:
                self.log.error('Error while applying default shader on shapes: {} | {}'.format(node_shapes, exc))
            finally:
                maya.cmds.undoInfo(openChunk=False)

        return True


class ValidateGeometryShaders(pyblish.api.InstancePlugin):
    """
    Checks if current scene has geometries with shaders applied
    """

    label = 'Geometry - Shaders'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False
    actions = [ApplyDefaultShader]

    def process(self, instance):

        import tpDcc.dccs.maya as maya

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        nodes_with_shaders = list()
        shaders = dict()
        for check_node in nodes_to_check:
            shading_groups = None
            shape = maya.cmds.listRelatives(check_node, shapes=True, fullPath=True)
            if maya.cmds.nodeType(shape) == 'mesh':
                if shape:
                    shading_groups = maya.cmds.listConnections(shape, type='shadingEngine')
                shading_group_to_check = shading_groups[0]
                if not shading_group_to_check == 'initialShadingGroup':
                    if shading_group_to_check not in shaders:
                        shaders[shading_group_to_check] = list()
                    shaders[shading_group_to_check].append(check_node)
                    if check_node not in nodes_with_shaders:
                        nodes_with_shaders.append(check_node)

        if node in nodes_with_shaders:
            instance.data['apply_default_shader'] = True

        assert not shaders, 'Geometries with applied shaders found: {}'.format(shaders)

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
