from qgis.core import *
from PyQt5 import QtCore, QtGui
import random
from .... import PostgisDB
from PyQt5.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import iface

MESSAGE_CATEGORY = 'Serializer Task'
AREA_POINTS_TABLE_NAME = 'area_points'
AREA_DATA_TABLE_NAME = 'area_data'

class DbSerializer(QtCore.QObject):

    signal = pyqtSignal(object, object)

    def __init__(self, data):
        QtCore.QObject.__init__(self)
        self.data = data

    def saveToDb(self):

        def workerFinished(result):
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()

        thread = QtCore.QThread(iface.mainWindow())
        worker = Worker('Save')
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        worker.data = self.data
        thread.started.connect(worker.run)
        thread.start()

    def loadFromDb(self):

        def workerFinished(result):
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()
            self.signal.emit(result[0][0], result[0][1])

        thread = QtCore.QThread(iface.mainWindow())
        worker = Worker('Load')
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        worker.data = self.data
        thread.started.connect(worker.run)
        thread.start()

class Worker(QtCore.QObject):

    def __init__(self, taskType):
        QtCore.QObject.__init__(self)
        self.killed = False

        self.taskType = taskType
        self.data = None
        self.serializer = SerializerTask('Work with serializable area', self.taskType)

    def run(self):
        ret = None
        try:
            self.serializer.run(self.data)
            self.serializer.waitForFinished()
            if self.serializer.area == None and self.taskType != 'Save':
                QMessageBox.information(
                None, 'Ошибка', "Данные отвода в БД не найдены")
                # ret = [[]]
                return
            else:
                ret = [self.serializer.area]

        except Exception as e:
            raise e
            # self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)


class SerializerTask(QgsTask):

    def __init__(self, description, taskType):
        super().__init__(description, QgsTask.CanCancel)

        self.area = None
        self.taskType = taskType

        self.total = 0
        self.iterations = 0
        self.exception = None

    def deleteExistingArea(self, uid):
        postgisConnection = PostgisDB.PostGisDB()
        cursor = postgisConnection.connection.cursor()
        cursor.execute("DELETE FROM {table} WHERE area_uid='{area_uid}'"
        .format(table=AREA_DATA_TABLE_NAME, area_uid=uid))
        postgisConnection.connection.commit()
        cursor.execute("DELETE FROM {table} WHERE area_uid='{area_uid}'"
        .format(table=AREA_POINTS_TABLE_NAME, area_uid=uid))      
        postgisConnection.connection.commit()
        # postgisConnection.__del__()

    def saveAreaToDatabase(self, data):
      try:
        postgisConnection = PostgisDB.PostGisDB()
        cursor = postgisConnection.connection.cursor()
        cursor.execute("INSERT INTO {table} "
        "VALUES ('{uuid}', {type}, {coord}, {x}, {y}, {inclination})"
        .format(table=AREA_DATA_TABLE_NAME, uuid=data[0], type=data[1], coord=data[2], x=data[3], y=data[4], inclination=data[5]))
        postgisConnection.connection.commit()

        for key, value in data[-1].items():
          cursor.execute("INSERT INTO {table} "
          "VALUES ('{area_uuid}', {pt_num}, {x}, {y}, '{point_type}')"
          .format(table=AREA_POINTS_TABLE_NAME, area_uuid=data[0], pt_num=key, x=value[0].x(), y=value[0].y(), point_type=value[1]))
          postgisConnection.connection.commit()
      finally:
          pass
        # postgisConnection.__del__()

    def loadAreaFromDatabase(self, uid):
      try:
        postgisConnection = PostgisDB.PostGisDB()
        areaData = postgisConnection.getQueryResult(
            """SELECT * FROM {table} where area_uid = '{uid}'""".format(table=AREA_DATA_TABLE_NAME, uid=uid))
        if not areaData:
            self.area = None
            return
        points = postgisConnection.getQueryResult(
            """SELECT * FROM {table} where area_uid = '{uid}'""".format(table=AREA_POINTS_TABLE_NAME, uid=uid))
        self.area = self.prepareData(areaData[0], points)
      except:
        self.area = None          
      finally:
        postgisConnection.__del__()

    def prepareData(self, data, points):
        uid = data[0]
        magneticInclination = data[5]
        bindingPoint = QgsPointXY(float(data[3]), float(data[4]))
        pointsDict = {}
        for point in points:
            pointsDict.update({point[1]: [QgsPointXY(float(point[2]), float(point[3])), point[4]]})
        return [[uid, bindingPoint, magneticInclination], [pointsDict]]

    def run(self, data):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)
        if self.taskType == 'Save':
            self.deleteExistingArea(data[0])
            self.saveAreaToDatabase(data)
        elif self.taskType == 'Load':
            self.loadAreaFromDatabase(data)

        return True

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