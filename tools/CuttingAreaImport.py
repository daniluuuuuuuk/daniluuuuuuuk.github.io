import json
from typing import Union
from PyQt5.QtCore import QThread, pyqtSignal
from .. import PostgisDB
from .CuttingAreaExport import CuttingAreaExport


class CuttingAreaImport(QThread):
    """
    Поток для чтения данных из файла и записи в БД.
    """

    signal_message_result = pyqtSignal(str)

    def __init__(
        self,
        path_to_file: str,
        action_code: int,
        competitors_list: Union[list, bool],
    ):
        QThread.__init__(self)
        self.path_to_file = path_to_file
        self.action_code = action_code
        self.competitors_list = competitors_list

    def read_to_file(self) -> dict:
        """
        Чтение данных из JSON

        Returns:
            dict: [Данные для импорта]
        """
        with open(self.path_to_file, "r") as json_file:
            json_data = json.load(json_file)
        return json_data

    def action_handler(insert_method):
        """
        Обработчик выбранного действия пользователя
        по сохранению данных при имеющихся данных в бд
        """

        def wrapper(self, imported_data):
            exclude_uuid = False
            if self.action_code == 0:  # Заменить
                sql_commands = ""
                for table in CuttingAreaExport.CUTTING_AREAS_TABLES:
                    table_field = CuttingAreaExport.CUTTING_AREAS_TABLES.get(
                        table
                    )
                    sql_commands += f"DELETE FROM {table} WHERE {table_field} in {str(tuple(self.competitors_list)) if len(self.competitors_list)>1 else str(self.competitors_list).replace('{', '(').replace('}', ')')};"
                    PostgisDB.PostGisDB().getQueryResult(
                        sql_commands, no_result=True
                    )

            elif self.action_code == 1:  # Пропустить
                exclude_uuid = self.competitors_list

            return insert_method(self, imported_data, exclude_uuid)

        return wrapper

    @action_handler
    def write_data_to_db(self, imported_data, exclude_uuid=False):
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
                current_uuid = record.get(
                    CuttingAreaExport.CUTTING_AREAS_TABLES.get(table)
                )
                if exclude_uuid:
                    if current_uuid not in exclude_uuid:
                        sql_commands += f"insert into {table} ({','.join(list(record.keys()))}) values {str(tuple(record.values())) if len(record.values())>1 else str(record.values()).replace('{', '(').replace('}', ')')};\n"
                else:
                    sql_commands += f"insert into {table} ({','.join(list(record.keys()))}) values {str(tuple(record.values())) if len(record.values())>1 else str(record.values()).replace('{', '(').replace('}', ')')};\n"
        try:
            if sql_commands == "":
                self.signal_message_result.emit("Нечего импортировать.")
                return False
            PostgisDB.PostGisDB().getQueryResult(sql_commands, no_result=True)
        except Exception as mes:
            self.signal_message_result.emit(
                "Лесосеки не были импортированы из-за ошибки:\n" + str(mes)
            )

            return False
        return True

    def run(self):
        if self.write_data_to_db(self.read_to_file()):
            self.signal_message_result.emit("Лесосеки успешно импортированы.")


class SearchDuplicates(QThread):
    """
    Поток для поиска копий
    """

    signal_message_result = pyqtSignal(str)
    signal_data_result = pyqtSignal(object)

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

    def get_imported_uuids(self):
        input_data = self.read_to_file()
        imported_uuids = []
        for table in input_data:
            field_name = CuttingAreaExport.CUTTING_AREAS_TABLES.get(table)
            for record in input_data.get(table):
                imported_uuids.append(record.get(field_name))
        return set(imported_uuids)

    def search_duplicates_uuid(self):
        current_uuids = self.get_imported_uuids()
        uuid_in_db = []

        for table in CuttingAreaExport.CUTTING_AREAS_TABLES:
            table_field = CuttingAreaExport.CUTTING_AREAS_TABLES.get(table)
            sql = f"select {table_field} from {table} where {table_field} in {str(tuple(current_uuids)) if len(current_uuids)>1 else str(current_uuids).replace('{', '(').replace('}', ')')};"
            uuid_in_db += [
                i[0] for i in PostgisDB.PostGisDB().getQueryResult(sql)
            ]
        self.uuid_in_db = set(uuid_in_db)
        return self.uuid_in_db

    def get_cutting_areas_attributes(self):
        dupl_uuids = self.search_duplicates_uuid()
        if not len(dupl_uuids):
            return False
        cutting_areas_attributes = PostgisDB.PostGisDB().getQueryResult(
            f"""select lesnich_text as "Л-во", num_kv as "кв.", num_vds as "выд.", num as "№ лесосеки" from area where uid in {str(tuple(dupl_uuids)) if len(dupl_uuids)>1 else str(dupl_uuids).replace('{', '(').replace('}', ')')};""",
            as_dict=True,
        )
        duplicated_cutting_areas = ""
        for cua in cutting_areas_attributes:

            duplicated_cutting_areas += (
                "; ".join(
                    ["%s: %s" % (key, value) for (key, value) in cua.items()]
                )
                + "\n"
            )
        return duplicated_cutting_areas

    def run(self):
        self.signal_data_result.emit(self.get_cutting_areas_attributes())
