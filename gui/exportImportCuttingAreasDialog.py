import os
from datetime import date
from PyQt5 import QtWidgets, uic, QtCore

from ..tools.CuttingAreaList import CuttingAreaScrollList
from ..tools.CuttingAreaExport import CuttingAreaExport
from ..tools.CuttingAreaImport import CuttingAreaImport
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
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cutting_area_scroll_list = CuttingAreaScrollList()
        self.cutting_areas_container = (
            self.cutting_area_scroll_list.cutting_areas_container
        )
        self.verticalLayout_4.addWidget(self.cutting_area_scroll_list)

        self.checkBox.clicked.connect(self.select_all_cutting_areas)
        self.pushButton.clicked.connect(self.import_cutting_areas)
        self.pushButton_2.clicked.connect(self.export_cutting_areas)
        self.toolButton.clicked.connect(self.select_file_to_import)

        self.spinner = QtWaitingSpinner(
            self, True, True, QtCore.Qt.ApplicationModal
        )

    def select_file_to_import(self):
        import_file = QtWidgets.QFileDialog.getOpenFileName(
            caption="Импорт файла",
            directory=os.path.expanduser("~") + "/Documents/",
            filter="JSON (*.json)",
        )[0]
        if import_file:
            self.lineEdit.setText(import_file)

    def export_cutting_areas(self):
        """
        Экспорт выбранных лесосек
        """
        export_file = QtWidgets.QFileDialog.getSaveFileName(
            caption="Сохранение файла",
            directory=os.path.expanduser("~")
            + "/Documents/Экспорт_лесосек_"
            + date.today().strftime("%Y-%m-%d")
            + ".json",
            filter="JSON (*.json)",
        )
        if export_file[0]:
            self.cutting_area_export = CuttingAreaExport(
                uuid_list=self.cutting_area_scroll_list.selected_areas_uuid,
                path_to_file=export_file[0],
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

    def import_cutting_areas(self):
        if self.lineEdit.text():
            self.cutting_area_import = CuttingAreaImport(
                path_to_file=self.lineEdit.text(),
            )
            self.cutting_area_import.started.connect(
                lambda: self.spinner.start()
            )
            self.cutting_area_import.finished.connect(
                lambda: self.spinner.stop()
            )
            self.cutting_area_import.start()
            self.cutting_area_import.signal_message_result.connect(
                lambda mes: QtWidgets.QMessageBox.information(
                    None, "", str(mes)
                ),
                QtCore.Qt.QueuedConnection,
            )
        else:
            QtWidgets.QMessageBox.critical(
                None, "", "Выберите файл для импорта."
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
