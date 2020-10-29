import math
from .GeoOperations import *
from .GeoOperations import calculateAzimuthWithPrecision
from .GeoOperations import calculateDistanceWithPrecision
from qgis.core import QgsPointXY

"""Калькулятор невязки"""


class DiscrepancyCalculator:

    """Структура словаря self.pointsDict: {номер ночки: [точка, дирекционный угол, длина линии, горизонтальный угол]}
    """

    def __init__(self, points):
        self.points = [[point] for point in points]
        self.pointsDict = dict(zip(range(len(self.points)), self.points))
        self.linearDiscrepancy = self.getLinearDiscrepancy()
        self.maxLinearDiscrepancy = self.getMaxLinearDiscrepancy()
        self.angleDiscrepancy = self.getSimplifiedAngleDiscrepancy()
        self.maxAngleDiscrepapancy = self.getMaxAngleDiscrepancy()

        self.isLinearDiscrepancyAcceptable()
        self.isAngleDiscrepancyAcceptable()

        # self.calculateHorizontalAngles()
        # self.measuredDiscrepance = self.calculateSumDiscrepanceMeasured()
        # self.theoreticalDiscrepance = self.calculateSumDiscreapancyTheoretical()
        # print(self.pointsDict)
        # print(self.measuredDiscrepance, '~~~~', self.theoreticalDiscrepance)
        # print('@@@', self.measuredDiscrepance - self.theoreticalDiscrepance)

    def isLinearDiscrepancyAcceptable(self):
        return self.maxLinearDiscrepancy > float(self.linearDiscrepancy)

    def isAngleDiscrepancyAcceptable(self):
        return self.maxAngleDiscrepapancy > self.angleDiscrepancy

    def getLinearDiscrepancy(self):
        pointA = self.points[0][0]
        pointB = self.points[-1][0]
        distance = calculateDistanceWithPrecision(
            pointA, pointB, '.0000001')
        return distance

    def getPerimeter(self):
        linSum = 0
        for x in range(0, len(self.points) - 1):
            pointA = self.points[x][0]
            pointB = self.points[x + 1][0]
            linSum += calculateDistanceWithPrecision(
                pointA, pointB, '.0000001')
        return linSum

    def getMaxLinearDiscrepancy(self):
        return self.getPerimeter() / 200

    def getMaxAngleDiscrepancy(self):
        return 1 * math.sqrt(len(self.points)-1)

    def getSimplifiedAngleDiscrepancy(self):
        point1 = self.points[0][0]
        point4 = self.points[-2][0]
        point5 = self.points[-1][0]
        az1 = float((str(calculateAzimuthWithPrecision(
            point4, point5, '.0000001'))))
        az2 = float((str(calculateAzimuthWithPrecision(
            point4, point1, '.0000001'))))
        if abs(az1 - az2) > 180:
            return 360 - abs(az1) + abs(az2)
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
                    # print(float(horizAngle))
                    # print(round(sumCalculated, 10))
        return sumCalculated

    def calculateDirectionalAngles(self):
        for number, point in self.pointsDict.items():
            pointA = self.pointsDict.get(number)[0]
            if number < len(self.pointsDict) - 1:
                pointB = self.pointsDict.get(number + 1)[0]
            else:
                pointB = self.pointsDict.get(1)[0]
            az = str(calculateAzimuthWithPrecision(
                pointA, pointB, '.0000001'))
            distance = str(calculateDistanceWithPrecision(
                pointA, pointB, '.0000001'))
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


if __name__ == "__main__":
    pointsList = [QgsPointXY(634949.7395154417026788, 6041304.52622585743665695),
                  QgsPointXY(635029.07146056334022433,
                             6041420.9825291782617569),
                  QgsPointXY(635383.69381886976771057,
                             6041257.0739208348095417),
                  QgsPointXY(635032.28667706274427474,
                             6041226.66965983249247074),
                  QgsPointXY(634890.79190736170858145,
                             6041166.9532755883410573),
                  QgsPointXY(634949.47610439569689333, 6041304.16026490926742554)]

    # pointsList = [QgsPointXY(617424.81845468503888696, 5912539.07046225760132074),
    #               QgsPointXY(617522.45562940277159214, 5912636.76445650961250067),
    #               QgsPointXY(617653.21088422299362719, 5912602.4614575607702136),
    #               QgsPointXY(617669.72725944058038294, 5912483.17949853092432022),
    #               QgsPointXY(617515.68385558039881289, 5912397.14634604193270206),
    #               QgsPointXY(617423.36250574351288378, 5912547.99802142009139061)]

    # pointsList = [QgsPointXY(617424.81845468503888696, 5912539.07046225760132074),
    #               QgsPointXY(617522.46990116685628891,
    #                          5912636.72190873883664608),
    #               QgsPointXY(617653.65390643791761249,
    #                          5912602.79541818983852863),
    #               QgsPointXY(617670.41034779348410666,
    #                          5912483.56714271381497383),
    #               QgsPointXY(617516.12743145413696766,
    #                          5912398.04672570154070854),
    #               QgsPointXY(617423.69743535597808659, 5912548.87877077609300613)]

    print('_________')
    discCalc = DiscrepancyCalculator(pointsList)

# 0: [<QgsPointXY: POINT(634949.7395154417026788 6041304.52622585743665695)>, '34.2633333', '140.9100000'],
# 1: [<QgsPointXY: POINT(635029.07146056334022433 6041420.9825291782617569)>, '114.8066667', '390.6700000', 99.4566666],
# 2: [<QgsPointXY: POINT(635383.69381886976771057 6041257.0739208348095417)>, '265.0550000', '352.7200000', 29.751666699999987],
# 3: [<QgsPointXY: POINT(635032.28667706274427474 6041226.66965983249247074)>, '247.1183333', '153.5800000', 197.93666670000002],
# 4: [<QgsPointXY: POINT(634890.79190736170858145 6041166.9532755883410573)>, '23.1566667', '149.2300000', 43.9616666],
# 5: [<QgsPointXY: POINT(634949.47610439569689333 6041304.16026490926742554)>, '34.2680607', '141.3607518', 168.88860599999998]}


# <QgsPointXY: POINT(617424.81845468503888696, 5912539.07046225760132074)>
# [<QgsPointXY: POINT(617522.45562940277159214, 5912636.76445650961250067)>,
# <QgsPointXY: POINT(617653.21088422299362719, 5912602.4614575607702136)>,
# <QgsPointXY: POINT(617669.72725944058038294, 5912483.17949853092432022)>,
# <QgsPointXY: POINT(617515.68385558039881289, 5912397.14634604193270206)>,
# <QgsPointXY: POINT(617423.36250574351288378, 5912547.99802142009139061)>]


# <QgsPointXY: POINT(617424.81845468503888696, 5912539.07046225760132074)>
# [<QgsPointXY: POINT(617522.46990116685628891, 5912636.72190873883664608)>,
# <QgsPointXY: POINT(617653.65390643791761249, 5912602.79541818983852863)>,
# <QgsPointXY: POINT(617670.41034779348410666, 5912483.56714271381497383)>,
# <QgsPointXY: POINT(617516.12743145413696766, 5912398.04672570154070854)>,
# <QgsPointXY: POINT(617423.69743535597808659, 5912548.87877077609300613)>]
