import random
from ..... import PostgisDB
from time import sleep
from qgis.core import (QgsMessageLog, QgsTask, QgsApplication, Qgis)

MESSAGE_CATEGORY = 'Forest Object Loader Task'

class Load(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)     
        self.total = 0
        self.iterations = 0
        self.exception = None

        self.name = None
        self.number = None
        self.lesnichestva = None

    def run(self):
        """Here you implement your heavy lifting. This method should
        periodically test for isCancelled() to gracefully abort.
        This method MUST return True or False
        raising exceptions will crash QGIS so we handle them internally and
        raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)

        postgis = PostgisDB.PostGisDB()
        number_results = postgis.getQueryResult("""select distinct leshos from forestbase.mainbase""")
        self.number = number_results[0][0]
        postgis.__del__()

        postgis2 = PostgisDB.PostGisDB()
        name_results = postgis2.getQueryResult("""select col2 from reference."15500009" where col1 like '%{}'""".format(self.number))
        self.name = name_results[0]
        postgis2.__del__()

        self.getAllForestries()

        # for i in range(101):
        #     sleep(wait_time)
        #     # use setProgress to report progress
        #     self.setProgress(i)
        #     self.total += random.randint(0, 100)
        #     self.iterations += 1

        #     # check isCanceled() to handle cancellation
        #     if self.isCanceled():
        #         return False

        #     # simulate exceptions to show how to abort task
        #     if random.randint(0, 500) == 42:
        #         self.exception = Exception('bad value!')
        #         return False
        return True

    def getAllForestries(self):
        lesnichList = []
        postgis = PostgisDB.PostGisDB()
        rows = postgis.getQueryResult("""select distinct lesnich FROM forestbase.mainbase order by lesnich""")
        postgis.__del__()
        for row in rows:
            if row[0] < 10:
                query2 = """select col2 from reference."13000002" where col1 like '%{}'""".format(str(self.number) + '0' + str(row[0]))
            else:
                query2 = """select col2 from reference."13000002" where col1 like '%{}'""".format(str(self.number) + str(row[0]))
            postgis = PostgisDB.PostGisDB()
            row2 = postgis.getQueryResult(query2)[0]
                # ISSUE НЕСООТВЕТСТВИЕ КОЛИЧЕСТВА ЛЕСНИЧЕСТВ В БАЗЕ FORESTBASE И СПРАВОЧНИКЕ
            rr = row2[0]
            lesnichList.append(rr)
            postgis.__del__()
        self.lesnichestva = lesnichList
    
    def finished(self, result):

        """This method is automatically called when self.run returns. result
        is the return value from self.run.
        This function is automatically called when the task has completed (
        successfully or otherwise). You just implement finished() to do 
        whatever
        follow up stuff should happen after the task is complete. finished is
        always called from the main thread, so it's safe to do GUI
        operations and raise Python exceptions here.
        """
        if result:
            QgsMessageLog.logMessage(
                'Task "{name}" completed\n' \
                .format(
                    name=self.description()),
                MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without exception ' \
                    '(probably the task was manually canceled by the '
                    'user)'.format(
                        name=self.description()),
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.description(), exception=self.exception),
                    MESSAGE_CATEGORY, Qgis.Critical)
                # raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was cancelled'.format(name=self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()