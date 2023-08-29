import math

from qgis.gui import QgsMapCanvasItem, QgsMapCanvas
from qgis.core import QgsPointXY, QgsApplication
from qgis.PyQt.QtGui import QPainter, QBrush, QPen, QColor, QPixmap, QPainterPath, QFontMetricsF, QFont
from qgis.PyQt.QtCore import Qt, QRectF, QSizeF
from qgis.PyQt.QtWidgets import QStyleOptionGraphicsItem, QWidget


# Inspired by Marco Hugentobler
class MarkerMapItem(QgsMapCanvasItem):
    def __init__(self, canvas: QgsMapCanvas):
        super().__init__(canvas)
        self.arrowLength = 50
        self.arrow_path = QPainterPath()
        self.rotation = 0
        self.current_position = QgsPointXY()
        self.setSymbol()

    def setMapPosition(self, point: QgsPointXY):
        self.current_position = point
        self.setPos(self.toCanvasCoordinates(self.current_position))

    def setRotation(self, rotation: int):
        diff = rotation - self.rotation
        self.rotation = rotation
        if abs(diff) > 1:
            self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        if painter is None:
            return

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Draw arrow, using a red line over a thicker white line so that the arrow is visible against a range of backgrounds
        painter.save()
        painter.rotate(self.rotation)
        pen = QPen()
        pen.setWidth(self.scaleIconSize(4))
        pen.setColor(QColor(Qt.GlobalColor.white))
        painter.setPen(pen)
        painter.drawPath(self.arrow_path)
        pen.setWidth(self.scaleIconSize(2))
        pen.setColor(QColor(Qt.GlobalColor.red))
        painter.setPen(pen)
        painter.drawPath(self.arrow_path)
        painter.restore()
        
        #draw position maker on top of arrow
        painter.setBrush(QBrush(Qt.blue))
        painter.drawRect(-4, -4, 8, 8)
        painter.restore()

    def setSymbol(self):
        
        l2 = self.arrowLength / 2.0
        l4 = self.arrowLength / 4.0
        
        self.arrow_path.moveTo(0, l2)
        self.arrow_path.lineTo(0, -l2)
        self.arrow_path.moveTo(-l4, -l4)
        self.arrow_path.lineTo(0, -l2)
        self.arrow_path.lineTo(l4, -l4)

    def boundingRect(self) -> QRectF:
        s = self.arrowLength / 2.0 + self.scaleIconSize(4)
        l = self.arrowLength + 2 * self.scaleIconSize(4)
        return QRectF(
            -s, -s, l, l
        )

    def updatePosition(self):
        self.setMapPosition(self.current_position)

    def scaleIconSize(self, standardSize: int) -> int:
        return QgsApplication.scaleIconSize(standardSize)
