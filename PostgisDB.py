import psycopg2
import configparser
from .tools import config
from qgis.PyQt.QtWidgets import QMessageBox


class PostGisDB:
    def __init__(self):
        self.cf = config.Configurer("dbconnection")
        self.connection = self.setConnection()

    def setConnection(self):
        try:
            btsettings = self.cf.readConfigs()
            self.user = btsettings.get("user")
            self.password = btsettings.get("password")
            self.host = btsettings.get("host")
            self.port = btsettings.get("port")
            self.database = btsettings.get("database")
        except Exception as e:
            QMessageBox.information(None, "Ошибка", e)
            # raise e
            # print(str(e))
        try:
            return psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
            )
        except Exception as e:
            return False

    def getQueryResult(self, query, as_dict=False):
        connection = self.setConnection()
        if connection:
            curPGSQL = connection.cursor()
            curPGSQL.execute(query)

            if as_dict:
                keys = [desc[0] for desc in curPGSQL.description]
                values = curPGSQL.fetchone()
                if values:  # Данные присутствуют в бд
                    return dict(zip(keys, values))
                return {}

            return curPGSQL.fetchall()
        return []

    def testConnection(self, *args, **kwargs):
        try:
            psycopg2.connect(
                user=kwargs["user"],
                password=kwargs["password"],
                host=kwargs["host"],
                port=kwargs["port"],
                database=kwargs["database"],
            )
            return True
        except:
            return False

    def __del__(self):
        if self.connection:
            self.connection.close()
