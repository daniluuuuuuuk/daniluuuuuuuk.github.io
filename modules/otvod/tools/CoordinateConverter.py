from . import GeoOperations
from qgis.core import QgsPointXY
import decimal

class CoordinateConverter:

    def __init__(self, tableList, tableType, coordType):
        super().__init__()
        self.tableList = tableList
        self.tableType = tableType
        self.coordType = coordType

    def decdeg2dms(self, dd, roundUp):
        mnt, sec = divmod(float(dd) * 3600, 60)
        deg, mnt = divmod(float(mnt), 60)
        if roundUp:
            d = decimal.Decimal(deg).quantize(decimal.Decimal('.1'))
            m = decimal.Decimal(mnt).quantize(decimal.Decimal('.1'))
            s = decimal.Decimal(sec).quantize(decimal.Decimal('.1'))
            return d, m, s
        else:
            return deg, mnt, sec

    def dms2dd(self, degrees, minutes, seconds, roundUp):
        dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
        if roundUp:
            return decimal.Decimal(dd).quantize(decimal.Decimal('.1'))
        else:
            return dd

    def convertDMSAz2Rumb(self):
        convertedValues = []
        for row in self.tableList:
            decAz = self.dms2dd(row[1], row[2], row[3], True)
            rumbTuple = GeoOperations.azimuthToRumb(decAz)[0]
            rumb = self.decdeg2dms(rumbTuple[0], True)
            convertedValues.append([row[0], str(rumb[0]), str(rumb[1]), str(rumb[2]), row[4], rumbTuple[1], row[5]])
        return convertedValues

    def convertDDAzimuth2Rumb(self):
        convertedValues = []
        for row in self.tableList:
            azimuth = row[1]
            rumb = GeoOperations.azimuthToRumb(azimuth)[0]
            convertedValues.append([row[0], str(rumb[0]), row[2], str(rumb[1]), row[3]])
        return convertedValues

    def convertDMSRumb2Az(self):
        convertedValues = []
        for row in self.tableList:
            decRumb = self.dms2dd(row[1], row[2], row[3], True)
            decAz = GeoOperations.rumbToAzimuth(row[5], decRumb)
            dmsAz = self.decdeg2dms(decAz, True)
            convertedValues.append([row[0], str(dmsAz[0]), str(dmsAz[1]), str(dmsAz[2]), row[4], row[6]])
        return convertedValues

    def convertDDRumb2Azimuth(self):
        convertedValues = []
        for row in self.tableList:
            az = GeoOperations.rumbToAzimuth(row[3], row[1])
            convertedValues.append([row[0], str(az), str(row[2]), row[4]])
        return convertedValues

    def convertDDCoord2Azimuth(self, bindingPoint, pointsDict):
        convertedValues = []
        i = 0
        for row in pointsDict:
            point = pointsDict[row][0]
            if i == 0:
                firstPoint = bindingPoint
                secondPoint = point
            else:
                firstPoint = pointsDict[row - 1][0]
                secondPoint = point
            i += 1
            azimuth = GeoOperations.calculateAzimuth(firstPoint, secondPoint)
            distance = GeoOperations.calculateDistance(firstPoint, secondPoint)
            convertedValues.append([str(str(row)+"-"+str(row+1)), str(azimuth), str(distance), pointsDict[row][1]])
        return convertedValues

    def convertDDCoord2Rumb(self, bindingPoint, pointsDict):
        convertedValues = []
        i = 0
        for row in pointsDict:
            point = pointsDict[row][0]
            if i == 0:
                firstPoint = bindingPoint
                secondPoint = point
            else:
                firstPoint = pointsDict[row - 1][0]
                secondPoint = point
            i += 1
            azimuth = GeoOperations.calculateAzimuth(firstPoint, secondPoint)
            distance = GeoOperations.calculateDistance(firstPoint, secondPoint)
            rumb = GeoOperations.azimuthToRumb(azimuth)[0]
            distRounded = decimal.Decimal(distance).quantize(decimal.Decimal('.1'))
            convertedValues.append([str(str(row)+"-"+str(row+1)), str(rumb[0]), str(distRounded), str(rumb[1]), pointsDict[row][1]])
        return convertedValues
    
    def convertDMSCoord2Az(self, bindingPoint, pointsDict):
        convertedValues = []
        i = 0
        for row in pointsDict:
            point = pointsDict[row][0]
            if i == 0:
                firstPoint = bindingPoint
                secondPoint = point
            else:
                firstPoint = pointsDict[row - 1][0]
                secondPoint = point
            i += 1
            azimuth = GeoOperations.calculateAzimuth(firstPoint, secondPoint)
            distance = GeoOperations.calculateDistance(firstPoint, secondPoint)
            azRounded = decimal.Decimal(azimuth).quantize(decimal.Decimal('.1'))
            distRounded = decimal.Decimal(distance).quantize(decimal.Decimal('.1'))
            azDMS = self.decdeg2dms(azRounded, True)
            convertedValues.append([str(str(row)+"-"+str(row+1)), str(azDMS[0]), str(azDMS[1]), str(azDMS[2]), str(distRounded), pointsDict[row][1]])
        return convertedValues

    def convertDMSCoord2Rumb(self, bindingPoint, pointsDict):
        convertedValues = []
        i = 0
        for row in pointsDict:
            point = pointsDict[row][0]
            if i == 0:
                firstPoint = bindingPoint
                secondPoint = point
            else:
                firstPoint = pointsDict[row - 1][0]
                secondPoint = point
            i += 1
            azimuth = GeoOperations.calculateAzimuth(firstPoint, secondPoint)
            rumb = GeoOperations.azimuthToRumb(azimuth)[0]
            distance = GeoOperations.calculateDistance(firstPoint, secondPoint)
            rumbRounded = decimal.Decimal(rumb[0]).quantize(decimal.Decimal('.1'))
            distRounded = decimal.Decimal(distance).quantize(decimal.Decimal('.1'))
            rumbDMS = self.decdeg2dms(rumb[0], True)
            convertedValues.append([str(str(row)+"-"+str(row+1)), str(rumbDMS[0]), str(rumbDMS[1]), str(rumbDMS[2]), str(distRounded), str(rumb[1]), pointsDict[row][1]])
        return convertedValues

    def convert2DMSCoords(self, pointsDict):
        convertedValues = []
        for row in pointsDict:
            point = GeoOperations.convertToWgs(pointsDict[row][0])
            lineType = pointsDict[row][1]
            x = self.decdeg2dms(point.x(), False)
            y = self.decdeg2dms(point.y(), False)
            convertedValues.append([str(str(row)+"-"+str(row+1)),
            str(y[0]), str(y[1]), str(x[2]),            
            str(x[0]), str(x[1]), str(x[2]),
            lineType])

        return convertedValues

    def convert2DDCoords(self, pointsDict):
        convertedValues = []
        for row in pointsDict:
            point =  GeoOperations.convertToWgs(pointsDict[row][0])
            lineType = pointsDict[row][1]
            convertedValues.append([str(str(row)+"-"+str(row+1)), str(point.y()), str(point.x()), lineType])
        return convertedValues

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
    
    def getFirstPointOfArea(self, pointsDict):
        firstPointOfArea = None
        for row in pointsDict:
            if row == 0 and pointsDict[row][1] == 'Лесосека':
                firstPointOfArea = row
            elif row > 0 and pointsDict[row - 1][1] == 'Привязка' and pointsDict[row][1] == 'Лесосека':
                firstPointOfArea = row
        return firstPointOfArea

        """Перевод координат в углы
        """
    def convertCoord2Angle(self, bindingPoint, pointsDict, angleType, coordType):
        convertedValues = []
        firstPointOfArea = self.getFirstPointOfArea(pointsDict)

        for row in pointsDict:
            secondPoint = pointsDict[row][0]
            if row == 0:
                firstPoint = bindingPoint
            else:
                firstPoint = pointsDict[row - 1][0]

            azimuth = GeoOperations.calculateAzimuth(firstPoint, secondPoint)
            distance = GeoOperations.calculateDistance(firstPoint, secondPoint)

            if (firstPointOfArea == None or row <= firstPointOfArea):
                if (coordType == 0):
                    az = decimal.Decimal(azimuth).quantize(decimal.Decimal('.1'))
                    convertedValues.append([str(str(row)+"-"+str(row+1)), str(az), str(distance), pointsDict[row][1]])
                else:
                    azRounded = decimal.Decimal(azimuth).quantize(decimal.Decimal('.1'))
                    distRounded = decimal.Decimal(distance).quantize(decimal.Decimal('.1'))
                    azDMS = self.decdeg2dms(azRounded, True)
                    convertedValues.append([str(str(row)+"-"+str(row+1)), str(azDMS[0]), str(azDMS[1]), str(azDMS[2]), str(distRounded), pointsDict[row][1]])
            else:
                if row < 2:
                    previousAzimuth = GeoOperations.calculateAzimuth(bindingPoint, firstPoint)
                else:
                    previousAzimuth = GeoOperations.calculateAzimuth(pointsDict[row - 2][0], firstPoint)
                angle = self.azimuthToAngle(previousAzimuth, azimuth, angleType)
                if (coordType == 0):
                    an = decimal.Decimal(angle).quantize(decimal.Decimal('.1'))
                    convertedValues.append([str(str(row)+"-"+str(row+1)), str(an), str(distance), pointsDict[row][1]])
                else:
                    angleRounded = decimal.Decimal(angle).quantize(decimal.Decimal('.1'))
                    distRounded = decimal.Decimal(distance).quantize(decimal.Decimal('.1'))
                    angleDMS = self.decdeg2dms(angleRounded, True)
                    convertedValues.append([str(str(row)+"-"+str(row+1)), str(angleDMS[0]), str(angleDMS[1]), str(angleDMS[2]), str(distRounded), pointsDict[row][1]])
        return convertedValues


    def convertAzimuth2Angle(self, pointsDict, angleType, coordType):
        firstPointOfArea = self.getFirstPointOfArea(pointsDict)
        convertedValues = []
        for i, row in enumerate(self.tableList):
            if i <= firstPointOfArea:
                if coordType == 0:
                    azimuth = row[1]
                    convertedValues.append([row[0], str(azimuth), str(row[2]), row[3]])
                else:
                    azimuth = self.dms2dd(row[1], row[2], row[3], True)
                    azDMS = self.decdeg2dms(azimuth, True)
                    convertedValues.append([row[0], str(azDMS[0]), str(azDMS[1]), str(azDMS[2]), row[4], row[5]])
            else:
                if coordType == 0:
                    azimuth = row[1]
                    azimuthPrevious = self.tableList[i - 1][1]
                    angle = self.azimuthToAngle(azimuthPrevious, azimuth, angleType)
                    an = decimal.Decimal(angle).quantize(decimal.Decimal('.1'))
                    convertedValues.append([row[0], str(an), str(row[2]), row[3]])
                else:
                    azimuthPrevious = self.dms2dd(self.tableList[i - 1][1], self.tableList[i - 1][2], self.tableList[i - 1][3], True)
                    azimuth = self.dms2dd(row[1], row[2], row[3], True)
                    angle = self.azimuthToAngle(azimuthPrevious, azimuth, angleType)
                    angleDMS = self.decdeg2dms(angle, True)
                    convertedValues.append([row[0], str(angleDMS[0]), str(angleDMS[1]), str(angleDMS[2]), row[4], row[5]])

        return convertedValues
                
    def convertRumb2Angle(self, pointsDict, angleType, coordType):
        firstPointOfArea = self.getFirstPointOfArea(pointsDict)
        convertedValues = []
        for i, row in enumerate(self.tableList):
            if i <= firstPointOfArea:
                if coordType == 0:
                    azimuth = GeoOperations.rumbToAzimuth(row[3], row[1])
                    az = decimal.Decimal(azimuth).quantize(decimal.Decimal('.1'))
                    convertedValues.append([row[0], str(az), str(row[2]), row[4]])
                else:
                    decRumb = self.dms2dd(row[1], row[2], row[3], True)
                    decAz = GeoOperations.rumbToAzimuth(row[5], decRumb)
                    dmsAz = self.decdeg2dms(decAz, True)
                    convertedValues.append([row[0], str(dmsAz[0]), str(dmsAz[1]), str(dmsAz[2]), row[4], row[6]])
            else:
                if coordType == 0:
                    azimuthPrevious = GeoOperations.rumbToAzimuth(self.tableList[i - 1][3], self.tableList[i - 1][1])
                    azimuth = GeoOperations.rumbToAzimuth(row[3], row[1])
                    angle = self.azimuthToAngle(azimuthPrevious, azimuth, angleType)
                    an = decimal.Decimal(angle).quantize(decimal.Decimal('.1'))
                    convertedValues.append([row[0], str(an), str(row[2]), row[4]])
                else:
                    decRumbPrevious = self.dms2dd(self.tableList[i - 1][1], self.tableList[i - 1][2], self.tableList[i - 1][3], True)
                    azimuthPrevious = GeoOperations.rumbToAzimuth(self.tableList[i - 1][5], decRumbPrevious)
                    decRumb = self.dms2dd(row[1], row[2], row[3], True)
                    azimuth = GeoOperations.rumbToAzimuth(row[5], decRumb)
                    angle = self.azimuthToAngle(azimuthPrevious, azimuth, angleType)
                    angleDMS = self.decdeg2dms(angle, True)
                    convertedValues.append([row[0], str(angleDMS[0]), str(angleDMS[1]), str(angleDMS[2]), row[4], row[6]])
        return convertedValues

        
    def convertAngle2Angle(self, pointsDict, coordType):
        firstPointOfArea = self.getFirstPointOfArea(pointsDict)
        convertedValues = []
        for i, row in enumerate(self.tableList):
            if i <= firstPointOfArea:
                if coordType == 0:
                    convertedValues.append([row[0], row[1], row[2], row[3]])
                else:
                    convertedValues.append([row[0], row[1], row[2], row[3], row[4], row[5]])
            else:
                if coordType == 0:
                    angle = 360 - float(row[1])
                    an = decimal.Decimal(angle).quantize(decimal.Decimal('.1'))
                    convertedValues.append([row[0], str(an), row[2], row[3]])
                else:
                    azimuth = self.dms2dd(row[1], row[2], row[3], True)
                    angleDD = 360 - azimuth
                    angleDMS = self.decdeg2dms(angleDD, True)
                    convertedValues.append([row[0], str(angleDMS[0]), str(angleDMS[1]), str(angleDMS[2]), row[4], row[5]])
        return convertedValues