import os
from datetime import date
from PyQt5 import QtWidgets, uic, QtCore

from ..tools.CuttingAreaList import CuttingAreaScrollList
from ..tools.CuttingAreaExport import CuttingAreaExport
from ..tools.CuttingAreaImport import CuttingAreaImport, SearchDuplicates
from ..tools.LayoutObjectsIterator import LayoutObjectsIterator
from ..util import resolvePath
from ..modules.trees_accounting.src.services.waiting_spinner_widget import (
    QtWaitingSpinner,
)

UI_EXPORT_IMPORT_CUTTING_AREAS = uic.loadUiType(
    resolvePath("ui\ExportImportCuttingAreas.ui")
)[0]


class ExportImportCuttingAreaWindow(
    QtWidgets.QDialog, UI_EXPORT_IMPORT_CUTTING_AREAS
):
    def __init__(self, selected_cutting_areas, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.spinner = QtWaitingSpinner(
            self, True, True, QtCore.Qt.ApplicationModal
        )

        self.cutting_area_scroll_list = CuttingAreaScrollList(
            selected_cutting_areas
        )
        self.cutting_areas_container = (
            self.cutting_area_scroll_list.cutting_areas_container
        )
        self.verticalLayout_4.addWidget(self.cutting_area_scroll_list)

        self.checkBox.clicked.connect(self.select_all_cutting_areas)
        self.pushButton.clicked.connect(self.import_cutting_areas)
        self.pushButton_2.clicked.connect(
            lambda: self.export_cutting_areas("json")
        )
        self.pushButton_3.clicked.connect(
            lambda: self.export_cutting_areas("xlsx")
        )
        self.pushButton_4.clicked.connect(
            lambda: self.export_cutting_areas("shp")
        )
        self.toolButton.clicked.connect(self.select_file_to_import)

        self.add_event_to_areas_cb()

        if selected_cutting_areas:
            self.checkBox.setChecked(False)

    def select_file_to_import(self):
        import_file = QtWidgets.QFileDialog.getOpenFileName(
            caption="Импорт файла",
            directory=os.path.expanduser("~") + "/Documents/",
            filter="JSON (*.json)",
        )[0]
        if import_file:
            self.lineEdit.setText(import_file)

    def export_cutting_areas(self, file_extension):
        """
        Экспорт выбранных лесосек
        """
        if self.cutting_area_scroll_list.selected_areas_uuid == []:
            QtWidgets.QMessageBox.information(
                None, "", "Отсутствуют лесосеки для экспорта."
            )
            return False

        export_file = QtWidgets.QFileDialog.getSaveFileName(
            caption="Сохранение файла",
            directory=os.path.expanduser("~")
            + "/Documents/Экспорт_лесосек_"
            + date.today().strftime("%Y-%m-%d")
            + f".{file_extension}",
            filter=f"{file_extension.upper()} (*.{file_extension})",
        )
        if export_file[0]:
            self.cutting_area_export = CuttingAreaExport(
                uuid_list=self.cutting_area_scroll_list.selected_areas_uuid,
                path_to_file=export_file[0],
                file_extension=file_extension,
            )
            self.cutting_area_export.started.connect(
                lambda: self.spinner.start()
            )
            self.cutting_area_export.finished.connect(
                lambda: self.spinner.stop()
            )
            self.cutting_area_export.start()
            self.cutting_area_export.signal_message_result.connect(
                lambda mes: QtWidgets.QMessageBox.information(
                    None, "", str(mes)
                ),
                QtCore.Qt.QueuedConnection,
            )

    def check_imported_cutting_areas(meth):
        def wrapper(self, duplicated_uuid):
            if self.lineEdit.text():
                self.check_import = SearchDuplicates(
                    path_to_file=self.lineEdit.text()
                )
                self.check_import.started.connect(lambda: self.spinner.start())
                self.check_import.finished.connect(lambda: self.spinner.stop())
                self.check_import.start()
                self.check_import.signal_data_result.connect(
                    lambda duplicated_cutting_areas: meth(
                        self,
                        duplicated_cutting_areas,
                        self.check_import.uuid_in_db,
                    ),
                    QtCore.Qt.QueuedConnection,
                )
            else:
                QtWidgets.QMessageBox.critical(
                    None, "", "Выберите файл для импорта."
                )

        return wrapper

    @check_imported_cutting_areas
    def import_cutting_areas(
        self,
        duplicated_cutting_areas=False,
        duplicated_cutting_areas_uuid=False,
    ):
        action_code = 3
        if duplicated_cutting_areas:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msgBox.setText(
                "Данные о текущих лесосеках уже присутствуют в базе данных, выберите действие:"
            )
            msgBox.setDetailedText(duplicated_cutting_areas)
            msgBox.addButton(
                "Заменить все", QtWidgets.QMessageBox.YesRole
            )  # 0
            msgBox.addButton(
                "Пропустить все",
                QtWidgets.QMessageBox.NoRole,
            )  # 1
            msgBox.addButton(
                "Отменить импорт", QtWidgets.QMessageBox.RejectRole
            )  # 2
            action_code = msgBox.exec_()
            if action_code == 2:
                return False

        self.cutting_area_import = CuttingAreaImport(
            path_to_file=self.lineEdit.text(),
            action_code=action_code,
            competitors_list=duplicated_cutting_areas_uuid,
        )
        self.cutting_area_import.started.connect(lambda: self.spinner.start())
        self.cutting_area_import.finished.connect(lambda: self.spinner.stop())
        self.cutting_area_import.start()
        self.cutting_area_import.signal_message_result.connect(
            lambda mes: QtWidgets.QMessageBox.information(None, "", str(mes)),
            QtCore.Qt.QueuedConnection,
        )

    def add_event_to_areas_cb(self):
        self.cb_areas_clicked_event()
        for cutting_area_cb in LayoutObjectsIterator(
            layout=self.cutting_areas_container
        ):
            cutting_area_cb.clicked.connect(
                lambda: self.cb_areas_clicked_event(
                    status=cutting_area_cb.isChecked()
                )
            )

    def cb_areas_clicked_event(self, status=None):
        if status is False:
            self.checkBox.setChecked(False)
        self.verticalGroupBox.setTitle(
            f"Экспорт ({len(self.cutting_area_scroll_list.selected_areas_uuid)})"
        )

    def select_all_cutting_areas(self):
        """
        Выбрать все лесосеки
        """
        is_all_selected = self.checkBox.isChecked()

        for cutting_area_cb in LayoutObjectsIterator(
            layout=self.cutting_areas_container
        ):
            cutting_area_cb.setChecked(is_all_selected)

        self.cb_areas_clicked_event()
