from . import PostgisDB
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsFeatureRequest
from qgis.core import (QgsMessageLog, QgsTask, QgsApplication, Qgis)
from PyQt5 import QtCore
from .tools import config
import re
from PyQt5.QtCore import pyqtSignal, QObject
from qgis.utils import iface

MESSAGE_CATEGORY = 'DB query task'

class ForestObject:
    def __init__(self):
        self._forestry= None
        self._quartal = None
        self._stratum = None
        self._forestEnterprise = None
        self._mObservers = []

    @property
    def forestEnterprise(self):
        return self._forestEnterprise

    @property
    def forestry(self):
        return self._forestry

    @property
    def quartal(self):
        return self._quartal

    @property
    def stratum(self):
        return self._stratum

    @forestEnterprise.setter
    def forestEnterprise(self, forestEnterprise):
        self._forestEnterprise = forestEnterprise
    
    @forestry.setter
    def forestry(self, forestry):
        self._forestry = forestry

    @quartal.setter
    def quartal(self, quartal):
        self._quartal = quartal
    
    @stratum.setter
    def stratum(self, stratum):
        self._stratum = stratum


class ForestEnterprise(QtCore.QObject):

    nameLoaded = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QObject.__init__(self)        
        try:
            cf = config.Configurer('enterprise')
            settings = cf.readConfigs()
            self._number = settings.get('num_lhz')
            self.lhCode = str(int(float(settings.get('code_lh'))))
        except Exception as e:
            self._number = -1
            self._name = ""

    @property
    def number(self):
        return self._number

    @property
    def name(self):
        return self._name

    @number.setter
    def number(self, number):
        self._number = number
    
    @name.setter
    def name(self, name):
        self._name = name

    def setNameFromDb(self):
        def workerFinished(result):
            self.worker.deleteLater()
            self.thread.quit()
            self.thread.wait()
            self.thread.deleteLater()
            self.nameLoaded.emit(result)

        self.thread = QtCore.QThread(iface.mainWindow())
        self.worker = DbQueryWorker(
                ["""select name_organization 
                from "dictionary".organization
                where code_organization = '{}'""".format(str(self.lhCode)),

                """select name_organization from (select id_organization from "dictionary".organization
                where code_organization = '{}') typed
                join "dictionary".organization org on org.parent_id_organization = typed.id_organization""".format(self.lhCode)])
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(workerFinished)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

class Forestry(ForestObject):

    def __init__(self):
        self._number = None

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number


class Quarter():

    def __init__(self):
        self._number = None

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    def getAllQuarters(self, num_lch):
        layer = QgsProject.instance().mapLayersByName("Выдела")[0]
        expression = "\"num_lch\" = '{}'".format(num_lch)
        request = QgsFeatureRequest().setFilterExpression(expression)
        features = layer.getFeatures(request)
        num_kvs = (int(feature['num_kv']) for feature in features)
        num_kvs = set(sorted(num_kvs))
        return map(str, num_kvs)

class Stratum():

    def __init__(self):
        self._number = None

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    def getAllStratums(self, num_lch, num_kv):
        layer = QgsProject.instance().mapLayersByName("Выдела")[0]
        expression = "\"num_lch\" = '{}' and \"num_kv\" = '{}'".format(num_lch, num_kv)
        request = QgsFeatureRequest().setFilterExpression(expression)
        features = layer.getFeatures(request)
        num_vds = (int(feature['num_vd']) for feature in features)
        num_vds = set(sorted(num_vds))
        return map(str, num_vds)

class DbQueryWorker(QtCore.QObject):

    def __init__(self, query):
        QtCore.QObject.__init__(self)

        self.query = query

        self.killed = False
        self.loader = DatabaseQueryTask('Query Database')

    def run(self):
        ret = None
        try:
            self.loader.run(self.query)
            self.loader.waitForFinished()
            ret = self.loader.result

        except Exception as e:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                e), MESSAGE_CATEGORY, Qgis.Info)
            raise e
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)

class DatabaseQueryTask(QgsTask):

    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.result = None

        self.total = 0
        self.iterations = 0
        self.exception = None

    def run(self, query):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)
        postgisConnection = PostgisDB.PostGisDB()
        self.result = []
        for q in query:
            self.result.append(postgisConnection.getQueryResult(q))
        # postgisConnection.__del__()
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