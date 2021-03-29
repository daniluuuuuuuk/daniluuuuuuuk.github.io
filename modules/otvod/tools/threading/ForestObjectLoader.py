import random
from ..... import PostgisDB
from time import sleep
from qgis.core import QgsMessageLog, QgsTask, QgsApplication, Qgis
from .....tools import config

MESSAGE_CATEGORY = "Forest Object Loader Task"


class ForestObjectLoader(QgsTask):
    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.allGplho = None
        self.allLeshozy = None
        self.allLesnichestva = None
        self.allRestatements = None
        self.lhTypesAndNames = None

        self.lhCode = self.getLhCode()

        self.total = 0
        self.iterations = 0
        self.exception = None

    def getLhCode(self):
        cf = config.Configurer("enterprise")
        settings = cf.readConfigs()
        try:
            # поле может быть пустым но определяться как с наличием значения
            code = str(int(float(settings.get("code_lh"))))
            return code
        except:
            return "0"

    def getAllRestatements(self):
        postgisConnection = PostgisDB.PostGisDB()
        allRestatements = postgisConnection.getQueryResult(
            """select uid, num_lch, num_kv, num_vds, num, leshos from "public".area where geom is NULL"""
        )
        tupleToList = []
        for x in allRestatements:
            tupleToList.append(list(x))

        for x in tupleToList:
            num_lch = x[1]
            leshos = x[-1]

            code = "00"

            if len(str(num_lch)) == 2:
                code = str(num_lch)
            else:
                code = "0" + str(num_lch)

            forestry = postgisConnection.getQueryResult(
                """select name_organization from (select id_organization from "dictionary".organization
                where code_organization = '{}') typed
                join "dictionary".organization org on org.parent_id_organization = typed.id_organization
                where substring(code_organization::varchar(255) from 9 for 2) = '{}'""".format(
                    self.lhCode, code
                )
            )[0][0]
            x[1] = forestry

        self.allRestatements = tupleToList

        # postgisConnection.__del__()

    def getAllGPLHO(self):
        postgisConnection = PostgisDB.PostGisDB()
        gplhos = postgisConnection.getQueryResult(
            """select id_organization, name_organization from "dictionary".organization where type_organization = 'ГПЛХО' 
            or code_organization = '1500200000'
            or code_organization = '1500300000'
            or code_organization = '1500400000'
            or code_organization = '1500500000'
            or code_organization = '1500600000'
            or code_organization = '1500700000'"""
        )
        self.allGplho = dict(
            (idObject, nameObject) for (idObject, nameObject) in gplhos
        )
        # postgisConnection.__del__()

    def getLeshozyByGPLHO(self, gplhoName):
        postgisConnection = PostgisDB.PostGisDB()
        if gplhoName == "Управление делами Президента РБ":
            gplhoId = 966
        elif gplhoName == "Министерство обороны РБ":
            gplhoId = 955
        elif gplhoName == "Министерство по чрезвычайным ситуациям":
            gplhoId = 1067
        elif gplhoName == "Местные исполнительные и распорядительные органы":
            gplhoId = 1085
        elif gplhoName == "Министерство образования РБ":
            gplhoId = 1102
        elif gplhoName == "Национальная академия наук Беларуси":
            gplhoId = 1108
        else:
            gplhoId = postgisConnection.getQueryResult(
                """select id_organization from "dictionary".organization where name_organization = '{}' and type_organization = 'ГПЛХО'""".format(
                    gplhoName
                )
            )[0][0]
        leshozy = postgisConnection.getQueryResult(
            """select code_organization, type_organization, name_organization from "dictionary".organization where parent_id_organization = '{}'""".format(
                gplhoId
            )
        )
        self.allLeshozy = dict(
            (idObject, nameObject)
            for (idObject, lhType, nameObject) in leshozy
        )
        self.lhTypesAndNames = dict(
            (nameObject, lhType) for (idObject, lhType, nameObject) in leshozy
        )
        # postgisConnection.__del__()

    def getLesnichestvaByLeshoz(self, leshozName):
        postgisConnection = PostgisDB.PostGisDB()
        leshozId = postgisConnection.getQueryResult(
            """select id_organization from "dictionary".organization where name_organization = '{}'""".format(
                leshozName
            )
        )
        lesnichestva = postgisConnection.getQueryResult(
            """select code_organization, name_organization from "dictionary".organization where parent_id_organization = {}""".format(
                leshozId[0][0]
            )
        )
        self.allLesnichestva = dict(
            (idObject, nameObject) for (idObject, nameObject) in lesnichestva
        )
        # postgisConnection.__del__()

    def run(self, gplho, leshoz):
        QgsMessageLog.logMessage(
            '\nStarted task "{}"'.format(self.description()),
            MESSAGE_CATEGORY,
            Qgis.Info,
        )

        if gplho is None:
            self.getAllRestatements()
            self.getAllGPLHO()

        elif gplho is not None and leshoz is None:
            self.getLeshozyByGPLHO(gplho)

        elif gplho is not None and leshoz is not None:
            self.getLesnichestvaByLeshoz(leshoz)

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
