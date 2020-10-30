from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject, QgsApplication, QgsDistanceArea, QgsCoordinateTransformContext
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsPointXY
import math
import decimal


def calculateAzimuthWithPrecision(point1, point2, precision):
    azimuth = point1.azimuth(point2)
    if azimuth < 0:
        azimuth += 360
    return decimal.Decimal(azimuth).quantize(decimal.Decimal(precision))


def calculateDistanceWithPrecision(pt1, pt2, precision):
    distance = math.sqrt(((pt1.x()-pt2.x())**2)+((pt1.y()-pt2.y())**2))
    return decimal.Decimal(distance).quantize(decimal.Decimal(precision))


def calculateAzimuth(point1, point2):
    azimuth = point1.azimuth(point2)
    if azimuth < 0:
        azimuth += 360
    return decimal.Decimal(azimuth).quantize(decimal.Decimal('.1'))


def calculateDistance(pt1, pt2):
    distance = math.sqrt(((pt1.x()-pt2.x())**2)+((pt1.y()-pt2.y())**2))
    return decimal.Decimal(distance).quantize(decimal.Decimal('.1'))


def convertToDD(degrees, minutes, seconds):
    return float(degrees) + (float(minutes) / 60) + (float(seconds) / 3600)


def convertDMSAngle(degrees, minutes, seconds):
    return float(degrees) + (float(minutes) / 60) + (float(seconds) / 3600)


def convertToZone35(point):
    # print("Convert to zone 35", point)
    transf = QgsCoordinateTransform(QgsCoordinateReferenceSystem(
        4326), QgsCoordinateReferenceSystem(32635), QgsProject.instance())
    wgsPoint = transf.transform(point)
    return wgsPoint


def convertToWgs(point):
    transf = QgsCoordinateTransform(QgsCoordinateReferenceSystem(
        32635), QgsCoordinateReferenceSystem(4326), QgsProject.instance())
    wgsPoint = transf.transform(point)
    return wgsPoint


def getCoordFromGPS():
    try:
        connectionRegistry = QgsApplication.gpsConnectionRegistry()
        connectionList = connectionRegistry.connectionList()
        GPSInfo = connectionList[0].currentGPSInformation()
        return [GPSInfo.longitude, GPSInfo.latitude]
    except:
        QMessageBox.information(
            None, 'Ошибка подключения', "Отсутствует подключение к GPS. Нажмите CTRL + 0 для настройки")


def pointFromXY(xCoord, yCoord):
    return QgsPointXY(xCoord, yCoord)


def pointFromDMSXY(xd, xm, xs, yd, ym, ys):
    x = convertToDD(xd, xm, xs)
    y = convertToDD(yd, ym, ys)
    return QgsPointXY(x, y)


def pointFromAzimuthDD(point1, angle, distance):
    calculateAzimuth = QgsDistanceArea()
    trctxt = QgsCoordinateTransformContext()
    calculateAzimuth.setEllipsoid('WGS84')
    calculateAzimuth.setSourceCrs(QgsCoordinateReferenceSystem(32635), trctxt)
    point2 = findPointByAzimuth(point1, distance, angle)
    point = convertToWgs(point2)
    return convertToZone35(point)


def findPointByAzimuth(pt1, distance, angle):
    x1 = pt1.x()
    y1 = pt1.y()
    x2 = x1 + distance * math.sin(math.radians(angle))
    y2 = y1 + distance * math.cos(math.radians(angle))
    return QgsPointXY(x2, y2)


def pointFromAzimuthDMS(point1, xd, xm, xs, distance, magnIncl):
    angle = float(convertDMSAngle(xd, xm, xs)) + magnIncl
    return pointFromAzimuthDD(point1, angle, distance)


def pointFromRumbDD(point1, rumbAngle, distance, rumb, magnIncl):
    if str(rumb) == 'СВ':
        angle = float(rumbAngle) + float(magnIncl)
    elif str(rumb) == 'ЮВ':
        angle = 180 - float(rumbAngle) - float(magnIncl)
    elif str(rumb) == 'ЮЗ':
        angle = 180 + float(rumbAngle) + float(magnIncl)
    elif str(rumb) == 'СЗ':
        angle = 360 - float(rumbAngle) - float(magnIncl)
    return pointFromAzimuthDD(point1, angle, distance)


def pointFromRumbDMS(point1, xd, xm, xs, distance, rumb, magnIncl):
    rumbAngle = convertToDD(xd, xm, xs)
    # print(rumbAngle, "<===", magnIncl)
    if str(rumb) == 'СВ':
        angle = float(rumbAngle) + float(magnIncl)
    elif str(rumb) == 'ЮВ':
        angle = 180 - float(rumbAngle) - float(magnIncl)
    elif str(rumb) == 'ЮЗ':
        angle = 180 + float(rumbAngle) + float(magnIncl)
    elif str(rumb) == 'СЗ':
        angle = 360 - float(rumbAngle) - float(magnIncl)
    return pointFromAzimuthDD(point1, angle, distance)


def parseXYRow(table, row):
    # rs = ["№", "X, °", "Y, °", "GPS", "Тип"]
    x = table.item(row, 1).text()
    y = table.item(row, 2).text()
    return convertToZone35(pointFromXY(float(y), float(x)))


def parseDMSXYRow(table, row):
    # rs = ["№", "X, °", "X, ′", "X, ″", "Y, °", "Y, ′", "Y, ″", "Тип"]
    xd = table.item(row, 1).text()
    xm = table.item(row, 2).text()
    xs = table.item(row, 3).text()
    yd = table.item(row, 4).text()
    ym = table.item(row, 5).text()
    ys = table.item(row, 6).text()
    return convertToZone35(pointFromDMSXY(float(yd), float(ym), float(ys), float(xd), float(xm), float(xs)))


def parseLeftAngleDDRow(point, azimuth, table, row, magnIncl):
    angle = float(table.item(row, 1).text()) + magnIncl
    az = float(azimuth) - 180 + angle
    distance = table.item(row, 2).text()
    return pointFromAzimuthDD(point, float(az), float(distance))


def parseRightAngleDDRow(point, azimuth, table, row, magnIncl):
    angle = float(table.item(row, 1).text()) + magnIncl
    az = float(azimuth) + 180 - angle
    distance = table.item(row, 2).text()
    return pointFromAzimuthDD(point, float(az), float(distance))


def parseLeftAngleDMSRow(point, azimuth, table, row, magnIncl):
    angleD = table.item(row, 1).text()
    angleM = table.item(row, 2).text()
    angleS = table.item(row, 3).text()
    angle = float(convertDMSAngle(angleD, angleM, angleS)) + magnIncl
    az = float(azimuth) - 180 + angle
    distance = table.item(row, 4).text()
    print(angle, az, distance, point)
    return pointFromAzimuthDD(point, float(az), float(distance))


def parseRightAngleDMSRow(point, azimuth, table, row, magnIncl):
    angleD = table.item(row, 1).text()
    angleM = table.item(row, 2).text()
    angleS = table.item(row, 3).text()
    angle = float(convertDMSAngle(angleD, angleM, angleS)) + magnIncl
    az = float(azimuth) + 180 - angle
    distance = table.item(row, 4).text()
    print(angle, az, distance, point)
    return pointFromAzimuthDD(point, float(az), float(distance))


def parseAzimuthDDRow(point, table, row, magnIncl):
    # rs = ["№", "Угол, °", "Длина линии, м", "Тип"]
    angle = float(table.item(row, 1).text()) + magnIncl
    distance = table.item(row, 2).text()
    return pointFromAzimuthDD(point, float(angle), float(distance))


def parseAzimuthDMSRow(point, table, row, magnIncl):
    # rs = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Тип"]
    xd = table.item(row, 1).text()
    xm = table.item(row, 2).text()
    xs = table.item(row, 3).text()
    distance = table.item(row, 4).text()
    return pointFromAzimuthDMS(point, float(xd), float(xm), float(xs), float(distance), magnIncl)


def parseRumbDDRow(point, table, row, magnIncl):
    # rs = ["№", "Угол, °", "Длина линии, м", "Румб", "Тип"]
    angle = table.item(row, 1).text()
    distance = table.item(row, 2).text()
    rumbWidget = table.cellWidget(row, 3)
    try:
        rumb = rumbWidget.currentText()
        return pointFromRumbDD(point, float(angle), float(distance), rumb, magnIncl)
    except Exception as e:
        print(e)


def parseRumbDMSRow(point, table, row, magnIncl):
    # rs = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Румб", "Тип"]
    xm = table.item(row, 2).text()
    xs = table.item(row, 3).text()
    distance = table.item(row, 4).text()
    xd = table.item(row, 1).text()
    rumbWidget = table.cellWidget(row, 5)
    rumb = rumbWidget.currentText()
    return pointFromRumbDMS(point, float(xd), float(xm), float(xs), float(distance), rumb, magnIncl)


def rumbToAzimuth(rumb, rumbAngle):
    if str(rumb) == 'СВ':
        angle = float(rumbAngle)
    elif str(rumb) == 'ЮВ':
        angle = 180 - float(rumbAngle)
    elif str(rumb) == 'ЮЗ':
        angle = 180 + float(rumbAngle)
    elif str(rumb) == 'СЗ':
        angle = 360 - float(rumbAngle)
    return angle


def azimuthToRumb(az):
    a = float(az)
    azimuth = decimal.Decimal(a).quantize(decimal.Decimal('.1'))
    rumbsList = []
    if azimuth >= 0 and azimuth <= 90:
        angle = azimuth
        rumbsList.append((angle, "СВ"))
    elif azimuth >= 90.001 and azimuth <= 180:
        angle = 180 - azimuth
        rumbsList.append((angle, "ЮВ"))
    elif azimuth >= 180.001 and azimuth <= 270:
        angle = azimuth - 180
        rumbsList.append((angle, "ЮЗ"))
    elif azimuth >= 270.001 and azimuth <= 360:
        angle = 360 - azimuth
        rumbsList.append((angle, "СЗ"))
    return rumbsList


def convertToDMS(dd):
    mnt, sec = divmod(dd*3600, 60)
    deg, mnt = divmod(mnt, 60)
    return [deg, mnt, sec]
