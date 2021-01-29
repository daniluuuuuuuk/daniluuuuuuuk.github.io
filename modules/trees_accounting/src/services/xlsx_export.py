from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QThread, pyqtSignal
from ..models.dictionary import Species
from ..services.config import BasicDir
from openpyxl import load_workbook


class XLSXExportedData(QThread):
    """
    ! Не обработаны ошибки
    Поток для сохранения данных в JSON для импорта в АРМ Лесопользование.
    """

    signal_message_result = pyqtSignal(dict)

    def __init__(self, att_data: dict, model: QStandardItemModel, export_file: str):
        QThread.__init__(self)
        self.att_data = att_data
        self.model = model
        self.export_file = export_file

    def write_trees_data(self, wb):
        """Добавляю данные в книгу Перечет"""
        species_name = {}
        ws = wb["Перечет"]
        instance_list = self.model.as_list()

        if type(instance_list) is list:
            for instance in instance_list:

                # Формула для получения номера столбца в xlsx для нужной породы,
                # а так же для (Деловых, Дровяных(Соответственно + 1)):
                # По 3 строке это будет название породы
                xlsx_column = self.model.species_position(instance["code_species"]) + 2
                if xlsx_column > 12:
                    xlsx_column += 1  # это будет новая страница

                # Формула для получения номера строки в xlsx для нужного диаметра:
                xlsx_row = self.model.row_number_by_dmr(instance["dmr"]) + 1

                # Получаю название породы по коду породы, если ещё не получал:
                if instance["code_species"] not in species_name.keys():
                    spc_name = Species.get(
                        Species.code_species == instance["code_species"]
                    ).name_species
                    species_name[instance["code_species"]] = spc_name
                    ws.cell(row=3, column=xlsx_column, value=spc_name)

                # Заношу значение в xlsx таблицу:
                if instance["num_ind"] != "0":
                    ws.cell(
                        row=xlsx_row, column=xlsx_column, value=int(instance["num_ind"])
                    )

                if instance["num_fuel"] != "0":
                    ws.cell(
                        row=xlsx_row,
                        column=xlsx_column + 1,
                        value=int(instance["num_fuel"]),
                    )

            return True
        instance_list["detailed_text"] = " "
        self.signal_message_result.emit(instance_list)
        return False

    def run(self):
        file = BasicDir.get_module_dir("templates/template_accounting.xlsx")
        workbook = load_workbook(file)

        if self.write_trees_data(wb=workbook):

            workbook.save(self.export_file)
            self.signal_message_result.emit(
                {
                    "main_text": "Данные успешно экспортированы в\n" + self.export_file,
                    "detailed_text": None,
                }
            )
