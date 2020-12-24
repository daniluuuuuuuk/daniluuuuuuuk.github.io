from PyQt5 import QtCore
from ..models.nri import Species
import json


class OutputData(QtCore.QThread):
    """
    Работа с данными для экспорта перечётки в АРМ Лесопользование-3
    """

    signal_status = QtCore.pyqtSignal(dict)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.uuid = args["uuid"]
        self.table = args["table"]
        self.export_file = args["export_file"]
        self.attribute_data = args["attribute_data"]

    def configure_trees_array(self) -> list:
        """
        Создаю массив перечётки из GUI таблицы.
        """
        _trees = []
        for column in range(1, self.table.columnCount()):
            if column % 4 == 1:
                species = self.table.item(0, column).text()

                _trees.append(
                    {
                        "full_name": species,
                        "code_spc": Species.get(
                            Species.name_species == species
                        ).code_species,
                        "code_trf_height": 1,
                        "trees": [],
                    }
                )

                for row in range(2, self.table.rowCount() - 1):
                    dmr = self.table.item(row, 0).text()
                    """Если ячейка пустая - пишу ноль"""
                    if self.table.item(row, column + 1):
                        num_ind = int(self.table.item(row, column + 1).text())
                    else:
                        num_ind = 0
                    if self.table.item(row, column + 2):
                        num_fuel = int(self.table.item(row, column + 2).text())
                    else:
                        num_fuel = 0

                    if self.table.item(row, column + 3):
                        num_biodiversity = int(self.table.item(row, column + 3).text())
                    else:
                        num_biodiversity = 0
                    """Запись деревьев"""
                    if num_ind != 0 or num_fuel != 0 or num_biodiversity != 0:
                        _trees[-1]["trees"].append(
                            {
                                "dmr": int(dmr),
                                "num_ind": num_ind,
                                "num_fuel": num_fuel,
                                "num_biodiversity": num_biodiversity,
                            }
                        )

        return _trees

    def run(self):
        """
        Экспорт в JSON
        """
        try:
            output_dict = self.attribute_data.copy()
            output_dict["species"] = self.configure_trees_array()

            # Удаляю данные, которые не нужны ЛП
            del output_dict["gplho"]
            del output_dict["enterprise"]
            del output_dict["forestry"]
            del output_dict["code_gplho"]

            with open(self.export_file, "w") as file:
                json.dump(output_dict, file, indent=1, ensure_ascii=False)
            self.signal_status.emit(
                {
                    "head": "Успешно",
                    "body": "Данные успешно экспортированы в\n" + self.export_file,
                    "detailed_text": "",
                }
            )
        except Exception as exc:
            self.signal_status.emit(
                {"head": "Ошибка экспорта.", "body": "", "detailed_text": exc}
            )
