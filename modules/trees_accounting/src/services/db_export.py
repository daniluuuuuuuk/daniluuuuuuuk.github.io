from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QThread, pyqtSignal
from ..models.public import Trees, TreesTrfHeight
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
            new_data_trees = []
            new_data_trf_trees = []
            instance_list = self.model.as_list()
            if type(instance_list) is list:
                for row in instance_list:
                    row["area_uuid"] = self.uuid

                    new_data_trf_trees.append(
                        {
                            "area_uuid": row["area_uuid"],
                            "code_species": row["code_species"],
                            "code_trf_height": row["code_trf_height"],
                        }
                    )
                    del row["code_trf_height"]

                    new_data_trees.append(row)

                new_data_trf_trees = [
                    dict(t) for t in {tuple(d.items()) for d in new_data_trf_trees}
                ]  # очищаю массив от повторений
                self.prepared_trees_data = Trees.insert_many(new_data_trees)
                self.prepared_trees_trf_data = TreesTrfHeight.insert_many(
                    new_data_trf_trees
                )
                return True

            self.signal_message_result.emit(instance_list)
            return False

        except Exception as mes:
            self.signal_message_result.emit(
                {"main_text": "Ошибка сохранения данных.", "detailed_text": str(mes)}
            )
            return False

    def run(self):
        old_trees_instances = [
            trees for trees in Trees.select().where(Trees.area_uuid == self.uuid)
        ]
        old_trees_trf_instances = [
            trees_trf
            for trees_trf in TreesTrfHeight.select().where(
                TreesTrfHeight.area_uuid == self.uuid
            )
        ]

        if self.add_to_db():
            try:
                self.prepared_trees_data.execute()
                self.prepared_trees_trf_data.execute()

                #  При успешном сохранении - удаляю старые значения:
                if old_trees_instances is not None:
                    for trees_instance in old_trees_instances:
                        trees_instance.delete_instance()

                if old_trees_trf_instances is not None:
                    for trees_trf_instance in old_trees_trf_instances:
                        trees_trf_instance.delete_instance()

                self.signal_message_result.emit(
                    {"main_text": "Данные успешно сохранены.", "detailed_text": None}
                )
            except DataError:
                self.signal_message_result.emit(
                    {
                        "main_text": "Ошибка сохранения данных. Проверьте корректность вводимых данных.",
                        "detailed_text": f"SQL запрос: \n\n {self.prepared_trees_data}",
                    }
                )

            except Exception as mes:
                self.signal_message_result.emit(
                    {
                        "main_text": "Ошибка сохранения данных.",
                        "detailed_text": str(mes),
                    }
                )
