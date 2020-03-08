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

        geo_meshes = cmds.ls(type='mesh')
        geo_transforms = [cmds.listRelatives(mesh, parent=True)[0] for mesh in geo_meshes]

        for node in geo_transforms:
            instance = context.create_instance(node, project=project)
            instance.data['node'] = node
            instance.data['family'] = 'geometry'
