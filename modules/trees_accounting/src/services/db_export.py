from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QThread, pyqtSignal
from ..models.public import Trees
from peewee import DataError


class DBExportedData(QThread):
    """
    Поток для сохранения данных в БД.
    Сначало подгружаю старые данные (которые были для данного uuid)
    Потом загружаю в БД новые данные, и если они загрузились, то сохраняю новые данные и
    удаляю старые данные.
    """

    signal_message_result = pyqtSignal(dict)

    def __init__(self, uuid: str, model: QStandardItemModel):
        QThread.__init__(self)
        self.uuid = uuid
        self.model = model

    def add_to_db(self) -> bool:
        """
        Добавляем данные в БД
        """
        try:
            new_data = []
            for row in self.model.as_list():
                row["area_uuid"] = self.uuid
                new_data.append(row)
            self.prepared_data = Trees.insert_many(new_data)
            return True
        except Exception as mes:
            self.signal_message_result.emit(
                {"main_text": "Ошибка сохранения данных.", "detailed_text": str(mes)}
            )
            return False

    def run(self):

        old_instances = [
            trees for trees in Trees.select().where(Trees.area_uuid == self.uuid)
        ]

        if self.add_to_db():
            try:
                self.prepared_data.execute()

                if old_instances is not None:
                    for instance in old_instances:
                        instance.delete_instance()

                self.signal_message_result.emit(
                    {"main_text": "Данные успешно сохранены.", "detailed_text": None}
                )
            except DataError:
                self.signal_message_result.emit(
                    {
                        "main_text": "Ошибка сохранения данных. Проверьте корректность вводимых данных.",
                        "detailed_text": f"SQL запрос: \n\n {self.prepared_data}",
                    }
                )

            except Exception as mes:
                self.signal_message_result.emit(
                    {
                        "main_text": "Ошибка сохранения данных.",
                        "detailed_text": str(mes),
                    }
                )
