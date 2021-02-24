from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from typing import Union
from ..models.dictionary import Species


class TreesNotCutting(QStandardItemModel):
    """
    Структура данных деловых и дровяных
    """

    def __init__(self):
        super().__init__()
        self.__makeHorizontalHeader()

    def __makeHorizontalHeader(self):
        """Строю диаметры для таблицы"""
        self.headers = [
            "Порода",
            "Вид семенников",
            "Диаметр",
            "Количество",
            "Номер семенников",
        ]

        for header_number in range(len(self.headers)):
            self.setHorizontalHeaderItem(
                header_number, QStandardItem(self.headers[header_number])
            )

    def add_record(self, record: dict, row: Union[int, None] = None) -> bool:
        """
        Добавляю запись в модель.
        """
        if row is None:
            row = self.rowCount()
        self.setItem(row, 0, QStandardItem(record["name_species"]))
        self.item(row, 0).code_species = record["code_species"]
        self.setItem(row, 1, QStandardItem(record["name_kind_seeds"]))
        self.item(row, 1).seed_type_code = record["seed_type_code"]
        self.setItem(row, 2, QStandardItem(record["seed_dmr"]))
        self.setItem(row, 3, QStandardItem(record["seed_count"]))
        self.setItem(row, 4, QStandardItem(record["seed_number"]))

        for col in range(len(self.headers)):
            self.item(row, col).setEditable(False)

        return False

    def as_list(self) -> Union[list, dict]:
        list_from_model = []
        try:
            for row in range(self.rowCount()):  # Заходим в строку
                one_row = {
                    "code_species": self.item(row, 0).code_species,
                    "seed_type_code": self.item(row, 1).seed_type_code,
                    "seed_dmr": int(self.item(row, 2).text()),
                    "seed_count": int(self.item(row, 3).text()),
                    "seed_number": self.item(row, 4).text(),
                }
                list_from_model.append(one_row)
            return list_from_model

        except Exception as mes:
            return {
                "main_text": f"Ошибка представления данных.",
                "detailed_text": str(mes),
            }
