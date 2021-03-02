import random
from ..... import PostgisDB
from time import sleep
from qgis.core import QgsMessageLog, QgsTask, QgsApplication, Qgis
from .....tools import config

MESSAGE_CATEGORY = "Restatement Object Loader Task"


class RestatementLoader(QgsTask):
    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.restatementData = None

        self.total = 0
        self.iterations = 0
        self.exception = None

        self.lhCode = self.getLhCode()

    def getLhCod(self):
        cf = config.Configurer("enterprise")
        settings = cf.readConfigs()
        return str(int(float(settings.get("code_lh"))))

    def getRestatementData(self, guid):
        postgisConnection = PostgisDB.PostGisDB()
        restatementData = postgisConnection.getQueryResult(
            """select leshos, num_lch, num_kv, num_vds, area, num, uid, date from "public".area where uid = '{}'""".format(
                guid
            )
        )
        self.restatementData = self.unwrapRestatementData(restatementData)
        # postgisConnection.__del__()

    def unwrapRestatementData(self, data):
        postgisConnection = PostgisDB.PostGisDB()

        leshozName = postgisConnection.getQueryResult(
            """select name_organization 
                from "dictionary".organization
                where code_organization = '{}'""".format(
                self.lhCode
            )
        )[0][0]

        gplhoNumber = postgisConnection.getQueryResult(
            """select parent_id_organization from "dictionary".organization where name_organization = '{}'""".format(
                leshozName
            )
        )[0][0]

        gplhoName = postgisConnection.getQueryResult(
            """select name_organization from "dictionary".organization where id_organization = {}""".format(
                gplhoNumber
            )
        )[0][0]

        code = "00"
        if len(str(data[0][1])) == 2:
            code = str(data[0][1])
        else:
            code = "0" + str(data[0][1])

        forestry = postgisConnection.getQueryResult(
            """select name_organization from (select id_organization from "dictionary".organization
                where code_organization = '{}') typed
                join "dictionary".organization org on org.parent_id_organization = typed.id_organization
                where substring(code_organization::varchar(255) from 9 for 2) = '{}'""".format(
                self.lhCode, code
            )
        )[0][0]

        forestObjectCode = postgisConnection.getQueryResult(
            """select code_organization from (select id_organization from "dictionary".organization
                where code_organization = '{}') typed
                join "dictionary".organization org on org.parent_id_organization = typed.id_organization
                where substring(code_organization::varchar(255) from 9 for 2) = '{}'""".format(
                self.lhCode, code
            )
        )[0][0]

        # postgisConnection.__del__()

        return {
            "ГПЛХО": [gplhoName, gplhoNumber],
            "Лесхоз": [leshozName, data[0][0]],
            "Лесничество": [forestry, data[0][1]],
            "Квартал": data[0][2],
            "Выдел": data[0][3],
            "Площадь": data[0][4],
            "Номер": data[0][5],
            "uid": data[0][6],
            "Дата": data[0][7],
            "Код": forestObjectCode,
        }

    def run(self, guid):
        QgsMessageLog.logMessage(
            '\nStarted task "{}"'.format(self.description()),
            MESSAGE_CATEGORY,
            Qgis.Info,
        )

        self.getRestatementData(guid)

        return True

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage(
                'Task "{name}" completed\n'.format(name=self.description()),
                MESSAGE_CATEGORY,
                Qgis.Success,
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without exception '
                    "(probably the task was manually canceled by the "
                    "user)".format(name=self.description()),
                    MESSAGE_CATEGORY,
                    Qgis.Warning,
                )
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.description(), exception=self.exception
                    ),
                    MESSAGE_CATEGORY,
                    Qgis.Critical,
                )
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was cancelled'.format(name=self.description()),
            MESSAGE_CATEGORY,
            Qgis.Info,
        )
        super().cancel()
