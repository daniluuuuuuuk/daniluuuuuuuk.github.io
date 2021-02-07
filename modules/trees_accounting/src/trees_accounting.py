import os
import platform
import subprocess
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QIcon, QStandardItemModel
from .services.config import BasicDir, Config
from .services.db_import import ImportedData
from .services.db_export import DBExportedData
from .services.lp_export import LPExportedData
from .services.xlsx_export import XLSXExportedData
from .models.trees_liquid import TreesLiquid
from .models.trees_not_cutting import TreesNotCutting
from .models.dictionary import Species, TrfHeight, KindSeeds
from .services.waiting_spinner_widget import QtWaitingSpinner

UI_MAINWINDOW = uic.loadUiType(BasicDir.get_module_dir("ui/trees_accounting.ui"))[0]
UI_LIQUID_SPECIES = uic.loadUiType(
    BasicDir.get_module_dir("ui/select_liquid_species.ui")
)[0]
UI_NOT_CUTTING_SPECIES = uic.loadUiType(
    BasicDir.get_module_dir("ui/select_not_cutting_species.ui")
)[0]


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
        self.pushButton_4.clicked.connect(self.add_gui_not_cutting_species)
        self.pushButton_5.clicked.connect(self.delete_gui_liquid_species)
        self.pushButton_6.clicked.connect(self.add_gui_liquid_species)
        self.pushButton_7.clicked.connect(self.delete_gui_not_cutting_species)

        self.tableView_2.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.tableView_2.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.tableView_2.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView_2.doubleClicked.connect(self.edit_not_cutting_row)

        self.spinner = QtWaitingSpinner(self, True, True, QtCore.Qt.ApplicationModal)

    def db_import(self):
        """
        Метод запуска потока для импорта данных из БД
        """
        self.imported_data = ImportedData(self.uuid)
        self.imported_data.start()
        self.imported_data.started.connect(lambda: self.spinner.start())
        self.imported_data.finished.connect(lambda: self.spinner.stop())
        self.imported_data.signal_get_trees_data.connect(
            self.set_trees_liquid_data, QtCore.Qt.QueuedConnection
        )
        self.imported_data.signal_get_att_data.connect(
            self.set_att_data, QtCore.Qt.QueuedConnection
        )
        self.imported_data.signal_get_not_cutting_trees_data.connect(
            lambda x: self.tableView_2.setModel(x), QtCore.Qt.QueuedConnection
        )

    def set_trees_liquid_data(self, model: QStandardItemModel):
        """
        Метод для установки данных в таблицу "Ведомость перечета деревьев".
        Применяется модель.
        Форматируется таблица (объединяются столбцы с заголовками пород).
        Выставляется разряд высот.
        """
        self.trees_liquid = model
        self.tableView.setModel(self.trees_liquid)

        for col in range(self.trees_liquid.columnCount()):
            if not col % 2:  # используем нечётные столбцы (именно там уст. наз. породы)
                self.formatting_trees_liquid_table(col)
                #  Ставлю разряд высот
                current_trf_height = (
                    self.tableView.model()
                    .item(self.trees_liquid.species_row, col)
                    .trf_height
                )
                self.tableView.indexWidget(
                    self.tableView.model().index(self.trees_liquid.trf_height_row, col)
                ).setCurrentIndex(current_trf_height)
        self.statusBar().showMessage("Данные успешно загружены из БД", 3000)

    def set_att_data(self, att_data: dict):
        """
        Метод для установки второстипенных данных в шапку программы,
        а так же всплывающие подсказки.
        Используемые данные:
            >>>leshos_text  -> Название лесхоза
            >>>lesnich_text -> Название лесничества
            >>>compartment  -> Квартал
            >>>sub_compartment  -> Выдел(а)
            >>>area -> Площадь лесосеки
            >>>num_cutting_area -> Номер лесосеки
            >>>person_name  -> ФИО
            >>>date_trial   -> Дата отвода
            >>>description  -> Дополнительные сведения
            >>>use_type -> Пользование
            >>>cutting_type -> Вид рубки
        """
        self.att_data = att_data

        uuid = att_data["uuid"]
        self.label_4.setText(att_data["leshos_text"])
        self.label_4.setToolTip(att_data["leshos_text"])

        self.label_3.setText(att_data["lesnich_text"])
        self.label_3.setToolTip(att_data["lesnich_text"])

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

    def formatting_trees_liquid_table(self, required_column: int) -> bool:
        """
        Форматирует таблицу "Ведомость перечета деревьев".
        Объединяет столбцы для:
            разряда высот TreesLiquid().trf_height_row
            названия породы TreesLiquid().species_row
        Создаёт виджет для выбора разряда высот.
        """
        self.tableView.setSpan(self.trees_liquid.trf_height_row, required_column, 1, 2)
        self.tableView.setSpan(self.trees_liquid.species_row, required_column, 1, 2)
        self.tableView.setIndexWidget(
            self.trees_liquid.index(self.trees_liquid.trf_height_row, required_column),
            self.create_trf_widget(),
        )
        return True

    def db_export(self):
        """
        Метод запуска потока для экспорта данных в БД
        """
        self.exported_data = DBExportedData(
            uuid=self.uuid,
            model_liquid=self.tableView.model(),
            model_not_cutting=self.tableView_2.model(),
        )
        self.exported_data.started.connect(lambda: self.spinner.start())
        self.exported_data.finished.connect(lambda: self.spinner.stop())
        self.exported_data.start()
        self.exported_data.signal_message_result.connect(
            lambda messages: self.message.show(**messages), QtCore.Qt.QueuedConnection
        )
        self.was_edited = False

    def lp_export(self):
        """
        Метод запуска потока для экспорта данных в АРМ Лесопользование 3.

        Проверяет добавлены ли данные в таблицу "Ведомость перечета деревьев".
        Вызывает окно с выбором пути и названием файла для экспорта.
        """
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
                self.lp_exported_data.started.connect(lambda: self.spinner.start())
                self.lp_exported_data.finished.connect(lambda: self.spinner.stop())
                self.lp_exported_data.start()
                self.lp_exported_data.signal_message_result.connect(
                    lambda messages: self.message.show(**messages),
                    QtCore.Qt.QueuedConnection,
                )

    def xls_export(self):
        """
        Метод запуска потока для экспорта данных в Excel (xlsx).

        Проверяет добавлены ли данные в таблицу "Ведомость перечета деревьев".
        Вызывает окно с выбором пути и названием файла для экспорта.
        """
        if self.tableView.model().columnCount() > 1:
            export_file = QtWidgets.QFileDialog.getSaveFileName(
                caption="Сохранение файла",
                directory=os.path.expanduser("~") + "/Documents/" + self.uuid + ".xlsx",
                filter="XLS (*.xlsx)",
            )
            if export_file[0]:
                self.xlsx_exported_data = XLSXExportedData(
                    self.att_data,
                    self.tableView.model(),
                    self.tableView_2.model(),
                    export_file[0],
                )
                self.xlsx_exported_data.started.connect(lambda: self.spinner.start())
                self.xlsx_exported_data.finished.connect(lambda: self.spinner.stop())
                self.xlsx_exported_data.start()
                self.xlsx_exported_data.signal_message_result.connect(
                    lambda messages: self.xls_export_on_finish(
                        message=messages, export_file=export_file[0]
                    ),
                    QtCore.Qt.QueuedConnection,
                )

    def xls_export_on_finish(self, message: dict, export_file: str):
        """
        Метод запускается после экспорта в XLSX.
        Вызывает окно с возможностью открытия экспортируемого файла.
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

    def add_gui_liquid_species(self):
        """
        Вызывает окно с выбором породы для добавления в таблицу "Ведомость перечета деревьев".
        """
        modal_window_select_species = TaSelectLiquidSpecies()

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

                self.formatting_trees_liquid_table(column_with_last_species)
                self.tableView.model().set_trf_for_spc(column_with_last_species, 0)

            else:
                QtWidgets.QMessageBox.warning(
                    self, "Внимание", "Данная порода уже присутствует в таблице"
                )

    def add_gui_not_cutting_species(self):
        """
        Вызывает окно с выбором породы для добавления в таблицу "Рубке не подлежат".
        """
        modal_select_not_cutting_spc = TaSelectNotCuttingSpecies(
            list(self.tableView.model().species_position().keys())
        )

        if modal_select_not_cutting_spc.exec():
            self.tableView_2.model().add_record(
                {
                    "code_species": modal_select_not_cutting_spc.code_species,
                    "name_species": modal_select_not_cutting_spc.name_species,
                    "seed_type_code": modal_select_not_cutting_spc.seed_type_code,
                    "name_kind_seeds": modal_select_not_cutting_spc.name_kind_seeds,
                    "seed_dmr": modal_select_not_cutting_spc.seed_dmr,
                    "seed_count": modal_select_not_cutting_spc.seed_count,
                    "seed_number": modal_select_not_cutting_spc.seed_number,
                }
            )
            self.was_edited = True

    def delete_gui_liquid_species(self):
        """
        Удаление выделенной породы из таблицы "Ведомость перечета деревьев"
        """
        current_col = self.tableView.currentIndex().column()
        try:
            code_spc = self.tableView.model().item(1, current_col).code_species
            name_spc = self.tableView.model().item(1, current_col).text()
        except AttributeError:
            try:
                code_spc = self.tableView.model().item(1, current_col - 1).code_species
                name_spc = self.tableView.model().item(1, current_col - 1).text()
            except AttributeError:
                QtWidgets.QMessageBox.critical(
                    self, "Ошибка", "Выберите породу в таблице для удаления"
                )
                return False
        result = QtWidgets.QMessageBox.question(
            self,
            "Внимание",
            f"Вы действительно хотите удалить выбранную породу: {name_spc}?",
            buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Yes,
            defaultButton=QtWidgets.QMessageBox.No,
        )
        if result == 16384:
            self.trees_liquid.del_species(code_spc)
            self.was_edited = True

    def delete_gui_not_cutting_species(self) -> bool:
        """
        Удаление выделенной строки из таблицы "Ведомость перечета деревьев".
        """
        current_row = self.tableView_2.currentIndex().row()
        if current_row < 0:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Выберите строку с записью.")
            return False
        self.tableView_2.model().takeRow(current_row)
        self.was_edited = True

    def create_trf_widget(self) -> QtWidgets.QComboBox:
        """
        Создание экземпляра класса для выбора разряда высот.
        Устанавливает сигнал, который при изменении значения в comboBox
        устанавливает новое значение разряда высот в ячейку с названием породы
        (Невозможно добавить значение разряда пород в ячейку разряда высот,
        т.к. в ячейки находится виджет и ячейка "якобы" пустая)
        """
        cb = TrfHeightComboBox()
        cb.currentIndexChanged.connect(
            lambda code_trf_height: self.tableView.model().set_trf_for_spc(
                self.tableView.currentIndex().column(), code_trf_height
            )
        )
        return cb

    def edit_not_cutting_row(self):
        """
        Вызывает окно с редактированием записи таблицы "Рубке не подлежат".
        """
        current_row = self.tableView_2.currentIndex().row()
        not_cutting_data = self.tableView_2.model().as_list()
        available_species = list(self.tableView.model().species_position().keys())

        if type(not_cutting_data) is list:
            not_cutting_row_data = not_cutting_data[current_row]
        else:
            self.message(not_cutting_data)
            return False

        modal_select_not_cutting_spc = TaSelectNotCuttingSpecies(
            available_species, not_cutting_row_data
        )

        if modal_select_not_cutting_spc.exec():
            self.tableView_2.model().add_record(
                {
                    "code_species": modal_select_not_cutting_spc.code_species,
                    "name_species": modal_select_not_cutting_spc.name_species,
                    "seed_type_code": modal_select_not_cutting_spc.seed_type_code,
                    "name_kind_seeds": modal_select_not_cutting_spc.name_kind_seeds,
                    "seed_dmr": modal_select_not_cutting_spc.seed_dmr,
                    "seed_count": modal_select_not_cutting_spc.seed_count,
                    "seed_number": modal_select_not_cutting_spc.seed_number,
                },
                current_row,
            )
            self.was_edited = True

    def closeEditor(self, widget, hint):
        """
        Проверка значения, которое вводится в таблицу "Ведомость перечета деревьев".
        Метод вызывается при окончании редактирования ячейки в таблице.
        """
        if widget.text() != "":
            self.was_edited = True
            try:
                if int(widget.text()) < 1 or int(widget.text()) > 2147483648:
                    raise ValueError

                self.tableView.model().summary_by_column(
                    self.tableView.currentIndex().column()
                )
            except ValueError:
                self.message.show(
                    main_text="Ошибка вводимых данных. Введите целочисленное значение (больше 0 и меньше 2147483648)."
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


class TaSelectLiquidSpecies(QtWidgets.QDialog, UI_LIQUID_SPECIES):
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


class TaSelectNotCuttingSpecies(QtWidgets.QDialog, UI_NOT_CUTTING_SPECIES):
    """
    GUI для выбора породы при добавлении/изменении записи
    """

    def __init__(self, current_spc: list, current_data: dict = None, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.current_spc = current_spc
        self.current_data = current_data

        self.setupUi(self)

    def fill_species(self):
        """
        Заполняю выпадающий список породами
        """
        for spc in (
            Species.select(Species.code_species, Species.name_species)
            .where(Species.code_species << self.current_spc)
            .order_by(Species.name_species)
        ):
            self.comboBox.addItem(
                spc.name_species, userData=QtCore.QVariant(spc.code_species)
            )

    def fill_kind_seeds(self):
        """Заполняю combobox видами семенников"""
        for kind_seed in KindSeeds.select(
            KindSeeds.code_kind_seeds, KindSeeds.name_kind_seeds
        ).order_by(KindSeeds.name_kind_seeds):
            self.comboBox_2.addItem(
                kind_seed.name_kind_seeds,
                userData=QtCore.QVariant(kind_seed.code_kind_seeds),
            )

    def seeds_field_validation(self) -> bool:
        """Валидация вводимых полей"""
        try:
            if int(self.lineEdit.text()) < 0 and int(self.lineEdit.text()) > 2147483648:
                raise ValueError

            if (
                int(self.lineEdit_2.text()) < 0
                and int(self.lineEdit_2.text()) > 2147483648
            ):
                raise ValueError
        except ValueError:
            return False
        return True

    def set_values(self, current_data: dict):
        """При изменении записи устанавливает выбранные значения"""
        self.lineEdit.setText(str(current_data["seed_dmr"]))
        self.lineEdit_2.setText(str(current_data["seed_count"]))
        self.lineEdit_3.setText(str(current_data["seed_number"]))
        current_species_name = (
            Species.select(Species.name_species)
            .where(Species.code_species == current_data["code_species"])
            .get()
            .name_species
        )
        current_seed_type_name = (
            KindSeeds.select(KindSeeds.name_kind_seeds)
            .where(KindSeeds.code_kind_seeds == current_data["seed_type_code"])
            .get()
            .name_kind_seeds
        )
        self.comboBox.setCurrentText(current_species_name)
        self.comboBox_2.setCurrentText(current_seed_type_name)

    def accept(self):
        self.name_species = self.comboBox.itemText(self.comboBox.currentIndex())
        self.code_species = self.comboBox.itemData(self.comboBox.currentIndex())
        if not self.seeds_field_validation():
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Введены неверные данные")
            return False
        self.seed_type_code = self.comboBox_2.itemData(self.comboBox_2.currentIndex())
        self.name_kind_seeds = self.comboBox_2.itemText(self.comboBox_2.currentIndex())
        self.seed_dmr = self.lineEdit.text()
        self.seed_count = self.lineEdit_2.text()
        self.seed_number = self.lineEdit_3.text()
        super().accept()

    def exec(self):
        if len(self.current_spc) == 0:
            QtWidgets.QMessageBox.critical(
                self, "Ошибка", "Не добавлены породы в перечет."
            )
            return False

        self.fill_species()
        self.fill_kind_seeds()
        if self.current_data:
            self.set_values(self.current_data)
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
        else:
            self.setDetailedText(None)
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
