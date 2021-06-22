from PyQt5.QtCore import QThread, pyqtSignal
from .. import PostgisDB


class SqlFileExecuter(QThread):
    """
    Поток для чтения SQL .
    """

    signal_message_result = pyqtSignal(str)

    def __init__(
        self,
        sql_file_path: str,
    ):
        QThread.__init__(self)
        self.sql_file_path = sql_file_path

    def run(self):
        try:
            with open(self.sql_file_path, "r") as f:
                contents = f.read()
                PostgisDB.PostGisDB().getQueryResult(contents, no_result=True)
            self.signal_message_result.emit("SQL скрипт успешно выполнен")

        except Exception as mes:
            self.signal_message_result.emit(str(mes))
