#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains student license check validator
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import tpDcc as tp

import pyblish.api


class ValidateStudentLicense(pyblish.api.ContextPlugin):
    """
    Checks if current scene has student license or not
    """

    label = 'Check Student License'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    optional = False

    def process(self, context):

        context.data["comment"] = ""

        from tpDcc.dccs.maya.core import helpers

        file_path = context.data.get('path', None)
        if not file_path:
            file_path = tp.Dcc.scene_name()
        assert file_path and os.path.isfile(file_path), 'File Path "{}" does not exist!'.format(file_path)

        has_student_license = helpers.file_has_student_line(file_path)
        assert not has_student_license, 'File "{}" has student license!'.format(file_path)
