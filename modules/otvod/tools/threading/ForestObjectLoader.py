import random
from ..... import PostgisDB
from time import sleep
from qgis.core import (QgsMessageLog, QgsTask, QgsApplication, Qgis)

MESSAGE_CATEGORY = 'Forest Object Loader Task'


class ForestObjectLoader(QgsTask):

    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.allGplho = None
        self.allLeshozy = None
        self.allLesnichestva = None
        self.allRestatements = None

        self.total = 0
        self.iterations = 0
        self.exception = None

    def getAllRestatements(self):
        postgisConnection = PostgisDB.PostGisDB()
        allRestatements = postgisConnection.getQueryResult(
            """select uid, num_lch, num_kv, num_vd, num, leshos from "public".area where geom is NULL""")
        
        tupleToList = []
        for x in allRestatements:
            tupleToList.append(list(x))

        for x in tupleToList:
            num_lch = x[1]
            leshos = x[-1]

            code = '00'
            if len(str(num_lch)) == 2:
                code = str(num_lch)
            else:
                code = '0' + str(num_lch)

            forestry = postgisConnection.getQueryResult(
                """select name_organization 
                from "dictionary".organization
                where substring(code_organization::varchar(255) from 6 for 3) = '{}'
                and substring(code_organization::varchar(255) from 9 for 2) = '{}'""".format(str(leshos), code))[0][0]

            x[1] = forestry

        self.allRestatements = tupleToList
            
        # postgisConnection.__del__()

    def getAllGPLHO(self):
        postgisConnection = PostgisDB.PostGisDB()
        gplhos = postgisConnection.getQueryResult(
            """select id_organization, name_organization from "dictionary".organization where type_organization = 'ГПЛХО'""")
        self.allGplho = dict((idObject, nameObject)
                             for (idObject, nameObject) in gplhos)
        # postgisConnection.__del__()

    def getLeshozyByGPLHO(self, gplhoName):
        postgisConnection = PostgisDB.PostGisDB()
        gplhoId = postgisConnection.getQueryResult(
            """select id_organization from "dictionary".organization where name_organization = '{}' and type_organization = 'ГПЛХО'""".format(gplhoName))
        leshozy = postgisConnection.getQueryResult(
            """select code_organization, name_organization from "dictionary".organization where parent_id_organization = '{}'""".format(gplhoId[0][0]))
        self.allLeshozy = dict((idObject, nameObject)
                               for (idObject, nameObject) in leshozy)
        # postgisConnection.__del__()

    def getLesnichestvaByLeshoz(self, leshozName):
        postgisConnection = PostgisDB.PostGisDB()
        leshozId = postgisConnection.getQueryResult(
            """select id_organization from "dictionary".organization where name_organization = '{}'""".format(leshozName))
        lesnichestva = postgisConnection.getQueryResult(
            """select code_organization, name_organization from "dictionary".organization where parent_id_organization = {}""".format(leshozId[0][0]))
        self.allLesnichestva = dict((idObject, nameObject)
                                    for (idObject, nameObject) in lesnichestva)
        # postgisConnection.__del__()

    def run(self, gplho, leshoz):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)


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