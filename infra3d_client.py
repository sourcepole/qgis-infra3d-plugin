# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Infra3dClient
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
# -*- coding: utf-8 -*-

import uuid
import socketio
from typing import Callable
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QMessageBox


class Infra3dClient(QObject):
    """This is a convenience class that should ease the access
    to the infra3D application, that is running in the browser.
    """

    # This pyqtSignal is used to signal that
    # the Infra3D web app was loaded
    webapp_loaded = pyqtSignal(dict)
    # This pyqtSignal is used to signal that
    # the Infra3D web app was initialized by calling
    # the function "initInfra3d" (see Infra3dClient.init)
    webapp_initialized = pyqtSignal(dict)
    # This pyqtSignal is used to signal that
    # the position in the Infra3D web app changed
    position_changed = pyqtSignal(dict)
    connection_failed = pyqtSignal(dict)

    def __init__(self, socketio_server_url):
        super(Infra3dClient, self).__init__()
        self.socketio_server_url = socketio_server_url
        self.sio = socketio.Client()

    def connect(self) -> bool:
        """Try to connect to the socketio server and return
        whether the connection was successfull or not.

        Returns:
            bool: True, if the connection could be made.
        """
        if self.sio.connected is True:
            return True

        try:
            self.sio.connect(self.socketio_server_url)
        except socketio.exceptions.ConnectionError as e:
            QMessageBox.critical(
                None,  # type: ignore
                self.tr("infra3DRoad: Connection error"),
                self.tr("Could not connect to the socketio server!")
            )
            self.connection_failed.emit
            return False
        self.__listen_on_remote_event("loaded", self.webapp_loaded.emit)
        return True

    def init(self, username: str, password: str):
        """Call the JS method `initInfra3d` to start the initialization
        of Infra3D application in the browser.
        """
        self.__call_remote_method(
            "initInfra3d",
            {
                "url": "https://www.infra3d.ch/latest",
                "lang": "de",
                "map": False,
                "layer": "true",
                "navigation": True,
                "buttons": True,
                "username": username,
                "password": password
            }
        )
        self.__listen_on_remote_event("initialized", self.webapp_initialized.emit)

    def setOnPositionChanged(self):
        """Listen on the remote event `positionChanged` that is emitted
        whenever the Infra3D application in the browser changes the camera position.
        Everytime the event is emitted, the QT signal positionChanged is emitted too.

        """
        self.__call_remote_method("setOnPositionChanged", {})
        self.__listen_on_remote_event("positionChanged", self.position_changed.emit)

    def unsetOnPositionChanged(self):
        """Stop listening on remote event `positionChanged`
        """
        self.__call_remote_method("unsetOnPositionChanged", {})

    def lookAt2DPosition(self, easting: float, northing: float):
        """Set the current position in the Infra3d application in the browser.

        Args:
            easting (float): Coordinate E
            northing (float): Coordinate N
        """
        self.__call_remote_method("lookAt2DPosition", {"easting": easting, "northing": northing})

    def __call_remote_method(self, method_name: str, args: dict):
        """Helper method to call a remote method.
        A remote method is a JS method that can be called via the socketio server.
        To be able to call the JS method, the method has to be registered in the JS application
        (applications.js in this case).

        Args:
            method_name (str): JS method name that to call
            args (dict): Method arguments to pass
        """
        self.connect()
        request = {
            "id": str(uuid.uuid1()),
            "method": method_name,
            "args": args
        }

        try:
            self.sio.emit("rpcrequest", data=request)
        except socketio.exceptions.BadNamespaceError:
            # This exception only occurs when we are not connected to the server
            # We ignore it here, because we already notify the user that a
            # connection to the server could not be made
            pass

    def __listen_on_remote_event(self, event_name: str, handler: Callable):
        """Helper method to listen on a remote event.
        Events are handled with the publish-subscribe messaging pattern.
        This function simply listens on specific events (`event_name`)
        and calls their specified callback (`handler`).

        Args:
            event_name (str): Event name to listen to
            handler (Callable): Callback to execute when the event was emitted
        """
        self.connect()
        self.sio.on(event_name, handler=handler)

    def disconnect(self):
        """Disconnect from the socketio server
        """
        self.sio.disconnect()
