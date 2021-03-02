from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand, QgsMapTool, QgsVertexMarker, QgsMapCanvasSnappingUtils, QgisInterface
from qgis.core import QgsPointXY, QgsRectangle
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, QObject, QPoint
from qgis.core import QgsWkbTypes, QgsSnappingUtils, QgsPointLocator, QgsTolerance, QgsSnappingConfig, QgsProject, QgsGeometry
from ...tools import GeoOperations
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolTip, QWidget, QApplication
from decimal import *


class BuildFromMapTool(QgsMapToolEmitPoint, QWidget):

    signal = pyqtSignal(object)

    def __init__(self, canvas, inclination):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.snapUtils = self.canvas.snappingUtils()
        self.prj = QgsProject.instance()
        self.snapConfig = self.prj.snappingConfig()
        self.snapUtils.setConfig(self.snapConfig)

        self.inclination = inclination

        self.aimMarker = []
        self.vertexMarkers = []
        self.rubberBand = QgsRubberBand(self.canvas, False)
        self.rubberBand.setColor(QColor(0, 0, 0))

        self.measureLineRubber = QgsRubberBand(self.canvas, False)
        self.measureLineRubber.setColor(QColor(255, 0, 0))
        self.pointList = [[]]
        self.reset()

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if self.pointList:
            if modifiers == Qt.ControlModifier and event.key() == 90:
                self.canvas.scene().removeItem(self.vertexMarkers[-1])
                del self.pointList[-1]
                del self.vertexMarkers[-1]
                self.rubberBand.setToGeometry(
                    QgsGeometry.fromPolylineXY(self.getPointsFromList()), None)
                if not self.pointList:
                    self.canvas.scene().removeItem(self.measureLineRubber)
                    self.measureLineRubber = QgsRubberBand(self.canvas, False)
                    self.measureLineRubber.setColor(QColor(255, 0, 0))

    def canvasMoveEvent(self, event):
        if self.aimMarker:
            for marker in self.aimMarker:
                self.canvas.scene().removeItem(marker)
            self.aimMarker.clear()
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.showAimPoint(point)

    def drawToolTip(self, dist, az):
        magnAz = self.validatedAzimuth(float(az) - self.inclination)
        if self.canvas.underMouse():  # Only if mouse is over the map
            QToolTip.showText(self.canvas.mapToGlobal(self.canvas.mouseLastXY(
            )), "Расстояние: " + dist + " м\n" + "Аз. истин.: " + az + "°\nАз. магнитн.: " + str(round(magnAz, 1)) + "°", self.canvas)

    def validatedAzimuth(self, azimuth):
        if azimuth > 360:
            return azimuth - 360
        elif azimuth < 0:
            return 360 - abs(azimuth)
        else:
            return azimuth

    def drawMeasureLine(self, point):
        if not point:
            print("not point")
        if not self.pointList:
            pass
        else:
            pt1 = self.getLastPoint()
            pt2 = point
            firstAndLastPoints = [pt1, pt2]
            length = round(GeoOperations.calculateDistance(pt1, pt2), 1)
            azimuth = round(GeoOperations.calculateAzimuth(pt1, pt2), 1)
            self.drawToolTip(str(length), str(azimuth))
            self.measureLineRubber.setToGeometry(
                QgsGeometry.fromPolylineXY(firstAndLastPoints), None)

    def getLastPoint(self):
        return self.pointList[-1][0]

    def showAimPoint(self, point):
        matchres = self.snapUtils.snapToMap(point)  # QgsPointLocator.Match
        if matchres.isValid():
            m = QgsVertexMarker(self.canvas)
            m.setColor(QColor(255, 0, 255))
            m.setIconSize(7)
            m.setIconType(QgsVertexMarker.ICON_BOX)
            m.setPenWidth(2)
            m.setCenter(matchres.point())
            self.aimMarker.append(m)
            self.drawMeasureLine(matchres.point())
        else:
            self.drawMeasureLine(point)

    def getVertexMarker(self):
        m = QgsVertexMarker(self.canvas)
        m.setIconSize(7)
        m.setIconType(QgsVertexMarker.ICON_BOX)
        m.setPenWidth(1)
        m.setColor(QColor(255, 0, 0))
        return m

    def canvasPressEvent(self, e):
        lineType = None
        point = self.toMapCoordinates(e.pos())
        matchres = self.snapUtils.snapToMap(point)  # QgsPointLocator.Match
        if matchres.isValid():
            m = self.getVertexMarker()
            m.setCenter(matchres.point())
            self.vertexMarkers.append(m)
            pointIndex = self.ifPointExists(matchres.point())
            if (pointIndex is not None):
                self.pointList.append([matchres.point(), lineType])
                self.rubberBand.setToGeometry(
                    QgsGeometry.fromPolylineXY(self.getPointsFromList()), None)
                self.setLineType(pointIndex)
                self.signal.emit(self.pointList)
                self.deactivate()
            else:
                self.pointList.append([matchres.point(), lineType])
                self.rubberBand.setToGeometry(
                    QgsGeometry.fromPolylineXY(self.getPointsFromList()), None)

    def setLineType(self, index):
        i = 0
        for pointTuple in self.pointList:
            if i <= index:
                pointTuple[1] = "Привязка"
            elif i > index:
                pointTuple[1] = "Лесосека"
            i += 1

    def ifPointExists(self, newPoint):
        xPoint = round(newPoint.x(), 0)
        yPoint = round(newPoint.y(), 0)
        pointsList = self.getPointsFromList()
        for x in pointsList:
            xListPoint = round(x.x(), 0)
            yListPoint = round(x.y(), 0)
            if newPoint.x() == x.x() or newPoint.y() == x.y():
                return pointsList.index(x)
            elif xPoint == xListPoint and yPoint == yListPoint:
                return pointsList.index(x)
        return None

    def getPointsFromList(self):
        listOfPoints = []
        for x in self.pointList:
            listOfPoints.append(x[0])
        return listOfPoints

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

    def reset(self):
        self.deletePointsFromCanvas()

    def deactivate(self):
        try:
            self.deletePointsFromCanvas()
            self.canvas.scene().removeItem(self.rubberBand)
            self.canvas.scene().removeItem(self.measureLineRubber)
            QgsMapTool.deactivate(self)
        except:
            print("Ошибка при деактивации инструмента выноса в натуру")
