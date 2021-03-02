from PyQt5.QtCore import QThread, pyqtSignal
import psycopg2
import subprocess
from psycopg2 import sql
from .. import util


class DataImport(QThread):
    """
    Импорт базы данных
    """

    signal_message_result = pyqtSignal(str)

    def __init__(self, db_info: dict, filename: str):
        QThread.__init__(self)
        self.db_info = db_info
        self.filename = filename

    def pre_import(self) -> bool:
        """
        Подгатавливаю БД к импорту

        Returns:
            bool: [Успех подготовки БД к импорту]
        """
        try:
            dbconnection = psycopg2.connect(
                **{**self.db_info, "database": None}
            )
            dbconnection.autocommit = True

            curPGSQL = dbconnection.cursor()
            curPGSQL.execute(
                sql.SQL("CREATE DATABASE {};").format(
                    sql.Identifier(self.db_info["database"])
                )
            )
            curPGSQL.execute(f"CREATE EXTENSION IF NOT exists postgis;")
        except Exception as e:
            return str(e)
        return True

    def run(self):
        if self.pre_import():
            try:
                command = (
                    f'"{util.resolvePath("bin/pg_restore.exe")}" --verbose --host={self.db_info["host"]} '
                    f"--port={self.db_info['port']} "
                    f"--username={self.db_info['user']} "
                    f"--format=t "
                    f"--dbname={self.db_info['database']} "
                    f"{self.filename} "
                )

                with open(util.resolvePath("tmp/qgis.log"), "a") as err:
                    proc = subprocess.Popen(
                        command,
                        shell=True,
                        env={
                            "PGPASSWORD": self.db_info["password"],
                            "SYSTEMROOT": "C:\Windows",
                        },
                        stderr=err,
                    )
                    proc.wait()

                self.signal_message_result.emit("Готово")
            except Exception as e:
                self.signal_message_result.emit(str(e))
