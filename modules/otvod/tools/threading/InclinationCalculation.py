import random
from qgis.core import (QgsMessageLog, QgsTask, QgsApplication, Qgis)
from PyQt5 import QtCore
from .. import GeoOperations
import decimal

MESSAGE_CATEGORY = 'Inclination Calculation Loader Task'


class Worker(QtCore.QObject):

    def __init__(self, tableList, tableType, coordType, inclinationValue):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.tableList = tableList
        self.tableType = tableType
        self.coordType = coordType
        self.inclinationValue = inclinationValue
        self.loader = Calculator('Calculate Inclination')

    def run(self):
        ret = None
        try:
            self.loader.run(self.tableList, self.tableType, self.coordType, self.inclinationValue)
            self.loader.waitForFinished()
            ret = self.loader.updatedTableList
        except Exception as e:
            raise e

        self.finished.emit(ret)

    def kill(self):
        self.killed = True
        self.loader.cancel()

    finished = QtCore.pyqtSignal(object)

class Calculator(QgsTask):

    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)
        self.updatedTableList = None

    def run(self, tableList, tableType, coordType, inclinationValue):
        QgsMessageLog.logMessage('\nStarted task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)
        
        if tableType == 1:
            self.calculateAsAzimuths(tableList, coordType, inclinationValue)
        elif tableType == 2:
            self.calculateAsRumbs(tableList, coordType, inclinationValue)
        elif tableType == 3 or tableType == 4:
            self.calculateAsAngles(tableList, coordType, inclinationValue)
        return True

    def calculateAsAzimuths(self, tableList, coordType, inclinationValue):
        for row in tableList:
            if coordType == 0:
                row[1] = str(float(row[1]) - inclinationValue)
            if coordType == 1:
                azDec = GeoOperations.convertDMSAngle(row[1], row[2], row[3]) - inclinationValue
                azDMS = GeoOperations.convertToDMS(azDec)
                row[1], row[2], row[3] = str(azDMS[0]), str(azDMS[1]), str(azDMS[2])
        self.updatedTableList = tableList

    def calculateAsRumbs(self, tableList, coordType, inclinationValue):
        for row in tableList:
            if coordType == 0:
                az = GeoOperations.rumbToAzimuth(row[3], row[1]) - inclinationValue
                rumb = GeoOperations.azimuthToRumb(az)
                row[1], row[3] = str(rumb[0][0]), rumb[0][1]
            if coordType == 1:
                decRumb = self.dms2dd(row[1], row[2], row[3], True)
                decAz = GeoOperations.rumbToAzimuth(row[5], decRumb) - inclinationValue
                rumbDD = GeoOperations.azimuthToRumb(decAz)[0]
                rmb = self.decdeg2dms(rumbDD[0], True)
                row[1], row[2], row[3], row[5] = str(rmb[0]), str(rmb[1]), str(rmb[2]), rumbDD[1]
        self.updatedTableList = tableList

    def calculateAsAngles(self, tableList, coordType, inclinationValue):
        firstPoint = self.getFirstPointOfArea(tableList)
        for i, row in enumerate(tableList):
            if i > firstPoint:
                break
            if coordType == 0:
                row[1] = str(float(row[1]) - inclinationValue)
            if coordType == 1:
                azDec = GeoOperations.convertDMSAngle(row[1], row[2], row[3]) - inclinationValue
                azDMS = GeoOperations.convertToDMS(azDec)
                row[1], row[2], row[3] = str(azDMS[0]), str(azDMS[1]), str(azDMS[2])
        self.updatedTableList = tableList

    def getFirstPointOfArea(self, tableList):
        firstPointOfArea = None
        for i, row in enumerate(tableList):
            if i == 0 and row[-1] == 'Лесосека':
                firstPointOfArea = i
            elif i > 0 and tableList[i-1][-1] == 'Привязка' and tableList[i][-1] == 'Лесосека':
                firstPointOfArea = i
        return firstPointOfArea
    
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

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage(
                'Task "{name}" completed\n'
                .format(
                    name=self.description()),
                MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without exception '
                    '(probably the task was manually canceled by the '
                    'user)'.format(
                        name=self.description()),
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.description(), exception=self.exception),
                    MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was cancelled'.format(name=self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()