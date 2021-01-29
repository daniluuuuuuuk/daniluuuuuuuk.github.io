import os
import platform
import subprocess
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QIcon
from .services.config import BasicDir, Config
from .services.db_import import ImportedData
from .services.db_export import DBExportedData
from .services.lp_export import LPExportedData
from .services.xlsx_export import XLSXExportedData
from .models.trees_liquid import TreesLiquid
from .models.dictionary import Species, TrfHeight

UI_MAINWINDOW = uic.loadUiType(BasicDir.get_module_dir("ui/trees_accounting.ui"))[0]
UI_SPECIES = uic.loadUiType(BasicDir.get_module_dir("ui/select_species.ui"))[0]


class TaMainWindow(QtWidgets.QMainWindow, UI_MAINWINDOW):
    """
    Главное окно программы
    """

    def __init__(self, uuid, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.uuid = uuid

        self.config = Config()
        self.trees_liquid = TreesLiquid()

        self.message = InformativeMessage(self)

        self.db_import()

        self.was_edited = False

        self.origin_closeEditor = self.tableView.closeEditor
        self.tableView.closeEditor = self.closeEditor

        self.action.triggered.connect(self.lp_export)
        self.action.setIcon(QIcon(BasicDir.get_module_dir("img/lp.png")))
        self.action_XLSX.triggered.connect(self.xls_export)
        self.action_XLSX.setIcon(QIcon(BasicDir.get_module_dir("img/xls.png")))

        self.pushButton.clicked.connect(self.db_export)
        self.pushButton_2.clicked.connect(self.add_gui_species)
        self.pushButton_3.clicked.connect(self.delete_gui_species)

    def db_import(self):
        self.imported_data = ImportedData(self.uuid)
        self.imported_data.start()
        self.imported_data.signal_get_trees_data.connect(
            self.set_trees_data, QtCore.Qt.QueuedConnection
        )
        self.imported_data.signal_get_att_data.connect(
            self.set_att_data, QtCore.Qt.QueuedConnection
        )

    def set_trees_data(self, model):
        """Применяю модель"""
        self.trees_liquid = model
        self.tableView.setModel(self.trees_liquid)

        """Объединяю столбцы с заголовками пород"""
        for col in range(self.trees_liquid.columnCount()):
            if not col % 2:  # используем нечётные столбцы (именно там уст. наз. породы)
                self.tableView.setSpan(0, col, 1, 2)
                self.tableView.setSpan(self.trees_liquid.species_row, col, 1, 2)
                self.tableView.setIndexWidget(
                    self.trees_liquid.index(0, col),
                    self.create_trf_widget(),
                )
                #  Ставлю разряд высот
                current_trf_height = (
                    self.tableView.model()
                    .item(self.trees_liquid.species_row, col)
                    .trf_height
                )
                self.tableView.indexWidget(
                    self.tableView.model().index(0, col)
                ).setCurrentIndex(current_trf_height)
        self.statusBar().showMessage("Данные успешно загружены из БД", 3000)

    def set_att_data(self, att_data: dict):
        self.att_data = att_data
        """Рендерим атрибутивные данные"""
        uuid = att_data["uuid"]
        self.label_3.setText(att_data["leshos_text"])
        self.label_3.setToolTip(att_data["leshos_text"])

        self.label_4.setText(att_data["lesnich_text"])
        self.label_4.setToolTip(att_data["lesnich_text"])

        self.label_14.setText(att_data["compartment"])
        self.label_14.setToolTip(att_data["compartment"])

        self.label.setText(att_data["sub_compartment"])
        self.label.setToolTip(att_data["sub_compartment"])

        self.label_15.setText(att_data["area"])
        self.label_15.setToolTip(att_data["area"])

        self.label_16.setText(att_data["num_cutting_area"])
        self.label_16.setToolTip(att_data["num_cutting_area"])

        self.label_17.setText(att_data["person_name"])
        self.label_17.setToolTip(att_data["person_name"])

        self.label_18.setText(att_data["date_trial"])
        self.label_18.setToolTip(att_data["date_trial"])

        self.label_12.setText(att_data["description"])
        self.label_12.setToolTip(att_data["description"])

        self.label_5.setText(att_data["use_type"])
        self.label_5.setToolTip(att_data["use_type"])

        self.label_10.setText(att_data["cutting_type"])
        self.label_10.setToolTip(att_data["cutting_type"])

        self.statusBar().showMessage(f"UUID лесосеки: {uuid}", 3000)

    def db_export(self):
        #!
        # print(
        #     self.tableView.indexWidget(self.tableView.model().index(0, 0)).currentText()
        # )
        self.exported_data = DBExportedData(self.uuid, self.tableView.model())
        self.exported_data.start()
        self.exported_data.signal_message_result.connect(
            lambda messages: self.message.show(**messages), QtCore.Qt.QueuedConnection
        )
        self.was_edited = False

    def lp_export(self):
        if self.tableView.model().columnCount() > 1:
            export_file = QtWidgets.QFileDialog.getSaveFileName(
                caption="Сохранение файла",
                directory=os.path.expanduser("~") + "/Documents/" + self.uuid + ".json",
                filter="JSON (*.json)",
            )
            if export_file[0]:
                self.lp_exported_data = LPExportedData(
                    self.att_data, self.tableView.model(), export_file[0]
                )
                self.lp_exported_data.start()
                self.lp_exported_data.signal_message_result.connect(
                    lambda messages: self.message.show(**messages),
                    QtCore.Qt.QueuedConnection,
                )

    def xls_export(self):
        if self.tableView.model().columnCount() > 1:
            export_file = QtWidgets.QFileDialog.getSaveFileName(
                caption="Сохранение файла",
                directory=os.path.expanduser("~") + "/Documents/" + self.uuid + ".xlsx",
                filter="XLS (*.xlsx)",
            )
            if export_file[0]:
                self.xlsx_exported_data = XLSXExportedData(
                    self.att_data, self.tableView.model(), export_file[0]
                )
                self.xlsx_exported_data.start()
                self.xlsx_exported_data.signal_message_result.connect(
                    lambda messages: self.xls_export_on_finish(
                        message=messages, export_file=export_file[0]
                    ),
                    QtCore.Qt.QueuedConnection,
                )

    def xls_export_on_finish(self, message: dict, export_file: str):
        """
        Метод запускается после экспорта в XLSX
        """
        if message["detailed_text"] is None:
            result = QtWidgets.QMessageBox.information(
                self,
                self.windowTitle(),
                message["main_text"],
                buttons=QtWidgets.QMessageBox.Open | QtWidgets.QMessageBox.Close,
            )
            if result == 8192:  # 8192 - вес кнопки (Открыть)
                if platform.system() == "Windows":
                    os.startfile(export_file)
                else:
                    subprocess.call(("xdg-open", export_file))
        else:
            self.message.show(**message)

    def add_gui_species(self):
        """
        Вызов окна с выбором породы для добавления
        """
        modal_window_select_species = TaSelectSpecies()

        if modal_window_select_species.exec():
            self.trees_liquid = self.tableView.model()

            if (
                self.trees_liquid.species_position(
                    modal_window_select_species.code_species
                )
                is None
            ):

                self.trees_liquid.add_new_species(
                    code_species=modal_window_select_species.code_species,
                    name_species=modal_window_select_species.name_species,
                )

                column_with_last_species = self.trees_liquid.columnCount() - 2

                self.tableView.setSpan(0, column_with_last_species, 1, 2)  # Разряд
                self.tableView.setSpan(
                    self.trees_liquid.species_row, column_with_last_species, 1, 2
                )  # Назв породы
                self.tableView.setIndexWidget(
                    self.trees_liquid.index(0, column_with_last_species),
                    self.create_trf_widget(),
                )
                self.tableView.model().set_trf_for_spc(column_with_last_species, 0)
                # self.tableView.indexWidget(
                #     self.trees_liquid.index(0, column_with_last_species)
                # ).setCurrentIndex(0)

            else:
                QtWidgets.QMessageBox.warning(
                    self, "Внимание", "Данная порода уже присутствует в таблице"
                )

    def delete_gui_species(self):
        """
        Вызов окна с выбором породы для удаления
        """

        def fill_species():
            for code_spc in self.tableView.model().species_position().keys():
                name_species = Species.get(
                    Species.code_species == code_spc
                ).name_species
                modal_window_select_species.comboBox.addItem(
                    name_species, userData=QtCore.QVariant(code_spc)
                )

        modal_window_select_species = TaSelectSpecies()
        modal_window_select_species.fill_species = fill_species
        modal_window_select_species.setWindowTitle("Удаление породы")
        if modal_window_select_species.exec():
            self.trees_liquid.del_species(modal_window_select_species.code_species)

    def create_trf_widget(self) -> QtWidgets.QComboBox:
        """Возвращает combobox для разряда высот"""
        cb = TrfHeightComboBox()
        cb.currentIndexChanged.connect(
            lambda code_trf_height: self.tableView.model().set_trf_for_spc(
                self.tableView.currentIndex().column(), code_trf_height
            )
        )
        return cb

    def closeEditor(self, widget, hint):
        """Метод вызывается при окончании редактирования ячейки в таблице"""
        if widget.text() != "":
            self.was_edited = True
            try:
                int(widget.text())
                self.tableView.model().summary_by_column(
                    self.tableView.currentIndex().column()
                )
            except ValueError:
                self.message.show(
                    main_text="Ошибка вводимых данных. Введите целочисленное значение."
                )
        self.origin_closeEditor(widget, hint)

    def closeEvent(self, event):
        if self.was_edited:
            result = QtWidgets.QMessageBox.information(
                self,
                self.windowTitle(),
                "Некоторые данные были изменены. Вы хотите сохранить изменения?",
                buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            )
            if result == 16384:
                event.ignore()
                self.db_export()
                self.was_edited = False


class TaSelectSpecies(QtWidgets.QDialog, UI_SPECIES):
    """
    GUI для выбора породы при добавлении породы
    """

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

    def fill_species(self):
        """
        Заполняю выпадающий список породами
        """
        for spc in Species.select(Species.code_species, Species.name_species).order_by(
            Species.name_species
        ):
            self.comboBox.addItem(
                spc.name_species, userData=QtCore.QVariant(spc.code_species)
            )

    def accept(self):
        self.name_species = self.comboBox.itemText(self.comboBox.currentIndex())
        self.code_species = self.comboBox.itemData(self.comboBox.currentIndex())
        super().accept()

    def exec(self):
        self.fill_species()
        return super().exec()


class InformativeMessage(QtWidgets.QMessageBox):
    def __init__(self, main_window):
        super().__init__()
        self.setIcon(QtWidgets.QMessageBox.Warning)
        self.setWindowTitle(main_window.windowTitle())

    def show(self, main_text: str, detailed_text: str = None):
        self.setText(str(main_text))
        if detailed_text:
            self.setDetailedText(str(detailed_text))
        super().show()


class TrfHeightComboBox(QtWidgets.QComboBox):
    def __init__(self):
        """
        Кастомный QComboBox для разряда высот
        """
        super().__init__()
        self.set_possible_trf_height()

    def set_possible_trf_height(self):
        """
        Добавляю все возможные разряды высот в comboBox
        """
        self.addItem("", 0)

        possible_trf_height = {}
        for trf in TrfHeight.select():
            self.addItem(trf.name_trf_height, trf.code_trf_height)

        return possible_trf_height
