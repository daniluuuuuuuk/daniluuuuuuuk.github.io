from qgis.gui import QgsMapTool
from PyQt5.QtCore import Qt, QPoint, QObject, pyqtSignal
from qgis.core import QgsRectangle, QgsFeatureRequest, QgsGeometry
from qgis.core import edit, QgsProject
from math import sqrt
from ...tools import GeoOperations as geop
from qgis.PyQt.QtWidgets import QTableWidgetItem
from decimal import Decimal

class MovePointTool(QgsMapTool, QObject):

    pointMoved = pyqtSignal(object)

    def __init__(self, mapCanvas, table):
        QgsMapTool.__init__(self, mapCanvas)
        self.setCursor(Qt.CrossCursor)
        self.table = table
        self.dragging = False
        self.featureId = None

    def canvasPressEvent(self, e):
        feature = self.findFeatureAt(e.pos())
        if feature == None:
            return

        mapPt,layerPt = self.transformCoordinates(e.pos())
        geometry = feature.geometry()
        vertexCoord,vertex,prevVertex,nextVertex,distSquared = geometry.closestVertex(layerPt)
        distance = sqrt(distSquared)
        tolerance = self.calcTolerance(e.pos())
        if distance > tolerance:
            return

        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.featureId = feature['id']
            self.canvas().refresh()
        
    def moveVertexTo(self, pos):
        x = pos.x()
        y = pos.y()
        point = self.canvas().getCoordinateTransform().toMapCoordinates(x, y)
        layer = self.getPeeketLayer()
        with edit(layer):
            layer.changeGeometry(self.getFeatureById(self.featureId).id(), QgsGeometry.fromPointXY(point))
        self.calculateNewPosition()
    
    def getPeeketLayer(self):
        layer = QgsProject.instance().mapLayersByName('Пикеты')
        if layer:
            return layer[0]

    def calculateNewPosition(self):
       
        def getCalcRange(fid):
            if self.featureId == 1:
                pointsToCalc = (self.featureId, self.featureId + 1)
            elif fid == self.getPeeketLayer().featureCount():
                pointsToCalc = (self.featureId - 1, self.featureId)
            else:
                pointsToCalc = (self.featureId - 1, self.featureId + 1)
            return pointsToCalc

        calcRange = getCalcRange(self.featureId)
        self.calcMove(calcRange)

    def calcMove(self, calcRange):
        if self.table.tabletype == 0:
            self.calcCoord()
        elif self.table.tabletype == 1:
            self.calcAzimuth(calcRange[0], calcRange[-1])
        elif self.table.tabletype == 2:
            self.calcRumb(calcRange[0], calcRange[-1])
        elif self.table.tabletype == 3 or self.table.tabletype == 4:
            self.calcAngle()

    def calcCoord(self):
        point35 = self.getFeatureById(self.featureId).geometry().asPoint()
        pointWgs = geop.convertToWgs(point35)
        xCoord = pointWgs.y()
        yCoord = pointWgs.x()
        if self.table.coordType == 0:
            self.setTableItem(self.featureId - 1, [xCoord, yCoord])
        else:
            coords = geop.convertToDMS(xCoord) + geop.convertToDMS(yCoord)
            self.setTableItem(self.featureId - 1, coords)
            
    def calcAzimuth(self, first, last):

        for i in range(first, last):
            if first == 1 and last == 2:
                def moveFirstPoint():
                    azimuth, distance = self.calcAzimuthAndDistance(nextFeatureId=i, bindingPoint=self.getBindingPoint())
                    
                    if self.table.coordType == 0:
                        self.setTableItem(i - 1, [azimuth, distance])
                    if self.table.coordType == 1:
                        azimuth = geop.convertToDMS(azimuth)
                        self.setTableItem(i - 1, azimuth + [distance])
                moveFirstPoint()
                continue

            azimuth, distance = self.calcAzimuthAndDistance(i, i + 1)

            if self.table.coordType == 0:
                self.setTableItem(i, [azimuth, distance])
            if self.table.coordType == 1:
                azimuth = geop.convertToDMS(azimuth)
                self.setTableItem(i, azimuth + [distance])

    def calcRumb(self, first, last):
        for i in range(first, last):

            if first == 1 and last == 2:
                def moveFirstPoint():

                    azimuth, distance = self.calcAzimuthAndDistance(nextFeatureId=i, bindingPoint=self.getBindingPoint())
                    rumb = geop.azimuthToRumb(azimuth)

                    # point35Prev = self.getBindingPoint()
                    # point35Next = self.getFeatureById(i).geometry().asPoint()

                    # azimuth = geop.calculateAzimuth(point35Prev, point35Next)
                    # distance = geop.calculateDistance(point35Prev, point35Next)

                    if self.table.coordType == 0:
                        self.setRumbCombobox(i - 1, 3, rumb[0][1])
                        self.setTableItem(i - 1, [rumb[0][0], distance])
                    if self.table.coordType == 1:
                        rumbDMS = geop.convertToDMS(rumb[0][0])
                        self.setRumbCombobox(i - 1, 5, rumb[0][1])
                        self.setTableItem(i - 1, rumbDMS + [distance])

                moveFirstPoint()
                continue

            azimuth, distance = self.calcAzimuthAndDistance(i, i + 1)

            # point35Prev = self.getFeatureById(i).geometry().asPoint()
            # point35Next = self.getFeatureById(i + 1).geometry().asPoint()

            # azimuth = geop.calculateAzimuth(point35Prev, point35Next)
            # distance = geop.calculateDistance(point35Prev, point35Next)
            rumb = geop.azimuthToRumb(azimuth)

            if self.table.coordType == 0:
                self.setRumbCombobox(i, 3, rumb[0][1])
                self.setTableItem(i, [rumb[0][0], distance])
            if self.table.coordType == 1:
                rumbDMS = geop.convertToDMS(rumb[0][0])
                self.setRumbCombobox(i, 5, rumb[0][1])
                self.setTableItem(i, rumbDMS + [distance])

    def calcAngle(self):

        i = self.featureId
        pointTypes = self.getPointTypes(i)
        if (pointTypes == ['Точка', 'Лесосека', 'Лесосека'] or 
                pointTypes == ['Привязка', 'Лесосека', 'Лесосека']):
            if pointTypes[0] == 'Точка':
                azimuthA, distance12 = self.calcAzimuthAndDistance(None, i, bindingPoint=self.getBindingPoint())
            else:
                azimuthA, distance12 = self.calcAzimuthAndDistance(i - 1, i)
            azimuthB, distance23 = self.calcAzimuthAndDistance(i, i + 1)
            angleCD = self.roundUp(self.azimuthToAngle(azimuthA, azimuthB, self.table.tabletype))
            
            if self.table.coordType == 0:
                self.setTableItem(i - 1, [azimuthA, distance12])
                self.setTableItem(i, [angleCD, distance23])
            if self.table.coordType == 1:
                azimuthADMS = geop.convertToDMS(azimuthA)
                angleCDDMS = geop.convertToDMS(angleCD)
                self.setTableItem(i - 1, azimuthADMS + [distance12])
                self.setTableItem(i, angleCDDMS + [distance23])

        elif (pointTypes == ['Точка', 'Привязка', 'Лесосека'] or 
                pointTypes == ['Точка', 'Привязка', 'Привязка'] or 
                pointTypes == ['Привязка', 'Привязка', 'Привязка'] or
                pointTypes == ['Привязка', 'Привязка', 'Лесосека']):
            if pointTypes[0] == 'Точка':
                azimuthB, distance12 = self.calcAzimuthAndDistance(None, i, bindingPoint=self.getBindingPoint())
            else:
                azimuthB, distance12 = self.calcAzimuthAndDistance(i - 1, i)
            azimuthC, distance23 = self.calcAzimuthAndDistance(i, i + 1)
            if self.table.coordType == 0:
                self.setTableItem(i - 1, [azimuthB, distance12])
                self.setTableItem(i, [azimuthC, distance23])
            if self.table.coordType == 1:
                azimuthBDMS = geop.convertToDMS(azimuthB)
                azimuthCDMS = geop.convertToDMS(azimuthC)
                self.setTableItem(i - 1, azimuthBDMS + [distance12])
                self.setTableItem(i, azimuthCDMS + [distance23])

        elif pointTypes == ['Лесосека', 'Лесосека', 'Лесосека']:

            if i == 2:
                azimuthA, _ = self.calcAzimuthAndDistance(None, i - 1, bindingPoint=self.getBindingPoint())  
            else:
                azimuthA, _ = self.calcAzimuthAndDistance(i - 2, i - 1)

            azimuthB, distance12 = self.calcAzimuthAndDistance(i - 1, i)
            azimuthC, distance23 = self.calcAzimuthAndDistance(i, i + 1)

            if not i == self.table.rowCount() - 1:
                azimuthD, _ = self.calcAzimuthAndDistance(i + 1, i + 2)
                angleCD = self.roundUp(self.azimuthToAngle(azimuthC, azimuthD, self.table.tabletype))


            angleAB = self.roundUp(self.azimuthToAngle(azimuthA, azimuthB, self.table.tabletype))
            angleBC = self.roundUp(self.azimuthToAngle(azimuthB, azimuthC, self.table.tabletype))

            if self.table.coordType == 0:
                self.setTableItem(i - 1, [angleAB, distance12])
                self.setTableItem(i, [angleBC, distance23])
                if not i == self.table.rowCount() - 1:
                    self.setTableItem(i + 1, [angleCD])
            if self.table.coordType == 1:
                angleABDMS = geop.convertToDMS(angleAB)
                angleBCDMS = geop.convertToDMS(angleBC)
                self.setTableItem(i - 1, angleABDMS + [distance12])
                self.setTableItem(i, angleBCDMS + [distance23])
                if not i == self.table.rowCount() - 1:
                    angleCDDMS = geop.convertToDMS(angleCD)
                    self.setTableItem(i + 1, [angleCDDMS[0]])
                    
        elif pointTypes == ['Лесосека', 'Лесосека']:
            azimuthA, _ = self.calcAzimuthAndDistance(i - 2, i - 1)
            azimuthB, distance12 = self.calcAzimuthAndDistance(i - 1, i)

            angleAB = self.roundUp(self.azimuthToAngle(azimuthA, azimuthB, self.table.tabletype))

            if self.table.coordType == 0:
                self.setTableItem(i - 1, [angleAB, distance12])
            if self.table.coordType == 1:
                angleABDMS = geop.convertToDMS(angleAB)
                self.setTableItem(i - 1, angleABDMS + [distance12])

    """Перемещение точки затрагивает две соседних"""
    def getPointTypes(self, i):
        def getLineTypeCol():
            if self.table.coordType == 0:
                return 3
            elif self.table.coordType == 1:
                return 5

        def getLineType(n):
            col = getLineTypeCol()
            lineWidget = self.table.cellWidget(n - 1, col)
            return lineWidget.currentText()

        def getLineTypes():
            lineTypes = ()
            if i == 1:
                lineTypes = ['Точка', getLineType(i), getLineType(i + 1)]
            elif i == self.table.rowCount():
                lineTypes = [getLineType(i - 1), getLineType(i)]
            else:
                lineTypes = [getLineType(i - 1), getLineType(i), getLineType(i + 1)]
            return lineTypes

        return getLineTypes()

        
    def roundUp(self, angle):
        return Decimal(angle).quantize(Decimal('.1'))

    def calcAzimuthAndDistance(self, prevFeatureId=None, nextFeatureId=None, bindingPoint=None):
        if bindingPoint:
            point35Prev = bindingPoint
        else:
            point35Prev = self.getFeatureById(prevFeatureId).geometry().asPoint()
        point35Next = self.getFeatureById(nextFeatureId).geometry().asPoint()

        azimuth = geop.calculateAzimuth(point35Prev, point35Next)
        distance = geop.calculateDistance(point35Prev, point35Next)

        return (azimuth, distance)

    def azimuthToAngle(self, azimuthOne, azimuthTwo, angleType):
        if (angleType == 3):
            angle = 180 + float(azimuthTwo) - float(azimuthOne)
        elif (angleType == 4):
            angle = float(azimuthOne) + 180 - float(azimuthTwo)
        if angle < 0:
            angle += 360
        elif angle > 360:
            angle -= 360
        return angle

    def getBindingPoint(self):
        return self.table.bindingPoint

    def getFeatureById(self, fid):
        for feat in self.getPeeketLayer().getFeatures():
            if feat['id'] == fid:
                return feat

    def setRumbCombobox(self, row, col, rumb):
        self.table.rerenderEnabled = False
        rumbWidget = self.table.cellWidget(row, col)
        index = rumbWidget.findText(rumb)
        rumbWidget.setCurrentIndex(index)
        self.table.rerenderEnabled = True
        
    def setTableItem(self, row, items):
        for i, item in enumerate(items):
            self.table.setItem(row, i + 1, QTableWidgetItem(str(item)))

    def canvasReleaseEvent(self, e):
        if self.dragging:
            self.moveVertexTo(e.pos())
            layer = QgsProject.instance().mapLayersByName('Пикеты')
            if layer:
                layer[0].updateExtents()
            self.canvas().refresh()
            self.dragging = False
            self.featureId = None

    def findFeatureAt(self, pos):
        mapPt,layerPt = self.transformCoordinates(pos)
        tolerance = self.calcTolerance(pos)
        searchRect = QgsRectangle(layerPt.x() - tolerance,layerPt.y() - tolerance,layerPt.x() + tolerance,layerPt.y() + tolerance)
        request = QgsFeatureRequest()
        request.setFilterRect(searchRect)
        request.setFlags(QgsFeatureRequest.ExactIntersect)
        for feature in self.getPeeketLayer().getFeatures(request):
            return feature
        return None

    def calcTolerance(self, pos):
        pt1 = QPoint(pos.x(), pos.y())
        pt2 = QPoint(pos.x() + 10, pos.y())

        mapPt1, layerPt1 = self.transformCoordinates(pt1)
        mapPt2, layerPt2 = self.transformCoordinates(pt2)
        tolerance = layerPt2.x() - layerPt1.x()
        return tolerance
        
    def transformCoordinates(self, canvasPt):
        return (self.toMapCoordinates(canvasPt),self.toLayerCoordinates(self.getPeeketLayer(),canvasPt))