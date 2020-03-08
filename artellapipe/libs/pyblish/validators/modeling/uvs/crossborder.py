#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains cross borders UVs validator implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import tpDcc as tp

import pyblish.api


class ValidateCrossBorder(pyblish.api.InstancePlugin):
    """
    Checks if a geometry node has cross borders
    """

    label = 'UVs - Cross Border'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False

    def process(self, instance):

        import maya.api.OpenMaya as OpenMaya

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        meshes_selection_list = OpenMaya.MSelectionList()
        for node in nodes_to_check:
            meshes_selection_list.add(node)

        cross_borders = list()
        sel_it = OpenMaya.MItSelectionList(meshes_selection_list)
        while not sel_it.isDone():
            poly_it = OpenMaya.MItMeshPolygon(sel_it.getDagPath())
            object_name = sel_it.getDagPath().getPath()
            while not poly_it.isDone():
                u = None
                v = None
                uvs = poly_it.getUVs()
                for index, each_uvs in enumerate(uvs):
                    if index == 0:
                        for uv in each_uvs:
                            if u is None:
                                u = int(uv)
                            if u != int(uv):
                                component_name = '{}.f[{}]'.format(object_name, poly_it.index())
                                cross_borders.append(component_name)
                    elif index == 1:
                        for uv in each_uvs:
                            if v is None:
                                v = int(uv)
                            if v != int(uv):
                                component_name = '{}.f[{}]'.format(object_name, poly_it.index())
                                cross_borders.append(component_name)
                poly_it.next(None)
            sel_it.next()

        assert not cross_borders, 'Cross Border found in following geometry nodes: {}'.format(cross_borders)

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
