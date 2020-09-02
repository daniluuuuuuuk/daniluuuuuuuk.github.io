import psycopg2
import configparser
from .tools import config
class PostGisDB:

    def __init__(self):
        self.cf = config.Configurer('dbconnection')
        self.connection = self.setConnection()

    def setConnection(self):
        try:
            btsettings = self.cf.readConfigs()
            self.user = btsettings.get('user')
            self.password = btsettings.get('password')
            self.host = btsettings.get('host')
            self.port = btsettings.get('port')
            self.database = btsettings.get('database')
        except Exception as e:
            print(str(e))
        try:
            return psycopg2.connect(user = self.user,
                        password = self.password,
                        host = self.host,
                        port = self.port,
                        database = self.database)
        except Exception as e:
            return False

    def getQueryResult(self, query):
        connection = self.setConnection()
        curPGSQL = connection.cursor()
        curPGSQL.execute(query)
        return curPGSQL.fetchall()

    def testConnection(self, *args, **kwargs):
        try:
            psycopg2.connect(user = kwargs['user'],
                        password = kwargs['password'],
                        host = kwargs['host'],
                        port = kwargs['port'],
                        database = kwargs['database'])
            return True
        except:
            return False

    def __del__(self):
        self.connection.close()

class QgsConnection:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def createQgsConnection(self):
        pass

    def addLayersToProject(self):
        pass