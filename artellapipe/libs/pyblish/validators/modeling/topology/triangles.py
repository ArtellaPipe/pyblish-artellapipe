#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains triangles validation implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDcc as tp

import pyblish.api


class SelectTriangles(pyblish.api.Action):
    label = 'Select Triangles'
    on = 'failed'

    def process(self, context, plugin):
        if not tp.is_maya():
            self.log.warning('Select Triangles Action is only available in Maya!')
            return False

        for instance in context:
            if not instance.data['publish'] or not instance.data['_has_failed']:
                continue

            node = instance.data.get('node', None)
            assert node and tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

            triangles = instance.data.get('triangles', None)
            assert triangles, 'No triangles geometry found in instance: {}'.format(instance)

            tp.Dcc.select_object(triangles, replace_selection=False)


class ValidateTriangles(pyblish.api.InstancePlugin):
    """
    If one of the geometries is tringulated, we must ensure that the rest of the geometry is also triangulated
    """

    label = 'Topology - Triangles'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['geometry']
    optional = False
    actions = [SelectTriangles]

    def process(self, instance):

        import maya.api.OpenMaya as OpenMaya

        node = instance.data.get('node', None)
        assert tp.Dcc.object_exists(node), 'No valid node found in current instance: {}'.format(instance)

        nodes_to_check = self._nodes_to_check(node)
        assert nodes_to_check, 'No Nodes to check found!'

        meshes_selection_list = OpenMaya.MSelectionList()
        for node in nodes_to_check:
            meshes_selection_list.add(node)

        triangles_found = list()
        total_nodes = len(nodes_to_check)
        tringulated_meshes = 0
        sel_it = OpenMaya.MItSelectionList(meshes_selection_list)
        while not sel_it.isDone():
            mesh_triangles = list()
            face_it = OpenMaya.MItMeshPolygon(sel_it.getDagPath())
            object_name = sel_it.getDagPath().getPath()
            while not face_it.isDone():
                num_of_edges = face_it.getEdges()
                if len(num_of_edges) == 3:
                    face_index = face_it.index()
                    component_name = '{}.f[{}]'.format(object_name, face_index)
                    mesh_triangles.append(component_name)
                    triangles_found.append(component_name)
                    tringulated_meshes += 1
                face_it.next(None)
            if mesh_triangles:
                self.log.info('Geometry {} has triangles!'.format(object_name))
            # assert mesh_triangles, 'Mesh with no triangles found: {}'.format(object_name)
            sel_it.next()

        if triangles_found:
            instance.data['triangles'] = triangles_found
            assert tringulated_meshes == total_nodes, 'Not all meshes of {} are triangulated!'.format(instance)

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
