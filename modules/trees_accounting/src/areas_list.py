from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QApplication

from .services import areas_list_main_window
from .models.nri import Organization
from .models.restatement import Trees
from .models.public import Area
from .restatements import Restatement, AreaProperty


class AreasList(areas_list_main_window.MainWindow):
    """
    Главное окно для отображения таблицы всех пробных площадей на устройстве.
    В наследуемом классе устанавливаются дефолтные настройки для GUI.
    """

    def __init__(self):
        super().__init__()

        self.last_column = self.tableWidget.columnCount() - 1

        self.tableWidget.doubleClicked.connect(self.open_selected_area)

        self.pushButton.clicked.connect(self.add_area)
        self.pushButton_2.clicked.connect(self.delete_areas)
        self.pushButton_3.clicked.connect(self.import_data_from_db)

        self.areas_data = AreasData()
        self.areas_data.all_areas.connect(
            self.render_areas_table, QtCore.Qt.QueuedConnection
        )

        self.import_data_from_db()

    def render_areas_table(self, all_areas: tuple):
        self.tableWidget.setRowCount(len(all_areas))

        for area_number in range(len(all_areas)):
            for param_number in range(len(all_areas[area_number].keys())):
                value_data = all_areas[area_number][
                    list(all_areas[area_number].keys())[param_number]
                ]  # Значения параметра (прим.: Городищенское лесничество)
                self.tableWidget.setItem(
                    area_number, param_number, QTableWidgetItem(value_data),
                )
        QApplication.restoreOverrideCursor()

    def import_data_from_db(self):

        QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)
        self.areas_data.run = self.areas_data.get_all_areas
        self.areas_data.start()

    def open_selected_area(self):
        current_uuid = self.tableWidget.item(
            self.tableWidget.currentRow(), self.last_column
        ).text()
        self.one_area = Restatement(current_uuid)
        self.one_area.show()

    def add_area(self):
        self.one_new_area = AreaProperty()
        self.one_new_area.show()

    def delete_areas(self):
        uuid_areas_for_delete = []
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        for row in selected_rows:
            uuid_areas_for_delete.append(
                self.tableWidget.item(row.row(), self.last_column).text()
            )

        buttonReply = QtWidgets.QMessageBox.question(
            self,
            "Удаление пробных площадей",
            "Удалить выбранные пробные площади?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )
        if buttonReply == QtWidgets.QMessageBox.Yes:
            for area_uuid in uuid_areas_for_delete:
                Trees.delete().where(Trees.area_uuid == area_uuid).execute()
                Area.delete().where(Area.uuid == area_uuid).execute()

            self.import_data_from_db()


class AreasData(QtCore.QThread):
    all_areas = QtCore.pyqtSignal(tuple)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def get_all_areas(self):
        """Получаю данные всех пробных площадей на устройстве"""
        org = Organization()
        all_areas_db = Area.select(
            Area.uuid,
            Area.num_forestry,
            Area.num_enterprise,
            Area.compartment,
            Area.sub_compartment,
            Area.date_trial,
            Area.area,
        )
        all_areas_data = []

        for _area in all_areas_db:
            full_organization_name = org.convert_org_id(
                id_forestry=int(_area.num_forestry),
                id_forestry_enterprise=int(_area.num_enterprise),
            )
            area_data = {
                "enterprise": full_organization_name[1],
                "forestry": full_organization_name[2],
                "compartment": str(_area.compartment),
                "sub_compartment": str(_area.sub_compartment),
                "date": _area.date_trial,
                "area": str(_area.area),
                "uuid": _area.uuid,
            }
            all_areas_data.append(area_data)

        self.all_areas.emit(tuple(all_areas_data))
