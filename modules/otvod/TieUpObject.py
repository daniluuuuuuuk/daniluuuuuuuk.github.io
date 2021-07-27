"""Классы используются для расчета невязок и увязки полигона
"""

from qgis.core import QgsPointXY, QgsGeometry, QgsFeatureRequest
from qgis.core import QgsProject, QgsFeature
from .tools import GeoOperations
from math import cos, sin, sqrt


class Polygon():

    def __init__(self, pointList):
        self.pointList = pointList
        self.coordPoints = self.prepareCoordPoints()
        self.perimeter = self.getPerimeter()
        rsX = self.residualX()
        rsY = self.residualY()

        # print("Невязка приращения координат X", rsX)
        # print("Невязка приращения координат Y", rsY)
        # print("===>Абсолютная невязка", sqrt((rsX * rsX) + (rsY * rsY)))
        # print("Сумма поправок приращения координат Х",
        #       self.getIncrementCorrectionSumX())
        # print("Сумма поправок приращения координат Y",
        #       self.getIncrementCorrectionSumY())
        # print("Допустимая линейная невязка", self.perimeter / 200)
        self.validateSumCorrectedIncrements()
        self.getTiedUpFeature()
        self.printCorrectedFeature()

    def printCorrectedFeature(self):
        pass
        # for point in self.coordPoints:
        #     print("Приращение по X", point.coordIncrementX)
        #     print("Коррекция невязки приращения по X",
        #           point.coordIncrementCorrectionX())
        #     print("Скорректированные приращения по X",
        #           point.correctedIncrementsX())
        #     print("Приращение по Y", point.coordIncrementY)
        #     print("Коррекция невязки приращения по Y",
        #           point.coordIncrementCorrectionY())
        #     print("Скорректированные приращения по Y",
        #           point.correctedIncrementsY())

    def validateSumCorrectedIncrements(self):
        sumX = 0
        sumY = 0
        summarize = sumX + sumY
        for point in self.coordPoints:
            sumX += round(point.correctedIncrementsX(), 3)
            sumY += round(point.correctedIncrementsY(), 3)


        """Сумма исправленных приращений координат X
        """

    def getIncrementCorrectionSumX(self):
        i = 0
        for point in self.coordPoints:
            i += float(point.coordIncrementCorrectionX())
        return i

        """Сумма исправленных приращений координат Y
        """

    def getIncrementCorrectionSumY(self):
        i = 0
        for point in self.coordPoints:
            i += float(point.coordIncrementCorrectionY())
        return i

        """Рассчитать периметр неувязанного полигона
        """

    def getPerimeter(self):
        i = 0
        for point in self.coordPoints:
            i += float(point.directDistance)
        for point in self.coordPoints:
            point.setPerimeter(i)
        return i



        """Сделать из списка точек объект CoordPoint для последущих операций невязки 
        """

    def prepareCoordPoints(self):
        coordPoints = []
        for x in range(len(self.pointList)):
            if x == len(self.pointList) - 1:
                pass
            else:
                coordPoints.append(CoordPoint(
                    x, self.pointList[x], self.pointList[x + 1]))
        return coordPoints

    def getPoints(self):
        if self.coordPoints:
            return self.coordPoints

        """Невязка в приращении координат Х
        """

    def residualX(self):
        x = 0
        for point in self.coordPoints:
            x += point.coordIncrementX
        for point in self.coordPoints:
            point.residualX = x
        return x

        """Невязка в приращении координат Y
        """

    def residualY(self):
        y = 0
        for point in self.coordPoints:
            y += point.coordIncrementY
        for point in self.coordPoints:
            point.residualY = y
        return y

    def getTiedUpFeature(self):
        self.tiedUpFeaturePoints = []
        for x in range(len(self.coordPoints)):
            if x == 0:
                self.tiedUpFeaturePoints.append(self.pointList[0])
            else:
                prevPoint = self.coordPoints[x - 1]
                coordX = prevPoint.x + prevPoint.correctedIncrementsX()
                coordY = prevPoint.y + prevPoint.correctedIncrementsY()
                self.tiedUpFeaturePoints.append(QgsPointXY(coordX, coordY))
        return self.tiedUpFeaturePoints[1:]


class CoordPoint():

    def __init__(self, number, point, nextPoint):
        self.point = point
        self.nextPoint = nextPoint
        self.x = point.x()
        self.y = point.y()
        self.directDistance = self.directDistance()

        self.coordIncrementX = self.coordIncrementX()
        self.coordIncrementY = self.coordIncrementY()
        self.residualX = None
        self.residualY = None

        self.perimeter = None


        """Расстояние между точками
        """

    def directDistance(self):
        return float(GeoOperations.calculateDistance(self.point, self.nextPoint))


        """Приращение координат X
        """

    def coordIncrementX(self):
        ciX = self.nextPoint.x() - self.point.x()
        return float(ciX)

        """Приращение координат Y
        """

    def coordIncrementY(self):
        ciY = self.nextPoint.y() - self.point.y()
        return float(ciY)

        """Поправки в приращения координат X
        """

    def coordIncrementCorrectionX(self):
        cicX = (-self.residualX / self.perimeter) * self.directDistance
        return cicX

        """Поправки в приращения координат Y
        """

    def coordIncrementCorrectionY(self):
        cicY = (-self.residualY / self.perimeter) * self.directDistance
        return cicY

        """Исправленные приращения координат X
        """

    def correctedIncrementsX(self):
        return float(self.coordIncrementX + self.coordIncrementCorrectionX())

        """Исправленные приращения координат Y
        """

    def correctedIncrementsY(self):
        return float(self.coordIncrementY + self.coordIncrementCorrectionY())

        """Установка периметра
        """

    def setPerimeter(self, perimeter):
        self.perimeter = perimeter
