from PyQt5 import QtCore
import decimal
from ..models.restatement import Trees
from ..models.public import Area
from ..models.nri import *


class DBData(QtCore.QThread):
    signal_status = QtCore.pyqtSignal(dict)

    def __init__(self, table, uuid, area):
        QtCore.QThread.__init__(self)
        self.table = table
        self.uuid = uuid
        self.area = area

    def run(self):
        if self.table.columnCount() == 1:
            self.signal_status.emit(
                {"head": "Ошибка", "body": "Отсутсвуют данные сохранения."}
            )
            return None
        for column in range(1, self.table.columnCount()):
            if column % 3 == 1:
                output_data = {
                    "species": Species.select()
                    .where(Species.name_species == self.table.item(0, column).text())
                    .get()
                    .code_species
                }

                for row in range(2, self.table.rowCount() - 1):
                    # Сумму не трогаю (self.table.rowCount()-1)
                    """Собираю данные с ячеек (если ячейки пусты - ставлю 0"""
                    if self.table.item(row, column):
                        output_data["num_ind"] = int(
                            self.table.item(row, column).text()
                        )
                    else:
                        output_data["num_ind"] = 0
                    if self.table.item(row, column + 1):
                        output_data["num_fuel"] = int(
                            self.table.item(row, column + 1).text()
                        )
                    else:
                        output_data["num_fuel"] = 0
                    if self.table.item(row, column + 2):
                        output_data["num_half_ind"] = int(
                            self.table.item(row, column + 2).text()
                        )
                    else:
                        output_data["num_half_ind"] = 0
                    if (
                        output_data["num_ind"] == 0
                        and output_data["num_fuel"] == 0
                        and output_data["num_half_ind"] == 0
                    ):
                        None
                    else:
                        output_data["dmr"] = int(row * 4)
                        try:
                            Trees.create(
                                area_uuid=self.uuid,
                                code_species=output_data["species"],
                                dmr=output_data["dmr"],
                                num_ind=output_data["num_ind"],
                                num_fuel=output_data["num_fuel"],
                                num_half_ind=output_data["num_half_ind"],
                            )
                        except Exception as e:
                            self.signal_status.emit(
                                {
                                    "head": "Ошибка",
                                    "body": "Ошибка записи в БД.\nПеречётные данные не сохранены.",
                                }
                            )
                            return None

                try:
                    Area.update({Area.area: self.area}).where(
                        Area.uuid == self.uuid
                    ).execute()
                except Exception as e:
                    print(e)
                    self.signal_status.emit(
                        {
                            "head": "Ошибка",
                            "body": "Ошибка записи в БД (area).\nАтрибутивные данные не записаны в БД",
                        }
                    )
                    return None
        self.signal_status.emit(
            {"head": "Успешно", "body": "Данные успешно сохранены."}
        )
