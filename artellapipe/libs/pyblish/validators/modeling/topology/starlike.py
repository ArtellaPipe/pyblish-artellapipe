#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains polygon star-like validation implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDcc as tp

import pyblish.api


class SelectStarLikePolygons(pyblish.api.Action):
    label = 'Select Star-Like Polygons'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Select Star-Like Polygons Action is only available in Maya!')
            return False

        for instance in context:
            if not instance.data['publish'] or not instance.data['_has_failed']:
                continue

            node = instance.data.get('node', None)
            assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

            star_like_polygons = instance.data.get('star_like_polygons', None)
            assert star_like_polygons, 'No star-like polygons geometry found in instance: {}'.format(instance)

            tp.Dcc.select_object(star_like_polygons, replace_selection=False)


class ValidateStarLike(pyblish.api.InstancePlugin):
    """
    Checks if there are polygons with start-like topology
    """

    label = 'Topology - Star-Like Polygons'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False
    actions = [SelectStarLikePolygons]

    def process(self, instance):

        import maya.api.OpenMaya as OpenMaya

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        meshes_selection_list = OpenMaya.MSelectionList()
        for node in nodes_to_check:
            meshes_selection_list.add(node)

        starlike_found = list()
        sel_it = OpenMaya.MItSelectionList(meshes_selection_list)
        while not sel_it.isDone():
            poly_it = OpenMaya.MItMeshPolygon(sel_it.getDagPath())
            object_name = sel_it.getDagPath().getPath()
            while not poly_it.isDone():
                if poly_it.isStarlike() is False:
                    poly_index = poly_it.index()
                    component_name = '{}.f[{}]'.format(object_name, poly_index)
                    starlike_found.append(component_name)
                poly_it.next(None)
            sel_it.next()

        if starlike_found:
            instance.data['star_like_polygons'] = starlike_found

        assert not starlike_found, 'Star-Like polys found in the following components: {}'.format(starlike_found)

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
