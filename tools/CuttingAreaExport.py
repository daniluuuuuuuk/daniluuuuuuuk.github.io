import json
from PyQt5.QtCore import QThread, pyqtSignal
from .. import PostgisDB


class CuttingAreaExport(QThread):
    """
    Поток для чтения данных из базы и записи в JSON.
    """

    signal_message_result = pyqtSignal(str)
    CUTTING_AREAS_TABLES = (
        {"area": "uid"},
        {"area_data": "area_uid"},
        {"area_line": "uid"},
        {"area_points": "area_uid"},
        {"trees": "area_uuid"},
        {"trees_not_cutting": "area_uuid"},
        {"trees_trf_height": "area_uuid"},
    )

    def __init__(
        self,
        uuid_list: list,
        path_to_file: str,
    ):
        QThread.__init__(self)
        self.uuid_list = uuid_list
        self.path_to_file = path_to_file

    def get_data_from_db(self):
        """
        Получение данных из БД для прописанных таблиц и полей идентификатора

        Returns:
            [type]: [Данные для сохранения в JSON]
        """
        output_data = {}

        try:
            for table in self.CUTTING_AREAS_TABLES:
                table_name = list(table.keys())[0]
                field_name = list(table.values())[0]

                sql_data = PostgisDB.PostGisDB().getQueryResult(
                    f"select * from {table_name} where {field_name} in ({str(self.uuid_list)[1:-1]})",
                    as_dict=True,
                )
                if sql_data != [{}]:  # Если таблица не пуста
                    output_data.setdefault(table_name, sql_data)

        except Exception as mes:
            self.signal_message_result.emit(str(mes))

        return output_data

    def write_to_file(self) -> bool:
        """
        Запись выбранных данных в JSON файл

        Returns:
            bool: [Успешно ли]
        """
        with open(self.path_to_file, "w") as outfile:
            json.dump(
                self.get_data_from_db(), outfile, ensure_ascii=False, indent=2
            )
        return True

    def run(self):
        if self.write_to_file():
            self.signal_message_result.emit(
                f"Лесосеки успешно экспортированы в:\n{self.path_to_file}"
            )
