from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from typing import Union
from ..models.dictionary import Species


class TreesLiquid(QStandardItemModel):
    """
    Структура данных деловых и дровяных
    """

    def __init__(self):
        super().__init__()
        self.trf_height_row = 0  # Номер строки, где прописана разряд высот
        self.species_row = 1  # Номер строки, где прописана порода
        self.make_dmr()

    def make_dmr(self):
        """Строю диаметры для таблицы"""
        self.setVerticalHeaderItem(self.trf_height_row, QStandardItem("Разряд"))
        self.setVerticalHeaderItem(self.species_row, QStandardItem("Диаметр"))
        self.setVerticalHeaderItem(2, QStandardItem("см."))

        diameters = [dmr for dmr in range(8, 128, 4)]

        for dmr in diameters:
            row_number = self.row_number_by_dmr(dmr)
            self.setVerticalHeaderItem(row_number, QStandardItem(str(dmr)))
        self.setVerticalHeaderItem(self.rowCount(), QStandardItem("Сумма"))

    def add_new_species(self, code_species: int, name_species: str = None):
        last_column = self.columnCount()

        self.insertColumns(last_column, 2)

        if not name_species:
            name_species = Species.get(
                Species.code_species == code_species
            ).name_species

        self.setItem(self.species_row, last_column, QStandardItem(name_species))
        self.item(self.species_row, last_column).code_species = code_species
        self.item(self.species_row, last_column).setTextAlignment(Qt.AlignHCenter)
        self.item(self.species_row, last_column).setEditable(False)

        self.setItem(2, last_column, QStandardItem("Деловых"))
        self.item(2, last_column).setTextAlignment(Qt.AlignHCenter)
        self.item(2, last_column).setEditable(False)

        self.setItem(2, last_column + 1, QStandardItem("Дровяных"))
        self.item(2, last_column + 1).setTextAlignment(Qt.AlignHCenter)
        self.item(2, last_column + 1).setEditable(False)

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
        current_row = self.row_number_by_dmr(record["dmr"])

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

    def as_list(self) -> Union[list, dict]:
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
            if self.item(self.species_row, col) is not None:
                if (
                    getattr(self.item(self.species_row, col), "code_species")
                    is not None
                ):
                    #  Если это столбец с названием породы
                    code_species = getattr(
                        self.item(self.species_row, col), "code_species"
                    )
                    trf_height = getattr(
                        self.item(self.species_row, col),
                        "trf_height",
                    )
                    if trf_height == 0:
                        name_species = (
                            Species.select(Species.name_species)
                            .where(Species.code_species == code_species)
                            .get()
                            .name_species
                        )

                        return {
                            "main_text": f'Не выбраны разряд высот для породы "{name_species}"',
                            "detailed_text": None,
                        }
                    for row in range(3, self.rowCount() - 1):  # -1 это Сумма
                        # Заходим в строку (первые две строки не берём, т.к. это разряд высот, название породы, тип)
                        if self.item(row, col) or self.item(row, col + 1):
                            instance = {}
                            instance["code_species"] = code_species
                            instance["code_trf_height"] = trf_height
                            instance["dmr"] = int((row - 1) * 4)

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
            if self.item(self.species_row, col):
                if code_species is not None:
                    if (
                        getattr(self.item(self.species_row, col), "code_species")
                        == code_species
                    ):
                        return col
                elif (
                    getattr(self.item(self.species_row, col), "code_species")
                    is not None
                ):
                    species_positions[
                        getattr(self.item(self.species_row, col), "code_species")
                    ] = col

        if code_species is None:
            return species_positions
        return None

    def summary_by_column(self, column: int):
        """
        Подсчитываем количество деревьев по столбцу (по породе и годности)
        """
        first_row = 3  # 1 - разряд, 2 - порода, 3 - деловые\дровяные
        last_row = self.rowCount() - 1
        summary = 0
        for row in range(first_row, last_row):
            if self.item(row, column) and self.item(row, column).text() != "":
                summary += int(self.item(row, column).text())
        self.setItem(last_row, column, QStandardItem(str(summary)))
        self.item(last_row, column).setEditable(False)

    def row_number_by_dmr(self, dmr: int) -> int:
        """Расчёт строки для диаметра"""
        return int(dmr / 4) + 1

    def set_trf_for_spc(self, col: int, code_trf_height: int):
        """
        Добавляю значение разряда высот в ячейку породы
        (Невозможно добавить значение разряда пород в ячейку разряда пород,
        т.к. в ячейки находится виджет и ячейка "якобы" пустая)
        """
        if col >= 0:  # При импорте по умолчанию выбран столбец -1
            self.item(self.species_row, col).trf_height = code_trf_height
