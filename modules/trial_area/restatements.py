import os
import serial
import traceback
import uuid
from decimal import Decimal, ROUND_HALF_UP
from PyQt5 import QtWidgets, QtCore, QtGui

from .src.business import (
    restatement_main_window,
    add_by_caliper,
    export_to_db,
    export_to_json,
    import_from_db,
    import_from_json,
    calculate_amount,
    export_to_xls,
    add_by_hand,
    area_property_main_window,
)
from .src.config import Settings

from .src.models.restatement import Trees
from .src.models.public import Area
from .src.models.nri import Species, Organization


class Restatement(restatement_main_window.MainWindow):
    def __init__(self, uuid):
        super().__init__()

        self.connection = None  # создаю пустое соединение

        self.uuid = uuid  # уникальный идентификатор отвода
        self.last_data = {
            "species": "None",  # пример словаря на котором работает программа
            "dmr": 0,
            "num_ind": 0,
            "num_fuel": 0,
            "num_half_ind": 0,
            "device_sign": "None",
            "row": 0,
            "column": 0,
        }
        try:
            Area.select().where(Area.uuid == self.uuid).get()
            self.import_from_db()
        except Trees.DoesNotExist:
            None
        self.species_positions = {}  # позиции пород в таблице

    def add_table_item(self, data):
        """Вставляю данные в таблицу"""
        self.default_color()  # крашу прошлые ячейки в белый
        if data["device_sign"] == "caliper":
            """Проверяю изменяли ли прошлое значение вилкой (сводили в ноль или разводили больше 65)"""
            if data["dmr"] == 0 or data["dmr"] >= 65:
                if len(self.last_data) > 0:
                    if data["dmr"] == 0:
                        data["num_fuel"] = 1
                    if data["dmr"] >= 65:
                        data["num_half_ind"] = 1
                    data["num_ind"] = -1

                    data["dmr"] = self.last_data["dmr"]
                    data["column"] = self.last_data["column"]
                    data["row"] = self.last_data["row"]
                    data["species"] = self.last_data["species"]
                else:
                    return None
        """Записываю данные (создаю нужные столбцы если их нету, показываю скрытые столбцы если они нужны)"""
        if (
            data["species"] not in self.species_positions.keys()
        ):  # если породы нету в таблице-присваю ей позицию в dict
            # ! 4 (Четверка) в коже ниже, это сколько столбцов относится на породу
            self.species_positions[data["species"]] = (
                len(self.species_positions.keys()) * 4
            )

        data["row"] = int(data["dmr"] / 4)
        data["column"] = self.species_positions[data["species"]]
        self.tableWidget.showRow(data["row"])
        if (
            self.tableWidget.columnCount() <= data["column"] + 2
        ):  # Создаю колонки, если такой попроды нету
            self.add_table_new_species(data)
        """Собираю старые значения"""
        try:
            old_num_ind = int(
                self.tableWidget.item(data["row"], data["column"] + 2).text()
            )

        except:
            old_num_ind = 0
        try:
            old_num_fuel = int(
                self.tableWidget.item(data["row"], data["column"] + 3).text()
            )
        except:
            old_num_fuel = 0
        try:
            old_num_half_ind = int(
                self.tableWidget.item(data["row"], data["column"] + 4).text()
            )
        except:
            old_num_half_ind = 0
        """Прибавляю новые данные"""
        num_ind = data["num_ind"] + old_num_ind
        num_fuel = data["num_fuel"] + old_num_fuel
        num_half_ind = data["num_half_ind"] + old_num_half_ind

        if num_ind >= 0:
            self.tableWidget.setItem(
                data["row"],
                data["column"] + 2,
                QtWidgets.QTableWidgetItem(str(num_ind)),
            )
            self.tableWidget.item(data["row"], data["column"] + 2).setTextAlignment(
                QtCore.Qt.AlignHCenter
            )

        if num_fuel >= 0:
            self.tableWidget.setItem(
                data["row"],
                data["column"] + 3,
                QtWidgets.QTableWidgetItem(str(num_fuel)),
            )
            self.tableWidget.item(data["row"], data["column"] + 3).setTextAlignment(
                QtCore.Qt.AlignHCenter
            )

        if num_half_ind >= 0:
            self.tableWidget.setItem(
                data["row"],
                data["column"] + 4,
                QtWidgets.QTableWidgetItem(str(num_half_ind)),
            )
            self.tableWidget.item(data["row"], data["column"] + 4).setTextAlignment(
                QtCore.Qt.AlignHCenter
            )

        # Крашу новое значение:
        if num_ind != old_num_ind:
            self.tableWidget.item(data["row"], data["column"] + 2).setBackground(
                QtGui.QColor("#c1f593")
            )
        if num_fuel != old_num_fuel:
            self.tableWidget.item(data["row"], data["column"] + 3).setBackground(
                QtGui.QColor("#c1f593")
            )
        if num_half_ind != old_num_half_ind:
            self.tableWidget.item(data["row"], data["column"] + 4).setBackground(
                QtGui.QColor("#c1f593")
            )

        self.last_data = data

        if data["device_sign"] == "caliper":
            self.calculate_amount()  # Считаю сумму

    def add_data_att(self, att_data):
        self.att_data = att_data
        self.label_4.setText(att_data["enterprise"])
        self.label_6.setText(att_data["forestry"])
        self.label_7.setText(att_data["compartment"])
        self.label_8.setText(att_data["sub_compartment"])
        self.lineEdit.setText(att_data["area_square"])

    def add_table_new_species(self, data):
        self.tableWidget.insertColumn(data["column"] + 1)
        self.tableWidget.insertColumn(data["column"] + 2)
        self.tableWidget.insertColumn(data["column"] + 3)
        self.tableWidget.insertColumn(data["column"] + 4)
        # Sets the span of the table element at (row , column ) to the number of rows
        # and columns specified by (rowSpanCount , columnSpanCount ).
        self.tableWidget.setSpan(0, data["column"] + 1, 1, 4)
        self.tableWidget.setItem(
            0,
            data["column"] + 1,
            QtWidgets.QTableWidgetItem(
                str(
                    Species.select()
                    .where(Species.name_species_latin == data["species"])
                    .get()
                    .name_species
                )
            ),
        )
        self.tableWidget.item(0, data["column"] + 1).setTextAlignment(
            QtCore.Qt.AlignHCenter
        )
        self.tableWidget.setItem(
            1, data["column"] + 1, QtWidgets.QTableWidgetItem("ИТГ")
        )
        self.tableWidget.item(1, data["column"] + 1).setBackground(
            QtGui.QColor("#DDA0DD")
        )
        self.tableWidget.setItem(
            1, data["column"] + 2, QtWidgets.QTableWidgetItem("ДЕЛ")
        )
        self.tableWidget.setItem(
            1, data["column"] + 3, QtWidgets.QTableWidgetItem("ДР")
        )
        self.tableWidget.setItem(
            1, data["column"] + 4, QtWidgets.QTableWidgetItem("СУХ")
        )

    def default_color(self):
        """Крашу прошлые значения в белый цвет"""
        if self.tableWidget.item(self.last_data["row"], self.last_data["column"]):
            self.tableWidget.item(
                self.last_data["row"], self.last_data["column"]
            ).setBackground(QtGui.QColor("white"))
        if self.tableWidget.item(self.last_data["row"], self.last_data["column"] + 2):
            self.tableWidget.item(
                self.last_data["row"], self.last_data["column"] + 2
            ).setBackground(QtGui.QColor("white"))
        if self.tableWidget.item(self.last_data["row"], self.last_data["column"] + 3):
            self.tableWidget.item(
                self.last_data["row"], self.last_data["column"] + 3
            ).setBackground(QtGui.QColor("white"))
        if self.tableWidget.item(self.last_data["row"], self.last_data["column"] + 4):
            self.tableWidget.item(
                self.last_data["row"], self.last_data["column"] + 4
            ).setBackground(QtGui.QColor("white"))

    def add_table_amount(self, data):
        for column in range(1, len(data["amount"].keys()) + 1):
            self.tableWidget.setItem(
                self.tableWidget.rowCount() - 1,
                column,
                QtWidgets.QTableWidgetItem(str(data["amount"][column])),
            )
            self.tableWidget.item(
                self.tableWidget.rowCount() - 1, column
            ).setTextAlignment(QtCore.Qt.AlignHCenter)
            self.tableWidget.item(
                self.tableWidget.rowCount() - 1, column
            ).setBackground(QtGui.QColor("#bdf0ff"))

        for _ in data["total_by_species"]:
            self.tableWidget.setItem(
                _["row"], _["column"], QtWidgets.QTableWidgetItem(str(_["total"])),
            )
            self.tableWidget.item(_["row"], _["column"]).setTextAlignment(
                QtCore.Qt.AlignHCenter
            )
            self.tableWidget.item(_["row"], _["column"]).setBackground(
                QtGui.QColor("#DDA0DD")
            )

    def add_by_hand(self):
        object_add_record = add_by_hand.AddByHand(last_data=self.last_data)
        if object_add_record.exec() == 1:
            self.add_table_item(data=object_add_record.output_data)
            self.calculate_amount()  # Считаю сумму
        else:
            None

    def add_by_caliper(self):
        try:
            self.connection = serial.Serial(
                Settings(group="Default_Settings", key="caliper_port").read_setting(),
                9600,
            )
            self.pushButton_2.setStyleSheet("background-color: #70c858")
        except:
            self.pushButton_2.setStyleSheet("background-color: #ee534e")
            return None
        self.object_add_by_caliper_thread = add_by_caliper.Caliper(
            connection=self.connection
        )
        self.object_add_by_caliper_thread.start()
        self.object_add_by_caliper_thread.signal_output_data.connect(
            self.add_table_item, QtCore.Qt.QueuedConnection
        )

    def add_one_tree(self):
        current_item = self.tableWidget.item(
            self.tableWidget.currentRow(), self.tableWidget.currentColumn()
        )
        if (
            self.tableWidget.rowCount() - 1 > self.tableWidget.currentRow() > 1
        ):  # Если это не шапка и не сумма
            if (
                self.tableWidget.currentColumn() > 0
                and self.tableWidget.currentColumn() % 4 != 1
            ):  # Если это не диаметр и не итого
                self.default_color()
                if current_item is None:
                    self.tableWidget.setItem(
                        self.tableWidget.currentRow(),
                        self.tableWidget.currentColumn(),
                        QtWidgets.QTableWidgetItem("1"),
                    )  # Если в ячейке пусто - ставлю 1
                    self.tableWidget.item(
                        self.tableWidget.currentRow(), self.tableWidget.currentColumn()
                    ).setTextAlignment(QtCore.Qt.AlignHCenter)
                    """Крашу в #c1f593"""
                    self.tableWidget.item(
                        self.tableWidget.currentRow(), self.tableWidget.currentColumn()
                    ).setBackground(QtGui.QColor("#c1f593"))
                    self.last_data["row"] = self.tableWidget.currentRow()
                    self.last_data["column"] = self.tableWidget.currentColumn()
                else:
                    self.tableWidget.setItem(
                        self.tableWidget.currentRow(),
                        self.tableWidget.currentColumn(),
                        QtWidgets.QTableWidgetItem(str(int(current_item.text()) + 1)),
                    )
                    # Если в ячейке не пусто, то прибавляю 1
                    self.tableWidget.item(
                        self.tableWidget.currentRow(), self.tableWidget.currentColumn()
                    ).setTextAlignment(QtCore.Qt.AlignHCenter)

                    """Крашу в #c1f593"""
                    self.tableWidget.item(
                        self.tableWidget.currentRow(), self.tableWidget.currentColumn()
                    ).setBackground(QtGui.QColor("#c1f593"))
                    self.last_data["row"] = self.tableWidget.currentRow()
                    self.last_data["column"] = self.tableWidget.currentColumn()
                self.calculate_amount()

    def delete_one_tree(self):
        current_item = self.tableWidget.item(
            self.tableWidget.currentRow(), self.tableWidget.currentColumn()
        )
        if (
            self.tableWidget.rowCount() - 1 > self.tableWidget.currentRow() > 1
        ):  # Если это не шапка и не сумма
            if (
                self.tableWidget.currentColumn() > 0
                and self.tableWidget.currentColumn() % 4 != 1
            ):  # Если это не диаметр и не итого
                if current_item is not None:
                    if int(current_item.text()) > 0:
                        self.tableWidget.setItem(
                            self.tableWidget.currentRow(),
                            self.tableWidget.currentColumn(),
                            QtWidgets.QTableWidgetItem(
                                str(int(current_item.text()) - 1)
                            ),
                        )
                        self.tableWidget.item(
                            self.tableWidget.currentRow(),
                            self.tableWidget.currentColumn(),
                        ).setTextAlignment(QtCore.Qt.AlignHCenter)
                        self.calculate_amount()  # Считаю сумму
                        self.default_color()  # Крашу в белый

                        """Крашу в #c1f593"""
                        self.tableWidget.item(
                            self.tableWidget.currentRow(),
                            self.tableWidget.currentColumn(),
                        ).setBackground(QtGui.QColor("#c1f593"))
                        self.last_data["row"] = self.tableWidget.currentRow()
                        self.last_data["column"] = self.tableWidget.currentColumn()

    def calculate_amount(self):
        self.object_calculate_amount_tread = calculate_amount.Amount(
            table=self.tableWidget
        )
        self.object_calculate_amount_tread.start()
        self.object_calculate_amount_tread.signal_output_data.connect(
            self.add_table_amount, QtCore.Qt.QueuedConnection
        )

    def import_from_db(self):
        """Импортирую данные из БД"""
        self.object_import_from_db = import_from_db.Data(uuid=self.uuid)
        self.object_import_from_db.start()
        self.object_import_from_db.signal_output_data.connect(
            self.add_table_item, QtCore.Qt.QueuedConnection
        )
        self.object_import_from_db.signal_att_data.connect(
            self.add_data_att, QtCore.Qt.QueuedConnection
        )
        self.object_import_from_db.signal_calculate_amount.connect(
            self.calculate_amount, QtCore.Qt.QueuedConnection
        )

    def save_to_db(self):
        try:
            Trees.select().where(Trees.area_uuid == self.uuid).get()
            q = QtWidgets.QMessageBox.warning(
                self,
                "Внимание",
                "Пробная площадь уже существует\n" "Вы хотите перезаписать данные?",
                buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            )
            if q == 16384:  # если нажали Yes
                try:  # пробую удалять записи с данным UUID
                    Trees.delete().where(Trees.area_uuid == self.uuid).execute()
                except Exception as error:
                    self.crit_message(
                        "Ошибка записи в БД. Данные не сохранены.",
                        error,
                        traceback.format_exc(),
                    )
                    return None

                self.object_save_to_db_thread = export_to_db.DBData(
                    table=self.tableWidget, uuid=self.uuid, area=self.lineEdit.text()
                )
                self.object_save_to_db_thread.start()
                self.object_save_to_db_thread.signal_status.connect(
                    lambda x: self.crit_message(x["body"], "", "")
                )
            if q == 65536:  # Если нажали No
                return None
        except:
            self.object_save_to_db_thread = export_to_db.DBData(
                table=self.tableWidget, uuid=self.uuid, area=self.lineEdit.text()
            )
            self.object_save_to_db_thread.start()
            self.object_save_to_db_thread.signal_status.connect(
                lambda x: self.crit_message(x["body"], "", ""),
                QtCore.Qt.QueuedConnection,
            )

    def export_to_json(self):
        if self.tableWidget.columnCount() > 1:
            export_file = QtWidgets.QFileDialog.getSaveFileName(
                caption="Сохранение файла",
                directory=os.path.expanduser("~") + "/Documents/" + self.uuid + ".json",
                filter="JSON (*.json)",
            )
            if export_file[0]:
                self.object_export_to_json = export_to_json.Data(
                    uuid=self.uuid, table=self.tableWidget, export_file=export_file[0]
                )
                self.object_export_to_json.start()
                self.object_export_to_json.signal_status.connect(
                    lambda x: self.crit_message(x["body"], "", ""),
                    QtCore.Qt.QueuedConnection,
                )

        else:
            self.crit_message("Отсутствуют данные для экспорта.", "", "")

    def import_from_json(self):
        if self.tableWidget.columnCount() > 1:
            q = QtWidgets.QMessageBox.warning(
                self,
                "Внимание",
                "Данные уже присутствуют\n" "Вы хотите перезаписать данные?",
                buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            )
            if q == 16384:  # если нажали Yes
                import_file = QtWidgets.QFileDialog.getOpenFileName(
                    caption="Выберите файл",
                    directory=os.path.expanduser("~") + "/Documents/",
                )
                if import_file[0] != "":
                    """Работую с текущей таблицей"""
                    self.tableWidget.setColumnCount(1)
                    self.species_positions = {}  # очищаю позиции пород
                    for i in range(
                        2, self.tableWidget.rowCount() - 1
                    ):  # прячу диаметры
                        self.tableWidget.hideRow(i)

                    """Готовлю новые данные"""
                    self.object_import_from_json_thread = import_from_json.Data(
                        import_file=import_file[0]
                    )
                    self.object_import_from_json_thread.start()
                    self.object_import_from_json_thread.signal_new_uuid.connect(
                        lambda x: self.uuid == x, QtCore.Qt.QueuedConnection
                    )
                    self.object_import_from_json_thread.signal_output_record.connect(
                        self.add_table_item, QtCore.Qt.QueuedConnection
                    )
                    self.object_import_from_json_thread.signal_calculate_amount.connect(
                        self.calculate_amount, QtCore.Qt.QueuedConnection
                    )
                    self.object_import_from_json_thread.signal_error.connect(
                        lambda: self.crit_message("Ошибка импорта файла.", "", ""),
                        QtCore.Qt.QueuedConnection,
                    )
            if q == 65536:  # Если нажали No
                return None
        else:
            import_file = QtWidgets.QFileDialog.getOpenFileName(
                caption="Выберите файл",
                directory=os.path.expanduser("~") + "/Documents/",
            )
            if import_file[0] != "":
                """Готовлю новые данные"""
                self.object_import_from_json_thread = import_from_json.Data(
                    import_file=import_file[0]
                )
                self.object_import_from_json_thread.start()
                self.object_import_from_json_thread.signal_new_uuid.connect(
                    lambda x: self.uuid == x, QtCore.Qt.QueuedConnection
                )
                self.object_import_from_json_thread.signal_output_record.connect(
                    self.add_table_item, QtCore.Qt.QueuedConnection
                )
                self.object_import_from_json_thread.signal_calculate_amount.connect(
                    self.calculate_amount, QtCore.Qt.QueuedConnection
                )
                self.object_import_from_json_thread.signal_error.connect(
                    lambda: self.crit_message("Ошибка импорта файла.", "", ""),
                    QtCore.Qt.QueuedConnection,
                )

    def export_to_xls(self):
        self.att_data["area_square"] = self.lineEdit.text()
        if self.tableWidget.columnCount() > 1:
            export_file = QtWidgets.QFileDialog.getSaveFileName(
                caption="Сохранение файла",
                directory=os.path.expanduser("~") + "/Documents/" + self.uuid + ".xlsx",
                filter="Excel (*.xlsx)",
            )
            if export_file[0]:
                self.object_export_to_xls = export_to_xls.Data(
                    table=self.tableWidget,
                    export_file=export_file[0],
                    att_data=self.att_data,
                )
                self.object_export_to_xls.start()
                self.object_export_to_xls.signal_status.connect(
                    lambda x: self.crit_message(x["body"], "", ""),
                    QtCore.Qt.QueuedConnection,
                )

        else:
            self.crit_message("Отсутствуют данные для экспорта.", "", "")

    def crit_message(self, error, info, detailed_text):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setIcon(QtWidgets.QMessageBox.Warning)
        dlg.setWindowModality(QtCore.Qt.WindowModal)
        dlg.setWindowTitle('ПО "Пробы". Перечёт деревьев.')
        dlg.setText(error)
        dlg.setInformativeText(str(info))
        dlg.setDetailedText(str(detailed_text))
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dlg.show()

    def closeEvent(self, event):
        try:
            # PostgreSQL().set_connection().close()
            self.connection.close()
        except:
            None


class AreaProperty(area_property_main_window.MainWindow):
    """Начальное окно с выбором лесхоза и тд"""

    def __init__(self):
        super().__init__()

    def get_data_gui(self):
        self.label.setStyleSheet("color: none;")
        self.label_2.setStyleSheet("color: none;")
        self.label_3.setStyleSheet("color: none;")
        self.label_4.setStyleSheet("color: none;")
        self.label_5.setStyleSheet("color: none;")
        self.label_6.setStyleSheet("color: none;")

        if self.comboBox.currentText() == "":
            self.label.setStyleSheet("color: red;")
            return False
        if self.comboBox_2.currentText() == "":
            self.label_2.setStyleSheet("color: red;")
            return False
        if self.comboBox_3.currentText() == "":
            self.label_3.setStyleSheet("color: red;")
            return False
        if self.spinBox.value() <= 0:
            self.label_4.setStyleSheet("color: red;")
            return False
        if self.spinBox_2.value() <= 0:
            self.label_5.setStyleSheet("color: red;")
            return False
        if self.doubleSpinBox.value() <= 0:
            self.label_6.setStyleSheet("color: red;")
            return False

        num_enterprise = int(
            str(
                Organization.select(Organization.code_organization)
                .where(Organization.id_organization == self.comboBox_2.currentData())
                .get()
                .code_organization
            )[5:8]
        )
        num_forestry = int(
            str(
                Organization.select(Organization.code_organization)
                .where(Organization.id_organization == self.comboBox_3.currentData())
                .get()
                .code_organization
            )[-2:]
        )

        att_data = {
            "geom": None,
            "uuid": None,
            "num_forestry": num_forestry,
            "compartment": str(self.spinBox.value()),
            "sub_compartment": str(self.spinBox_2.value()),
            "area": str(
                Decimal(self.doubleSpinBox.value()).quantize(
                    Decimal("1.00"), ROUND_HALF_UP
                )
            ),
            "num_enterprise": num_enterprise,
            "num_cutting_area": None,
            "use_type": None,
            "cutting_type": None,
            "num_plot": None,
            "person_name": None,
            "description": None,
            "num_vds": None,
            "leshos_text": None,
            "lesnich_text": None,
            # "gplho": self.comboBox.currentData(),
        }
        return att_data

    def create_area(self):
        """Создаю сущность пробной площади"""
        att_data = self.get_data_gui()
        if att_data:
            att_data["uuid"] = str(uuid.uuid1())
            Area.create(**att_data)
            self.close()
            self.w = Restatement(uuid=att_data["uuid"])
            self.w.show()
            return True
        return False
