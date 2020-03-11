#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains ngons validation implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDcc as tp

import pyblish.api


class SelectNgons(pyblish.api.Action):
    label = 'Select Ngons'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Select Ngons Action is only available in Maya!')
            return False

        for instance in context:
            if not instance.data['publish']:
                continue

            node = instance.data.get('node', None)
            assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

            ngons = instance.data.get('ngons', None)
            if not ngons:
                continue

            tp.Dcc.select_object(ngons, replace_selection=False)


class ValidateNGons(pyblish.api.InstancePlugin):
    """
    Checks if there are geometry with ngons
    """

    label = 'Topology - NGons'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False
    actions = [SelectNgons]

    def process(self, instance):

        import maya.api.OpenMaya as OpenMaya

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        meshes_selection_list = OpenMaya.MSelectionList()
        for node in nodes_to_check:
            meshes_selection_list.add(node)

        ngons_found = list()
        sel_it = OpenMaya.MItSelectionList(meshes_selection_list)
        while not sel_it.isDone():
            face_it = OpenMaya.MItMeshPolygon(sel_it.getDagPath())
            object_name = sel_it.getDagPath().getPath()
            while not face_it.isDone():
                num_of_edges = face_it.getEdges()
                if len(num_of_edges) > 4:
                    face_index = face_it.index()
                    component_name = '{}.f[{}]'.format(object_name, face_index)
                    ngons_found.append(component_name)
                face_it.next(None)
            sel_it.next()

        instance.data['ngons'] = ngons_found

        assert not ngons_found, 'NGons in the following components: {}'.format(ngons_found)

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
