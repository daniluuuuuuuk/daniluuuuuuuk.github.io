import random
from ..... import PostgisDB
from time import sleep
from qgis.core import QgsMessageLog, QgsTask, QgsApplication, Qgis

MESSAGE_CATEGORY = "Forest Object Loader Task"


class CuttingTypeLoader(QgsTask):
    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.cuttingTypes = None

        self.total = 0
        self.iterations = 0
        self.exception = None

    def getCuttingTypes(self, useType):
        postgisConnection = PostgisDB.PostGisDB()
        result = postgisConnection.getQueryResult(
            """select name_wct_meth from "dictionary".wct_meth where code_kind_use = {} and code_wct_meth::text like '%0'""".format(
                useType
            )
        )
        self.cuttingTypes = list((item[0]) for (item) in result)

    def run(self, useType):
        QgsMessageLog.logMessage(
            '\nStarted task "{}"'.format(self.description()),
            MESSAGE_CATEGORY,
            Qgis.Info,
        )

        self.getCuttingTypes(useType)

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
