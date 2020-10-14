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
            distRounded = decimal.Decimal(distance).quantize(decimal.Decimal('.01'))
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
            azRounded = decimal.Decimal(azimuth).quantize(decimal.Decimal('.01'))
            distRounded = decimal.Decimal(distance).quantize(decimal.Decimal('.01'))
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
            rumbRounded = decimal.Decimal(rumb[0]).quantize(decimal.Decimal('.01'))
            distRounded = decimal.Decimal(distance).quantize(decimal.Decimal('.01'))
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