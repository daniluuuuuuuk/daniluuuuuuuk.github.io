from .. import PostgisDB
from qgis.core import *
from PyQt5 import QtCore
from . import config

MESSAGE_CATEGORY = 'Taxation Loader Task'

class Worker(QtCore.QObject):

    def __init__(self, feature):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.feature = feature
        self.identity = int(self.generateIdentity(feature))
        self.lhCode = self.getLhCode()
        self.loader = Loader('Load Taxation Info')

    def getLhCode(self):
        cf = config.Configurer('enterprise')
        settings = cf.readConfigs()
        return str(int(float(settings.get('code_lh'))))
    
    def generateIdentity(self, feature):
        self.num_lhz = int(feature['num_lhz'])
        self.num_lch = int(feature['num_lch'])
        self.num_kv = int(feature['num_kv'])
        self.num_vd = int(feature['num_vd'])
        return (1000000000 * self.num_lhz) + (10000000 * self.num_lch) + (1000 * self.num_kv) + self.num_vd

    def run(self):
        ret = None
        try:
            self.loader.run(self.identity, self.num_lhz, self.num_lch, self.lhCode)
            self.loader.waitForFinished()
            ret = [self.loader.taxDetails, self.loader.taxDetailsM10, 
            [self.loader.lh_name, self.loader.lch_name,
            self.num_kv, self.num_vd]]

        except Exception as e:
            raise e
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)

class Loader(QgsTask):

    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.taxDetails = None
        self.taxDetailsM10 = None
        self.lh_name = None
        self.lch_name = None
        self.lhCode = None

        self.total = 0
        self.iterations = 0
        self.exception = None


    def run(self, identity, lh, lch, lh_type):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.loadTaxation(identity, lh, lch, lh_type)
        return True

    def loadTaxation(self, identity, lh, lch, lhCode):
        if lch < 10:
            num_lch = '0' + str(lch)
        else:
            num_lch = str(lch)  

        postgisConnection = PostgisDB.PostGisDB()

        self.lh_name = postgisConnection.getQueryResult(
            """select name_organization 
                from "dictionary".organization
                where code_organization = '{}'""".format(lhCode))[0][0]

        self.lch_name = postgisConnection.getQueryResult(
            """select name_organization from (select id_organization from "dictionary".organization
                where code_organization = '{}') typed
                join "dictionary".organization org on org.parent_id_organization = typed.id_organization
                where substring(code_organization::varchar(255) from 9 for 2) = '{}'""".format(lhCode, num_lch))[0][0]

        self.taxDetails = postgisConnection.getQueryResult(
            """select * from "public".subcompartment_taxation where identity = '{}'""".format(int(identity)))

        self.taxDetailsM10 = postgisConnection.getQueryResult(
            """select * from "public".subcompartment_taxation_m10 where identity = '{}'""".format(int(identity)))

        # postgisConnection.__del__()

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