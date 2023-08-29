# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Infra3d
                                 A QGIS plugin
 This plugin is an integration of the Infra3D application with QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-09-28
        copyright            : (C) 2022 by Sourcepole AG
        email                : hka@sourcepole.ch
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Infra3d class from file Infra3d.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .infra3d_plugin import Infra3d
    return Infra3d(iface)