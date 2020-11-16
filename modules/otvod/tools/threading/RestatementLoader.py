import random
from ..... import PostgisDB
from time import sleep
from qgis.core import (QgsMessageLog, QgsTask, QgsApplication, Qgis)

MESSAGE_CATEGORY = 'Forest Object Loader Task'


class RestatementLoader(QgsTask):

    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.restatementData = None

        self.total = 0
        self.iterations = 0
        self.exception = None

    def getRestatementData(self, guid):
        postgisConnection = PostgisDB.PostGisDB()
        self.restatementData = postgisConnection.getQueryResult(
            """select gplho_text, leshos_text, lesnich_text, num_kv, num_vds, num, uid, date from "public".area where uid = '{}'""".format(guid))
        # self.restatementData = self.unwrapRestatementData(restatementData)
        postgisConnection.__del__()

    def unwrapRestatementData(self, data):
        postgisConnection = PostgisDB.PostGisDB()
        gplhoName = postgisConnection.getQueryResult(
            """select name_organization from "dictionary".organization where id_organization = {}""".format(data[0][0]))[0][0]
        leshozName = postgisConnection.getQueryResult(
            """select name_organization from "dictionary".organization where id_organization = {}""".format(data[0][1]))[0][0]
        forestry = postgisConnection.getQueryResult(
            """select name_organization from "dictionary".organization where id_organization = {}""".format(data[0][2]))[0][0]
        postgisConnection.__del__()
        return {
            'ГПЛХО': gplhoName,
            'Лесхоз': leshozName,
            'Лесничество': forestry,
            'Квартал': data[0][3],
            'Выдел': data[0][4],
            'Площадь': data[0][5],
        }

    def run(self, guid):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)
        
        self.getRestatementData(guid)

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