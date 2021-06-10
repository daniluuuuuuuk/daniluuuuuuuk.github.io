import math
from .GeoOperations import *
from .GeoOperations import calculateAzimuthWithPrecision
from .GeoOperations import calculateDistanceWithPrecision
from qgis.core import QgsPointXY

"""Калькулятор невязки"""


class DiscrepancyCalculator:

    """Структура словаря self.pointsDict: {номер ночки: [точка, дирекционный угол, длина линии, горизонтальный угол]}"""

    def __init__(self, points):
        self.points = [[point] for point in points]
        self.pointsDict = dict(zip(range(len(self.points)), self.points))
        self.linearDiscrepancy = self.getLinearDiscrepancy()
        self.maxLinearDiscrepancy = self.getMaxLinearDiscrepancy()
        self.angleDiscrepancy = self.getSimplifiedAngleDiscrepancy()
        self.maxAngleDiscrepapancy = self.getMaxAngleDiscrepancy()

        self.isLinearDiscrepancyAcceptable()
        self.isAngleDiscrepancyAcceptable()

    def isLinearDiscrepancyAcceptable(self):
        return self.maxLinearDiscrepancy >= float(self.linearDiscrepancy)

    def isAngleDiscrepancyAcceptable(self):
        return self.maxAngleDiscrepapancy >= self.angleDiscrepancy

    def getLinearDiscrepancy(self):
        pointA = self.points[0][0]
        pointB = self.points[-1][0]
        distance = calculateDistanceWithPrecision(pointA, pointB, ".0000001")
        return distance

    def getPerimeter(self):
        linSum = 0
        for x in range(0, len(self.points) - 1):
            pointA = self.points[x][0]
            pointB = self.points[x + 1][0]
            linSum += calculateDistanceWithPrecision(
                pointA, pointB, ".0000001"
            )
        return linSum

    def getMaxLinearDiscrepancy(self):
        return self.getPerimeter() / 200

    def getMaxAngleDiscrepancy(self):
        return 1 * math.sqrt(len(self.points) - 1)

    def getSimplifiedAngleDiscrepancy(self):
        point1 = self.points[0][0]
        point4 = self.points[-2][0]
        point5 = self.points[-1][0]
        az1 = float(
            (str(calculateAzimuthWithPrecision(point4, point5, ".0000001")))
        )
        az2 = float(
            (str(calculateAzimuthWithPrecision(point4, point1, ".0000001")))
        )
        if abs(az1 - az2) > 180:
            az = 360 - abs(az1) + abs(az2)
            if az > 700:
                az = abs(az - 360 - 360)
            return az
        else:
            return abs(az1 - az2)

    def calculateSumDiscreapancyTheoretical(self):
        return 180 * (len(self.points) - 3)

    def calculateSumDiscrepancyMeasured(self):
        sumCalculated = 0
        for number, point in self.pointsDict.items():
            if number != 0:
                horizAngle = self.pointsDict.get(number)[3]
                if horizAngle:
                    sumCalculated += float(horizAngle)
        return sumCalculated

    def calculateDirectionalAngles(self):
        for number, point in self.pointsDict.items():
            pointA = self.pointsDict.get(number)[0]
            if number < len(self.pointsDict) - 1:
                pointB = self.pointsDict.get(number + 1)[0]
            else:
                pointB = self.pointsDict.get(1)[0]
            az = str(calculateAzimuthWithPrecision(pointA, pointB, ".0000001"))
            distance = str(
                calculateDistanceWithPrecision(pointA, pointB, ".0000001")
            )
            self.pointsDict.get(number).extend([az, distance])

    def calculateHorizontalAngles(self):
        for number, point in self.pointsDict.items():
            if number > 0:
                a = float(self.pointsDict.get(number - 1)[1])
                b = float(self.pointsDict.get(number)[1])
                angle = a + 180 - b
                if angle < 0:
                    angle += 360
                elif angle > 360:
                    angle -= 360
                self.pointsDict.get(number).append(angle)