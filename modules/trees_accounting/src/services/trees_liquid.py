from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from typing import Union
from ..models.dictionary import Species


class TreesLiquid(QStandardItemModel):
    """
    Структура данных деловых и дровяных
    """

    def __init__(self):
        super().__init__()
        self.make_dmr()

    def make_dmr(self):
        """Строю диаметры для таблицы"""
        self.setVerticalHeaderItem(0, QStandardItem("Диаметр"))
        self.setVerticalHeaderItem(1, QStandardItem("см."))

        diameters = (
            8,
            12,
            16,
            20,
            24,
            28,
            32,
            36,
            40,
            44,
            48,
            52,
            56,
            60,
            64,
            68,
            72,
            76,
            80,
            84,
            88,
            92,
            96,
            100,
            104,
            108,
            112,
            116,
            120,
            124,
        )

        for dmr in diameters:
            row_number = int(dmr / 4)
            self.setVerticalHeaderItem(row_number, QStandardItem(str(dmr)))
        self.setVerticalHeaderItem(self.rowCount(), QStandardItem("Сумма"))

    def add_new_species(self, code_species: int, name_species: str = None):
        last_column = self.columnCount()

        self.insertColumns(last_column, 2)

        if not name_species:
            name_species = Species.get(
                Species.code_species == code_species
            ).name_species

        self.setItem(0, last_column, QStandardItem(name_species))
        self.item(0, last_column).code_species = code_species
        self.item(0, last_column).setTextAlignment(Qt.AlignHCenter)
        self.item(0, last_column).setEditable(False)

        self.setItem(1, last_column, QStandardItem("Деловых"))
        self.item(1, last_column).setTextAlignment(Qt.AlignHCenter)
        self.item(1, last_column).setEditable(False)

        self.setItem(1, last_column + 1, QStandardItem("Дровяных"))
        self.item(1, last_column + 1).setTextAlignment(Qt.AlignHCenter)

        self.setItem(self.rowCount() - 1, last_column, QStandardItem("0"))
        self.item(self.rowCount() - 1, last_column).setEditable(False)

        self.setItem(self.rowCount() - 1, last_column + 1, QStandardItem("0"))
        self.item(self.rowCount() - 1, last_column + 1).setEditable(False)

        return True

    def del_species(self, code_species: int):
        species_position = self.species_position(code_species)
        self.takeColumn(species_position)
        self.takeColumn(species_position)

    def add_record(self, record: dict):
        """
        Добавляем запись вида
        {
            'id_enum': 725,
            'code_species': 71,
            'dmr': 32,
            'num_ind': 15,
            'num_fuel': 11
        }
        в модель
        """
        if self.species_position(record["code_species"]) is None:
            self.add_new_species(record["code_species"])

        current_column_ind = self.species_position(record["code_species"])
        current_column_fuel = current_column_ind + 1
        current_row = record["dmr"] / 4

        if record["num_ind"] > 0:
            self.setItem(
                current_row, current_column_ind, QStandardItem(str(record["num_ind"]))
            )
            self.summary_by_column(current_column_ind)

        if record["num_fuel"] > 0:
            self.setItem(
                current_row, current_column_fuel, QStandardItem(str(record["num_fuel"]))
            )
            self.summary_by_column(current_column_fuel)

    def as_list(self) -> list:
        """
        Возвращает список из данных модели
        Каждый элемент списка является словарём типа:
        {
            'code_species': 71,
            'dmr': 32,
            'num_ind': 15,
            'num_fuel': 11
        }
        """
        list_from_model = []

        for col in range(self.columnCount()):  # Заходим в столбец
            if self.item(0, col) is not None:
                if getattr(self.item(0, col), "code_species") is not None:
                    #  Если это столбец с названием породы
                    code_species = getattr(self.item(0, col), "code_species")
                    for row in range(2, self.rowCount()):
                        # Заходим в строку (первые две строки не берём, т.к. это название породы и тип)
                        if self.item(row, col) or self.item(row, col + 1):
                            instance = {}
                            instance["code_species"] = code_species
                            instance["dmr"] = int(row * 4)
                            try:
                                instance["num_ind"] = self.item(row, col).text()
                                if instance["num_ind"] == "":
                                    raise AttributeError
                            except AttributeError:
                                instance["num_ind"] = "0"

                            try:
                                instance["num_fuel"] = self.item(row, col + 1).text()
                                if instance["num_fuel"] == "":
                                    raise AttributeError
                            except AttributeError:
                                instance["num_fuel"] = "0"
                            list_from_model.append(instance)

        return list_from_model

    def species_position(self, code_species: int = None) -> Union[int, None]:
        """
        Получаю позицию породы по коду породы или названию породы.
        Если же нет определенной породы - по отдаю словарь с кодами всех пород и их
        позициями в таблице
        """
        species_positions = {}
        for col in range(self.columnCount()):
            if self.item(0, col):
                if code_species is not None:
                    if getattr(self.item(0, col), "code_species") == code_species:
                        return col
                elif getattr(self.item(0, col), "code_species") is not None:
                    species_positions[getattr(self.item(0, col), "code_species")] = col

        if code_species is None:
            return species_positions
        return None

    def summary_by_column(self, column: int):
        """
        Подсчитываем количество деревьев по столбцу (по породе и годности)
        """
        first_row = 2  # 1 - порода, 2 - деловые\дровяные
        last_row = self.rowCount() - 1
        summary = 0
        for row in range(first_row, last_row):
            if self.item(row, column) and self.item(row, column).text() != "":
                summary += int(self.item(row, column).text())
        self.setItem(last_row, column, QStandardItem(str(summary)))
        self.item(last_row, column).setEditable(False)
