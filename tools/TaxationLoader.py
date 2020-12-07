# import traceback
# import time
from qgis.gui import QgsMapToolEmitPoint
from PyQt5.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QMessageBox
from .. import PostgisDB
from time import sleep
from qgis.core import *
# from .ForestObjectLoader import ForestObjectLoader
from PyQt5 import QtCore, QtGui


MESSAGE_CATEGORY = 'Taxation Loader Task'

class Worker(QtCore.QObject):

    def __init__(self, feature):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.feature = feature
        self.identity = self.generateIdentity(feature)
        self.loader = Loader('Load Taxation Info')

    def generateIdentity(self, feature):
        num_lhz = feature['num_lhz']
        num_lch = feature['num_lch']
        num_kv = feature['num_kv']
        num_vd = feature['num_vd']
        return (1000000000 * num_lhz) + (10000000 * num_lch) + (1000 * num_kv ) + num_vd

    def run(self):
        ret = None
        try:
            self.loader.run(self.identity)
            self.loader.waitForFinished()
            ret = [self.loader.taxDetails]

        except Exception as e:
            raise e
            # self.error.emit(e, traceback.format_exc())
        print(ret)
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)

class Loader(QgsTask):

    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.taxDetails = None

        self.total = 0
        self.iterations = 0
        self.exception = None


    def run(self, identity):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.loadTaxation(identity)
        return True

    def loadTaxation(self, identity):
        postgisConnection = PostgisDB.PostGisDB()
        self.taxDetails = postgisConnection.getQueryResult(
            """select * from "public".compartment_taxation_description where identity = '{}'""".format(identity))
        postgisConnection.__del__()

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