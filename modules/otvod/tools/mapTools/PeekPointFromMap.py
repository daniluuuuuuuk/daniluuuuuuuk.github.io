from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker, QgsMapTool
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QColor
from qgis.core import QgsProject
from ...tools import GeoOperations


class PeekPointFromMap(QgsMapToolEmitPoint, QObject):

    signal = pyqtSignal(object)

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.snapUtils = self.canvas.snappingUtils()
        self.prj = QgsProject.instance()
        self.snapConfig = self.prj.snappingConfig()
        self.snapUtils.setConfig(self.snapConfig)
        self.aimMarker = []
        self.vertexPoint = []
        self.reset()

    def canvasMoveEvent(self, event):
        if self.aimMarker:
            for marker in self.aimMarker:
                self.canvas.scene().removeItem(marker)
            self.aimMarker.clear()
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.showAimPoint(point)

    def showAimPoint(self, point):
        matchres = self.snapUtils.snapToMap(point)  # QgsPointLocator.Match
        if matchres.isValid():
            m = QgsVertexMarker(self.canvas)
            m.setColor(QColor(255, 0, 255))
            m.setIconSize(7)
            # or ICON_CROSS, ICON_X, ICON_BOX
            m.setIconType(QgsVertexMarker.ICON_BOX)
            m.setPenWidth(2)
            m.setCenter(matchres.point())
            self.aimMarker.append(m)

    def reset(self):
        try:
            self.point = None
            for marker in self.vertexPoint:
                self.canvas.scene().removeItem(marker)
                self.vertexPoint.clear()
            for marker in self.aimMarker:
                self.canvas.scene().removeItem(marker)
                self.aimMarker.clear()
        except:
            pass

    def canvasReleaseEvent(self, e):
        if not self.point:
            self.point = self.toMapCoordinates(e.pos())
            self.showPoint(self.point)
        else:
            self.reset()
            self.point = self.toMapCoordinates(e.pos())
            self.showPoint(self.point)
        self.reset()

    def showPoint(self, point):
        matchres = self.snapUtils.snapToMap(point)  # QgsPointLocator.Match
        if matchres.isValid():
            m = QgsVertexMarker(self.canvas)
            m.setColor(QColor(0, 255, 0))
            m.setIconSize(7)
            # or ICON_CROSS, ICON_X, ICON_BOX
            m.setIconType(QgsVertexMarker.ICON_X)
            m.setPenWidth(2)
            m.setCenter(matchres.point())
            self.vertexPoint.append(m)
            self.signal.emit(matchres.point())
        else:
            print("Не удалось сделать привязку к точке")

    def deactivate(self):
        self.reset()
        QgsMapTool.deactivate(self)
