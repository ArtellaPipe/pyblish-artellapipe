import pyblish.api

import artellapipe


class CollectGeometry(pyblish.api.ContextPlugin):

    label = 'Collect Geometry'
    order = pyblish.api.CollectorOrder
    hosts = ['maya']

    def process(self, context):

        import maya.cmds as cmds

        project = None
        for name, value in artellapipe.__dict__.items():
            if name == 'project':
                project = value
                break

        assert project, 'Project not found'

        geo_meshes = cmds.ls(type='mesh', long=True)
        geo_transforms = [cmds.listRelatives(mesh, parent=True, fullPath=True)[0] for mesh in geo_meshes]

        for node in geo_transforms:
            node_name = node.split('|')[-1].split(':')[-1]
            instance = context.create_instance(node_name, project=project)
            instance.data['icon'] = 'cubes'
            instance.data['node'] = node
            instance.data['family'] = 'geometry'
