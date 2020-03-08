#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains custom tool definition for Pyblish based publishers
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging

import pyblish.api

import tpDcc as tp
from tpDcc.libs.qt.core import base

import artellapipe.register

LOGGER = logging.getLogger()


class ArtellaPyblishPublisher(base.BaseWidget, object):
    def __init__(self, project, templates, plugins, parent=None):
        self._project = project
        self._template = templates
        self._plugins = plugins
        self._registered_plugins = list()

        super(ArtellaPyblishPublisher, self).__init__(parent=parent)

        self._setup_host()

    def clean_publisher(self):
        self._deregister_plugins()

    def set_pyblish_window(self, pyblish_window):
        """
        Sets the Pyblish window wrapped by this window
        :param pyblish_window:
        """

        if not pyblish_window:
            return

        pyblish_window.reset()
        pyblish_window.setParent(self)
        self.main_layout.addWidget(pyblish_window)
        self._register_plugins()

    def register_plugin(self, plugin_class):
        """
        Registers given plugin path
        :param plugin_path: str
        """

        if not plugin_class or plugin_class in self._registered_plugins:
            return
        LOGGER.info('Registering Pyblish Plugin: {}'.format(plugin_class))
        pyblish.api.register_plugin(plugin_class)
        self._registered_plugins.append(plugin_class)

    def _setup_host(self):
        """
        Internal function that sets the host of the tool
        :return:
        """

        # TODO: Should we do this in a central place (not per tool)?

        if tp.is_maya():
            pyblish.api.register_host('maya')
        elif tp.is_houdini():
            pyblish.api.register_host('houdini')

    def _register_plugins(self):
        """
        Internal function that registers current available plugins in project
        """

        if not self._plugins:
            LOGGER.warning('No Pyblish Plugins defined to load')
            return

        for plugin_name in self._plugins:
            plguin_class = artellapipe.PyblishMgr().get_plugin(plugin_name)
            self.register_plugin(plguin_class)

    def _deregister_plugins(self):
        """
        Internal function that deregister current registered plugin paths
        """

        pyblish.api.deregister_all_plugins()
        self._registered_plugins = list()


artellapipe.register.register_class('PyblishPublisher', ArtellaPyblishPublisher)
