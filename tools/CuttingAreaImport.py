import json
from PyQt5.QtCore import QThread, pyqtSignal
from .. import PostgisDB


class CuttingAreaImport(QThread):
    """
    Поток для чтения данных из файла и записи в БД.
    """

    signal_message_result = pyqtSignal(str)

    def __init__(
        self,
        path_to_file: str,
    ):
        QThread.__init__(self)
        self.path_to_file = path_to_file

    def read_to_file(self) -> dict:
        """
        Чтение данных из JSON

        Returns:
            dict: [Данные для импорта]
        """
        with open(self.path_to_file, "r") as json_file:
            json_data = json.load(json_file)
        return json_data

    def write_data_to_db(self, imported_data):
        """
        Создание строки из команд SQL
        и выполнение этой большой одной команды

        Args:
            imported_data ([type]): [Прочтённые данные из JSON]

        Returns:
            [type]: [Успешность импорта]
        """
        sql_commands = ""
        for table in imported_data.keys():
            for record in imported_data.get(table):
                sql_commands += f"insert into {table} ({','.join(list(record.keys()))}) values {str(tuple(record.values()))};\n"
        try:
            PostgisDB.PostGisDB().getQueryResult(sql_commands, no_result=True)
        except Exception as mes:
            self.signal_message_result.emit(
                "Лесосеки не были импортированы из-за ошибки:\n" + str(mes)
            )

            return False
        return True

    def run(self):
        if self.write_data_to_db(self.read_to_file()):
            self.signal_message_result.emit("Лесосеки успешно импортировны.")
