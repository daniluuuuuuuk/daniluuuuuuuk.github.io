from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker, QgsMapTool
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QColor
from qgis.core import QgsProject
from ...tools import GeoOperations
from decimal import *


class AzimuthMapTool(QgsMapToolEmitPoint, QObject):

    signal = pyqtSignal(object)

    def __init__(self, canvas, inclination):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.snapUtils = self.canvas.snappingUtils()
        self.prj = QgsProject.instance()
        self.snapConfig = self.prj.snappingConfig()
        self.snapUtils.setConfig(self.snapConfig)

        self.aimMarker = []
        self.vertexMarkers = []
        self.pointList = []
        self.inclination = inclination
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

    def canvasPressEvent(self, e):
        if not self.firstPoint:
            self.firstPoint = self.toMapCoordinates(e.pos())
            self.showPoint(self.firstPoint)
        elif self.firstPoint and not self.secondPoint:
            self.secondPoint = self.toMapCoordinates(e.pos())
            self.showPoint(self.secondPoint)
            az = GeoOperations.calculateAzimuth(
                # self.pointList[0], self.pointList[1]) + Decimal(self.inclination)
                self.pointList[0], self.pointList[1])             
            dist = GeoOperations.calculateDistance(
                self.pointList[0], self.pointList[1])
            self.signal.emit([az, dist])
        elif self.firstPoint and self.secondPoint:
            self.reset()
            self.firstPoint = self.toMapCoordinates(e.pos())
            self.showPoint(self.firstPoint)

    def deletePointsFromCanvas(self):
        try:
            self.pointList.clear()
            for marker in self.vertexMarkers:
                self.canvas.scene().removeItem(marker)
            if self.aimMarker:
                for marker in self.aimMarker:
                    self.canvas.scene().removeItem(marker)
                self.aimMarker.clear()
        except:
            pass

    def showPoint(self, point):
        matchres = self.snapUtils.snapToMap(point)  # QgsPointLocator.Match
        if matchres.isValid():
            # print("valid")
            m = QgsVertexMarker(self.canvas)
            m.setColor(QColor(0, 255, 0))
            m.setIconSize(7)
            # or ICON_CROSS, ICON_X, ICON_BOX
            m.setIconType(QgsVertexMarker.ICON_X)
            m.setPenWidth(2)
            m.setCenter(matchres.point())
            self.vertexMarkers.append(m)
            self.pointList.append(matchres.point())
        else:
            print("MapTool не смог сделать snapping")

    def reset(self):
        self.firstPoint = self.secondPoint = None
        self.waitForSecondPoint = False
        self.deletePointsFromCanvas()

    def deactivate(self):
        self.deletePointsFromCanvas()
        QgsMapTool.deactivate(self)
