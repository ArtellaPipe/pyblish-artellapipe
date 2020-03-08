import os
import pyblish.api

import artellapipe


class CollectShots(pyblish.api.ContextPlugin):

    label = 'Collect Shots'
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

        shots = cmds.ls(type='shot')

        for shot in shots:
            shot_node = artellapipe.ShotsMgr().find_shot(shot)
            if not shot_node:
                continue

            instance = context.create_instance(shot, project=project)
            instance.data['shot'] = shot_node
            instance.data['family'] = 'shots'
