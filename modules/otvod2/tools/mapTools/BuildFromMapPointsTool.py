from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand, QgsMapTool, QgsVertexMarker, QgsMapCanvasSnappingUtils, QgisInterface
from qgis.core import QgsPointXY, QgsRectangle
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, QObject, QPoint
from qgis.core import QgsWkbTypes, QgsSnappingUtils, QgsPointLocator, QgsTolerance, QgsSnappingConfig, QgsProject, QgsGeometry
from ...tools import GeoOperations
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolTip, QWidget, QApplication


class BuildFromMapPointsTool(QgsMapToolEmitPoint, QWidget):

    signal = pyqtSignal(object)

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        # print("____________________________________")
        self.snapUtils = self.canvas.snappingUtils()
        self.prj = QgsProject.instance()
        self.snapConfig = self.prj.snappingConfig()
        print(self.snapConfig.setMode(3))
        self.snapConfig.setType(2)
        # print(self.snapConfig.type())
        self.snapUtils.setConfig(self.snapConfig)

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
                # self.drawMeasureLine(None)

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
        if self.canvas.underMouse():  # Only if mouse is over the map
            QToolTip.showText(self.canvas.mapToGlobal(self.canvas.mouseLastXY(
            )), "Расстояние: " + dist + " м\n" + "Азимут: " + az + "°", self.canvas)
            # QToolTip.hideText()

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
        # matchres = self.snapUtils.snapToMap(point)  # QgsPointLocator.Match
        # if matchres.isValid():
        m = QgsVertexMarker(self.canvas)
        m.setColor(QColor(255, 0, 255))
        m.setIconSize(7)
        # or ICON_CROSS, ICON_X, ICON_BOX
        m.setIconType(QgsVertexMarker.ICON_BOX)
        m.setPenWidth(2)
        m.setCenter(point)
        self.aimMarker.append(m)
        self.drawMeasureLine(point)
        # else:
        #   self.drawMeasureLine(point)

    def getVertexMarker(self):
        m = QgsVertexMarker(self.canvas)
        m.setIconSize(7)
        # or ICON_CROSS, ICON_X, ICON_BOX
        m.setIconType(QgsVertexMarker.ICON_BOX)
        m.setPenWidth(1)
        m.setColor(QColor(255, 0, 0))
        return m

    def canvasPressEvent(self, e):
        lineType = None
        if e.button() == Qt.RightButton:
            self.signal.emit(self.pointList)
        elif e.button() == Qt.LeftButton:
            lineType = "Лесосека"
            point = self.toMapCoordinates(e.pos())
            # matchres = self.snapUtils.snapToMap(point)  # QgsPointLocator.Match
            # if matchres.isValid():
            m = self.getVertexMarker()
            m.setCenter(point)
            self.vertexMarkers.append(m)
            pointIndex = self.ifPointExists(point)
            if (pointIndex is not None):
                self.pointList.append([point, lineType])
                self.rubberBand.setToGeometry(
                    QgsGeometry.fromPolylineXY(self.getPointsFromList()), None)
                self.setLineType(pointIndex)
                self.signal.emit(self.pointList)
                self.deactivate()
            else:
                self.pointList.append([point, lineType])
                self.rubberBand.setToGeometry(
                    QgsGeometry.fromPolylineXY(self.getPointsFromList()), None)
                # self.signal.emit(self.pointList)

    def setLineType(self, index):
        i = 0
        for pointTuple in self.pointList:
            if i <= index:
                pointTuple[1] = "Привязка"
            elif i > index:
                pointTuple[1] = "Лесосека"
            i += 1

    def ifPointExists(self, newPoint):
        xPoint = round(newPoint.x(), 4)
        yPoint = round(newPoint.y(), 4)
        pointsList = self.getPointsFromList()
        for x in pointsList:
            xListPoint = round(x.x(), 4)
            yListPoint = round(x.y(), 4)
            if newPoint.x() == x.x() and newPoint.y() == x.y():
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
            # self.canvas.refresh()
            QgsMapTool.deactivate(self)
        except:
            print("Ошибка при деактивации инструмента выноса в натуру")
