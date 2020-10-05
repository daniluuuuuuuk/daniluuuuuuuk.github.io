from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand, QgsMapTool, QgsVertexMarker, QgsMapCanvasSnappingUtils, QgisInterface
from qgis.core import QgsPointXY, QgsRectangle
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, QObject, QPoint
from qgis.core import QgsWkbTypes, QgsSnappingUtils, QgsPointLocator, QgsTolerance, QgsSnappingConfig, QgsProject, QgsGeometry
from ..tools import GeoOperations
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolTip

class AzimuthMapTool(QgsMapToolEmitPoint, QObject):

  signal = pyqtSignal(object)

  def __init__(self, canvas):
      self.canvas = canvas
      QgsMapToolEmitPoint.__init__(self, self.canvas)
      
      self.snapUtils = self.canvas.snappingUtils()
      self.prj = QgsProject.instance()
      self.snapConfig = self.prj.snappingConfig()
      self.snapUtils.setConfig(self.snapConfig)

      self.aimMarker = []
      self.vertexMarkers = []
      self.pointList = []
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
        m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X, ICON_BOX
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
      az = GeoOperations.calculateAzimuth(self.pointList[0], self.pointList[1])
      dist = GeoOperations.calculateDistance(self.pointList[0], self.pointList[1])
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
        m.setIconType(QgsVertexMarker.ICON_X) # or ICON_CROSS, ICON_X, ICON_BOX
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

"""[summary]

Returns:
    [type] -- [description]
"""
class BuildFromMapTool(QgsMapToolEmitPoint, QObject):

  signal = pyqtSignal(object)

  def __init__(self, canvas):
      self.canvas = canvas
      QgsMapToolEmitPoint.__init__(self, self.canvas)
      # print("____________________________________")
      self.snapUtils = self.canvas.snappingUtils()
      self.prj = QgsProject.instance()
      self.snapConfig = self.prj.snappingConfig()
      self.snapUtils.setConfig(self.snapConfig)

      self.aimMarker = []
      self.vertexMarkers = []
      self.rubberBand = QgsRubberBand(self.canvas, False)
      self.rubberBand.setColor(QColor(0, 0, 0))     

      self.measureLineRubber = QgsRubberBand(self.canvas, False)
      self.measureLineRubber.setColor(QColor(255, 0, 0))   
      self.pointList = [[]]
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

  def drawToolTip(self, dist, az):
      if self.canvas.underMouse(): # Only if mouse is over the map
        QToolTip.showText(self.canvas.mapToGlobal( self.canvas.mouseLastXY() ), "Расстояние: " + dist + " м\n" + "Азимут: " + az + "°" , self.canvas )
        # QToolTip.hideText()

  def drawMeasureLine(self, point):
      if not self.pointList:
        pass
      else:
        pt1 = self.getLastPoint()
        pt2 = point
        firstAndLastPoints = [pt1, pt2]
        length = round(GeoOperations.calculateDistance(pt1, pt2), 1)
        azimuth = round(GeoOperations.calculateAzimuth(pt1, pt2), 1)
        self.drawToolTip(str(length), str(azimuth))
        self.measureLineRubber.setToGeometry(QgsGeometry.fromPolylineXY(firstAndLastPoints), None)
        
  def getLastPoint(self):
      return self.pointList[-1][0]

  def showAimPoint(self, point):
      matchres = self.snapUtils.snapToMap(point)  # QgsPointLocator.Match
      if matchres.isValid():
        m = QgsVertexMarker(self.canvas)
        m.setColor(QColor(255, 0, 255))
        m.setIconSize(7)
        m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X, ICON_BOX
        m.setPenWidth(2)
        m.setCenter(matchres.point())
        self.aimMarker.append(m)
        self.drawMeasureLine(matchres.point())
      else:
        self.drawMeasureLine(point)

  def getVertexMarker(self):
    m = QgsVertexMarker(self.canvas)
    m.setIconSize(7)
    m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X, ICON_BOX
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
        self.rubberBand.setToGeometry(QgsGeometry.fromPolylineXY(self.getPointsFromList()), None)
        self.setLineType(pointIndex)
        self.signal.emit(self.pointList)
        self.deactivate()
      else:
        self.pointList.append([matchres.point(), lineType])
        self.rubberBand.setToGeometry(QgsGeometry.fromPolylineXY(self.getPointsFromList()), None)
        # self.signal.emit(self.pointList)

  def setLineType(self, index):
    i = 0
    for pointTuple in self.pointList:
      if i <= index:
        pointTuple[1] = "Привязка"
      elif i > index:
        pointTuple[1] = "Лесосека"
      i += 1

  # def canvasPressEvent(self, e):
  #     lineType = None
  #     if e.button() == Qt.RightButton:
  #       lineType = "Привязка"
  #     elif e.button() == Qt.LeftButton:
  #       lineType = "Лесосека"
  #     point = self.toMapCoordinates(e.pos())
  #     matchres = self.snapUtils.snapToMap(point)  # QgsPointLocator.Match
  #     if matchres.isValid():
  #       m = self.getVertexMarker(lineType)
  #       m.setCenter(matchres.point())
  #       self.vertexMarkers.append(m)
  #       # if (self.ifPointExists(matchres.point()) == True):
  #       #   self.deactivate()
  #       #   self.signal.emit("Close")
  #       # else:
  #       self.pointList.append([matchres.point(), lineType])
  #       self.rubberBand.setToGeometry(QgsGeometry.fromPolylineXY(self.getPointsFromList()), None)
  #       self.canvas.refresh()
  #       xPoint = round(matchres.point().x(), 5)
  #       yPoint = round(matchres.point().y(), 5)
  #       self.signal.emit(self.pointList)
  #     else:
  #       print("Не удалось выполнить привязку")

  def ifPointExists(self, newPoint):
    xPoint = round(newPoint.x(), 4)
    yPoint = round(newPoint.y(), 4)
    pointsList = self.getPointsFromList()
    for x in pointsList:
      xListPoint = round(x.x(), 4)
      yListPoint = round(x.y(), 4)
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
      # self.canvas.refresh()
      QgsMapTool.deactivate(self)
    except:
      print("Ошибка при деактивации инструмента выноса в натуру")


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
      m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X, ICON_BOX
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
      m.setIconType(QgsVertexMarker.ICON_X) # or ICON_CROSS, ICON_X, ICON_BOX
      m.setPenWidth(2)
      m.setCenter(matchres.point())
      self.vertexPoint.append(m)
      self.signal.emit(matchres.point())
    else:
      print("Не удалось сделать привязку к точке")

  def deactivate(self):
    self.reset()
    QgsMapTool.deactivate(self)

class PeekStratumFromMap(QgsMapToolEmitPoint, QObject):

    signal = pyqtSignal(object)

    def __init__(self, canvas):
      self.canvas = canvas
      QgsMapToolEmitPoint.__init__(self, self.canvas)

    def canvasMoveEvent(self, event):
      pass

    def canvasReleaseEvent(self, e):
      layers = QgsProject.instance().mapLayersByName('Выдела')
      layer = layers[0]
      x = self.toMapCoordinates(e.pos()).x()
      y = self.toMapCoordinates(e.pos()).y()
      radius = 5
      rect = QgsRectangle(x - radius,
                          y - radius,
                          x + radius,
                          y + radius)
      layer.selectByRect(rect, False)
      self.canvas.setCurrentLayer(layer)
      # self.canvas.zoomToSelected()
      # print("====>", list(layer.getSelectedFeatures())[0])      
      self.signal.emit(list(layer.getSelectedFeatures())[0])
      layer.removeSelection()

    def deactivate(self):
      pass

# class SelectStratumFromMap(QgsMapToolEmitPoint, QObject):

#     signal = pyqtSignal(object)

#     def __init__(self, canvas):
#       self.canvas = canvas
#       QgsMapToolEmitPoint.__init__(self, self.canvas)

#     def canvasMoveEvent(self, event):
#       pass

#     def canvasReleaseEvent(self, e):
#       layers = QgsProject.instance().mapLayersByName('Выдела')
#       layer = layers[0]
#       x = self.toMapCoordinates(e.pos()).x()
#       y = self.toMapCoordinates(e.pos()).y()
#       radius = 5
#       rect = QgsRectangle(x - radius,
#                           y - radius,
#                           x + radius,
#                           y + radius)
#       layer.selectByRect(rect, False)
#       self.canvas.setCurrentLayer(layer)
#       self.canvas.zoomToSelected()
#       self.signal.emit(list(layer.getSelectedFeatures())[0])

#     def deactivate(self):
#       pass

class RectangleMapTool(QgsMapToolEmitPoint, QObject):

  signal = pyqtSignal(object)

  def __init__(self, canvas):
      self.canvas = canvas
      QgsMapToolEmitPoint.__init__(self, self.canvas)
      self.rubberBand = QgsRubberBand(self.canvas, True)
      self.rubberBand.setColor(QColor(30, 30, 30, 30))
      self.rubberBand.setWidth(1)
      self.reset()

  def reset(self):
      self.startPoint = self.endPoint = None
      self.isEmittingPoint = False
      self.rubberBand.reset(True)

  def canvasPressEvent(self, e):
      self.startPoint = self.toMapCoordinates(e.pos())
      self.endPoint = self.startPoint
      self.isEmittingPoint = True
      self.showRect(self.startPoint, self.endPoint)

  def canvasReleaseEvent(self, e):
      self.isEmittingPoint = False
      r = self.rectangle()
      if r is not None:
        # print("Rectangle:", r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum())
        try:
            # self.signal.emit(str([r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum()]))
            self.signal.emit(r)
        except:
            pass

  def canvasMoveEvent(self, e):
      if not self.isEmittingPoint:
        return
      self.endPoint = self.toMapCoordinates(e.pos())
      self.showRect(self.startPoint, self.endPoint)

  def showRect(self, startPoint, endPoint):
      self.rubberBand.reset(2)
      if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
        return

      point1 = QgsPointXY(startPoint.x(), startPoint.y())
      point2 = QgsPointXY(startPoint.x(), endPoint.y())
      point3 = QgsPointXY(endPoint.x(), endPoint.y())
      point4 = QgsPointXY(endPoint.x(), startPoint.y())

      self.rubberBand.addPoint(point1, False)
      self.rubberBand.addPoint(point2, False)
      self.rubberBand.addPoint(point3, False)
      self.rubberBand.addPoint(point4, True)
      self.rubberBand.show()

  def rectangle(self):
      if self.startPoint is None or self.endPoint is None:
        return None
      elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
        return None
      return QgsRectangle(self.startPoint, self.endPoint)

  def deactivate(self):
      QgsMapTool.deactivate(self)
      self.deactivated.emit()