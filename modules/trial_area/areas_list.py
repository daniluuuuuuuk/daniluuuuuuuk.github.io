from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidgetItem

from .src.business import areas_list_main_window
from .src.models.nri import Organization


class AreasList(areas_list_main_window.MainWindow):
    """
    Главное окно для отображения таблицы всех пробных площадей на устройстве.
    В наследуемом классе устанавливаются дефолтные настройки для GUI.
    """

    def __init__(self):
        super().__init__()

        self.areas_data = AreasData()
        self.areas_data.all_areas.connect(
            self.render_areas_table, QtCore.Qt.QueuedConnection
        )

        self.import_data_from_db()

    def render_areas_table(self, all_areas: dict):

        self.tableWidget.setRowCount(len(all_areas))

        for area_number in range(len(all_areas)):
            for param_number in range(len(all_areas[area_number].keys())):
                value_data = all_areas[area_number][
                    list(all_areas[area_number].keys())[param_number]
                ]  # Значения параметра (прим.: Городищенское лесничество)
                self.tableWidget.setItem(
                    area_number, param_number, QTableWidgetItem(value_data),
                )

    def import_data_from_db(self):
        self.areas_data.run = self.areas_data.get_all_areas
        self.areas_data.start()


class AreasData(QtCore.QThread):
    all_areas = QtCore.pyqtSignal(list)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def get_all_areas(self):
        self.all_areas.emit(
            [
                {
                    "forestry": "Городищенский",
                    "compartment": "1",
                    "sub_compartment": "3,4",
                    "date": "2020.10.22",
                    "uuid": "2d1402e4-363b-4a1c-a4db-3a13c2733ba8",
                }
            ]
        )
