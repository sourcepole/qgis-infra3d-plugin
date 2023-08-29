# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Infra3dMapTool
                                 A QGIS plugin
 This plugin is an integration of the Infra3D application with QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-09-28
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Sourcepole AG
        email                : hka@sourcepole.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.core import QgsProject, QgsSnappingUtils, QgsPointLocator, QgsPointXY, Qgis
from qgis.gui import QgsMapToolEmitPoint, QgisInterface, QgsMapMouseEvent, QgsSnapIndicator
from typing import Callable

from .marker_map_item import MarkerMapItem
from .infra3d_client import Infra3dClient


class Infra3dMapTool(QgsMapToolEmitPoint):

    def __init__(self, iface: QgisInterface, infra3d_client: Infra3dClient, infra3d_marker: MarkerMapItem, callback_start_infra3d: Callable ):
        super(Infra3dMapTool, self).__init__(iface.mapCanvas())
        self.iface = iface
        self.map_canvas = self.iface.mapCanvas()
        self.snapper = QgsSnapIndicator(self.map_canvas)
        self.snapper.setVisible(True)
        self.locator = None

        self.infra3d_client = infra3d_client
        self.canvasClicked.connect(self.set_infra3d_position)
        self.infra3d_marker = infra3d_marker
        self.callback_start_infra3d = callback_start_infra3d

    def initLocator(self):
        layer = QgsProject.instance().mapLayersByName("infra3DRoad")
        if len(layer) > 0:
            self.locator = QgsSnappingUtils(self.map_canvas).locatorForLayer(layer[0])

    def canvasMoveEvent(self, mouseEvent: QgsMapMouseEvent):
        """Custom snapper for Infra3DRoad layer

        Args:
            mouseEvent (QgsMapMouseEvent): Mouse event
        """
        if not self.locator:
            self.initLocator()

        if self.locator:
            self.snapper.setMatch(self.locator.nearestEdge(mouseEvent.mapPoint(), 100))

    def set_infra3d_position(self, point: QgsPointXY):
        """Call the remote function `lookAt2DPosition` and set the position
        in the Infra3D application to the selected point in QGIS.

        """

        self.callback_start_infra3d()

        if self.infra3d_marker.isVisible() is False:
            self.infra3d_marker.show()

        if not self.locator:
            self.infra3d_client.lookAt2DPosition(point.x(), point.y())
            self.infra3d_marker.setMapPosition(point)
        # Get point from snapper
        elif self.snapper.match().isValid():
            point = self.snapper.match().point()
            self.infra3d_client.lookAt2DPosition(point.x(), point.y())
            self.infra3d_marker.setMapPosition(point)
        else:
            self.iface.messageBar().pushMessage(
                "Infra3D",
                self.tr(
                    "No image found for the selected position."
                ),
                Qgis.MessageLevel.Critical,  # type: ignore
                5
            )

        self.snapper.setMatch(QgsPointLocator.Match())