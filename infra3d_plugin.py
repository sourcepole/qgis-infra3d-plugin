# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Infra3d
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
from threading import Thread
from typing import Callable
import os.path
import sys

# Add prepackaged dependencies to PYTHONPATH so the plugin can use them
sys.path.append(os.path.join(os.path.dirname(__file__), "dependencies/site-packages"))

from qgis.gui import QgisInterface
from qgis.core import Qgis, QgsPointXY, QgsRectangle, QgsDataSourceUri, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QEventLoop, QSettings, QTranslator, QCoreApplication, QUrl, Qt
from qgis.PyQt.QtGui import QIcon, QDesktopServices, QGuiApplication
from qgis.PyQt.QtWidgets import QAction

from .infra3d_settings import Infra3DSettings, DEFAULT_SERVER_PORT, DEFAULT_PG_SERVER_PORT
from .infra3d_client import Infra3dClient
from .infra3d_map_tool import Infra3dMapTool
from .server.socketio_server import SocketIOServer
from .marker_map_item import MarkerMapItem

from .resources import *


class Infra3d:
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value("locale/userLocale", "en")[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            "i18n",
            "Infra3d_{}.qm".format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.toolbar = self.iface.addToolBar("Infra3d")
        self.toolbar.setObjectName("Infra3d")
        self.settings = QSettings()
        self.settings_dialog = Infra3DSettings(self.iface.mainWindow())

        # Start socketio server
        self.socketio_server = SocketIOServer()
        self.start_socketio_server(self.settings.value("/infra3d_viewer/server_port",  DEFAULT_SERVER_PORT))

        # Initialize Infra3D client
        self.infra3d_client = Infra3dClient(self.socketio_server_address())

        # Initialize marker object that will be used to show the tracked position
        self.infra3d_marker = MarkerMapItem(self.iface.mapCanvas())
        self.infra3d_marker.hide()

        # Initialize map tool
        self.infra3d_map_tool = Infra3dMapTool(
            self.iface,
            self.infra3d_client,
            self.infra3d_marker,
            self.start_infra3d_blocking
        )

    # noinspection PyMethodMayBeStatic
    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("Infra3d", message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # Ownership of a QAction is not transfered to QMenu, so we need to keep
        # the references of the actions alive. The easiest way is with an actions list.
        set_infra3d_position_action = QAction( QIcon(":/plugins/infra3d_viewer/infra3d_marker.png"), self.tr("Set infra3DRoad position"), self.iface.mainWindow())

        set_infra3d_position_action.triggered.connect(self.set_infra3d_position)
        set_infra3d_position_action.setCheckable(True)
        self.infra3d_map_tool.setAction(set_infra3d_position_action)
        self.actions.append(set_infra3d_position_action)

        zoom_to_marker = QAction(QIcon(":/plugins/infra3d_viewer/infra3d_zoom.png"), self.tr("Zoom to marker"), self.iface.mainWindow())
        zoom_to_marker.triggered.connect(self.zoom_to_marker)
        self.actions.append(zoom_to_marker)

        self.start_infra3d_action = QAction(QIcon(":/plugins/infra3d_viewer/infra3d.png"), self.tr("Enable infra3DRoad"))
        self.start_infra3d_action.toggled.connect(self.start_infra3d)
        self.start_infra3d_action.setCheckable(True)
        self.actions.append(self.start_infra3d_action)

        self.infra3d_settings = Infra3DSettings(self.iface.mainWindow())
        self.show_settings_action = QAction(QIcon(":/images/themes/default/mActionOptions.svg"), self.tr("Settings"))
        self.show_settings_action.triggered.connect(self.infra3d_settings.show)
        self.show_settings_action.setCheckable(False)
        self.actions.append(self.show_settings_action)

        for action in self.actions:
            self.toolbar.addAction(action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr("infra3DRoad"),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def start_infra3d(self, checked: bool):
        if checked:
            self.open_browser_and_connect(
                lambda: (
                    QGuiApplication.restoreOverrideCursor(),
                    self.infra3d_client.setOnPositionChanged()
                )
            )
            # Listen on tracking signal
            self.infra3d_client.position_changed.connect(
                lambda response: self.place_marker(
                    QgsPointXY(response["easting"], response["northing"]),
                    response["orientation"]
                )
            )
        else:
            self.iface.mapCanvas().unsetMapTool(self.infra3d_map_tool)
            self.infra3d_client.unsetOnPositionChanged()
            try:
                self.infra3d_client.position_changed.disconnect()
            except TypeError:
                # When the signal is not connected and we call disconnect()
                # then we get
                # TypeError: disconnect() failed between 'position_changed' and all its connections
                # That's why we just ignore it
                pass
            self.infra3d_marker.hide()

    def start_infra3d_blocking(self):
        if not self.start_infra3d_action.isChecked():
            # Wait until started
            QGuiApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            blockingWait = QEventLoop()
            self.infra3d_client.webapp_initialized.connect(blockingWait.quit)
            self.infra3d_client.connection_failed.connect(blockingWait.quit)
            self.start_infra3d_action.toggle()
            blockingWait.exec_()
            QGuiApplication.restoreOverrideCursor()

    def set_infra3d_position(self, checked: bool):
        if checked:
            if bool(self.settings.value("/infra3d_viewer/load_pg_layer", False)) is True:
                self.add_infra3d_layers()
            self.iface.mapCanvas().setMapTool(self.infra3d_map_tool)
        else:
            self.iface.mapCanvas().unsetMapTool(self.infra3d_map_tool)

    def check_settings(self) -> bool:
        """Check whether the settings are configured propertly.

        Returns:
            bool: Return True if the settings are defined,
            otherwise returns False
        """

        missing_configurations = []
        if not self.settings.value("/infra3d_viewer/infra3d_username"):
            missing_configurations.append("Infra3d username")
        if not self.settings.value("/infra3d_viewer/infra3d_password"):
            missing_configurations.append("Infra3d password")

        if bool(self.settings.value("/infra3d_viewer/load_pg_layer", False)) is True:
            if not self.settings.value("/infra3d_viewer/database/host"):
                missing_configurations.append("DB host")
            if not self.settings.value("/infra3d_viewer/database/database"):
                missing_configurations.append("DB name")
            if not self.settings.value("/infra3d_viewer/database/tablename"):
                missing_configurations.append("Table name")
            if not self.settings.value("/infra3d_viewer/database/schema"):
                missing_configurations.append("Schema name")
            if not self.settings.value("/infra3d_viewer/database/geometry_column"):
                missing_configurations.append("Geometry column")
        print(missing_configurations)
        if len(missing_configurations) > 0:
            self.iface.messageBar().pushMessage(
                "infra3DRoad",
                self.tr(
                    "The following settings are not set: " + ", ".join(missing_configurations)
                ),
                Qgis.MessageLevel.Critical,  # type: ignore
                5
            )
            return False

        return True

    def open_browser_and_connect(self, callback_after_init: Callable):
        """Start / open a browser / browser tab and initialize the
        Infra3D application via the `init` function.
        See: https://www.infra3d.ch/latest/api/apidoc/Reference/

        Args:
            callback_after_init (Callable): Callback that should be executed
            after the Infra3D application has been initialized. See
            `Infra3dClient.webapp_initialized` for more information about the
            initialization phase.
        """

        # Don't do anything if the socketio server is not running
        if self.socketio_server.running is False:
            QGuiApplication.restoreOverrideCursor()
            self.iface.messageBar().pushMessage(
                "infra3DRoad",
                self.tr("infra3DRoad server did not start correctly. Please restart QGIS"),
                Qgis.MessageLevel.Critical,  # type: ignore
                5
            )
            return

        # Check if settings are set correctly
        if self.check_settings() is False:
            QGuiApplication.restoreOverrideCursor()
            self.start_infra3d_action.setChecked(False)
            return

        # If we cannot connect to the server, then there is
        # no need to start the browser
        if not self.infra3d_client.connect():
            QGuiApplication.restoreOverrideCursor()
            return

        # Start browser
        QDesktopServices.openUrl(
            QUrl(
                self.socketio_server_address()
            )
        )

        # The web app needs to be loaded in the browser before we can
        # initialize the Infra3D application. The `webapp_loaded`
        # signal is emitted when a browser has been launched and
        # our JS code (code under server/static/js) was execeted.
        self.infra3d_client.webapp_loaded.connect(
            lambda: self.infra3d_client.init(
                self.settings.value("/infra3d_viewer/infra3d_username"),
                self.settings.value("/infra3d_viewer/infra3d_password")
            )
        )
        # All Infra3D functions can only be called after the Infra3D application
        # has been loaded(see `Infra3D.webapp_loaded` signal) and initialized.
        # The `webapp_initialized` signal is emitted when this is the case.
        # Only now can we call Infra3D functions or listen to Infra3D events.
        self.infra3d_client.webapp_initialized.connect(callback_after_init)

    def place_marker(self, point: QgsPointXY, orientation: float):
        """Place the marker `self.infra3d_marker` on the map canvas and
        set the orientation.

        Args:
            point (QgsPointXY): QgsPointXY object to use when placing the marker
            orientation (float): Marker orientation
        """
        if self.infra3d_marker.isVisible() is False:
            self.infra3d_marker.show()

        self.infra3d_marker.setRotation(int(orientation))
        self.infra3d_marker.setMapPosition(point)

    def zoom_to_marker(self):
        """Zoom to the current position of the marker on the map
        and refresh the map canvas
        """
        if not self.infra3d_marker.isVisible():
            return

        self.iface.mapCanvas().setExtent(
            QgsRectangle(
                self.infra3d_marker.current_position,
                self.infra3d_marker.current_position
            )
        )
        self.iface.mapCanvas().refresh()

    def start_socketio_server(self, port: int):
        """Start the socketio server in a different thread
        so we don't block the QGIS application.

        Args:
            port (int): Port on which the server should bind itself to
        """
        def start_server():
            self.socketio_server.start(port)

        thread = Thread(target=start_server)
        thread.start()

    def socketio_server_address(self) -> str:
        """Build the socketio server address

        Returns:
            str: Server address
        """
        return f"http://127.0.0.1:{self.settings.value('/infra3d_viewer/server_port', DEFAULT_SERVER_PORT)}"

    def add_infra3d_layers(self):
        """Add infra3d layers
        """
        uri = QgsDataSourceUri()

        uri.setConnection(
            self.settings.value("/infra3d_viewer/database/host"),
            str(self.settings.value("/infra3d_viewer/database/port", DEFAULT_PG_SERVER_PORT)),
            self.settings.value("/infra3d_viewer/database/database"),
            self.settings.value("/infra3d_viewer/database/username", ""),
            self.settings.value("/infra3d_viewer/database/password", "")
        )

        # Add Infra3D layer
        if len(QgsProject.instance().mapLayersByName("infra3DRoad")) == 0:
            uri.setDataSource(
                self.settings.value("/infra3d_viewer/database/schema"),
                self.settings.value("/infra3d_viewer/database/tablename"),
                self.settings.value("/infra3d_viewer/database/geometry_column")
            )

            layer = QgsVectorLayer(uri.uri(), "infra3DRoad", "postgres")
            if not layer.isValid():
                self.iface.messageBar().pushMessage(
                    "infra3DRoad",
                    self.tr(
                        "Could not load Infra3dRoad layer"
                    ),
                    Qgis.MessageLevel.Warning,  # type: ignore
                    5
                )
            else:
                qmlFile = os.path.join(os.path.split(__file__)[0], 'infra3DRoad.qml')
                layer.loadNamedStyle( qmlFile, False )
                QgsProject.instance().addMapLayer(layer)
