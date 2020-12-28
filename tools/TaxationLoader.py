from .. import PostgisDB
from qgis.core import *
from PyQt5 import QtCore


MESSAGE_CATEGORY = 'Taxation Loader Task'

class Worker(QtCore.QObject):

    def __init__(self, feature):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.feature = feature
        self.identity = self.generateIdentity(feature)
        self.loader = Loader('Load Taxation Info')

    def generateIdentity(self, feature):
        self.num_lhz = feature['num_lhz']
        self.num_lch = feature['num_lch']
        self.num_kv = feature['num_kv']
        self.num_vd = feature['num_vd']
        return (1000000000 * self.num_lhz) + (10000000 * self.num_lch) + (1000 * self.num_kv ) + self.num_vd

    def run(self):
        ret = None
        try:
            self.loader.run(self.identity, self.num_lhz, self.num_lch)
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

        self.total = 0
        self.iterations = 0
        self.exception = None


    def run(self, identity, lh, lch):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.loadTaxation(identity, lh, lch)
        return True

    def loadTaxation(self, identity, lh, lch):

        if lch < 10:
            num_lch = '0' + str(lch)
        else:
            num_lch = str(lch)  

        postgisConnection = PostgisDB.PostGisDB()

        self.lh_name = postgisConnection.getQueryResult(
            """select name_organization 
                from "dictionary".organization
                where substring(code_organization::varchar(255) from 6 for 3) = '{}'""".format(lh))[0][0]

        self.lch_name = postgisConnection.getQueryResult(
            """select name_organization 
                from "dictionary".organization
                where substring(code_organization::varchar(255) from 6 for 3) = '{}' 
                and substring(code_organization::varchar(255) from 9 for 2) = '{}'""".format(lh, num_lch))[0][0]

        self.taxDetails = postgisConnection.getQueryResult(
            """select * from "public".subcompartment_taxation where identity = '{}'""".format(identity))

        self.taxDetailsM10 = postgisConnection.getQueryResult(
            """select * from "public".subcompartment_taxation_m10 where identity = '{}'""".format(identity))    

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