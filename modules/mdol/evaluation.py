# self.crit_message('Ошибка вывода', error, traceback.format_exc())
import traceback

from PyQt5 import QtCore, QtWidgets, QtGui
from decimal import Decimal

from .src.evaluation import evaluation_main_window

from .src.evaluation.utilites import calculate
from .src.evaluation.utilites import export_to_db
from .src.evaluation.utilites import import_from_db
from .src.evaluation.utilites import export_to_xls
from .src.evaluation.utilites import export_to_lp

from .src.models.ta_fund import *
from .src.models.nri import *


class Evaluation(evaluation_main_window.MainWindow):
    def __init__(self, uuid):
        super().__init__()

        self.uuid = uuid
        self.import_from_db()
        self.statusBar.showMessage('UUID лесосеки: ' + str(self.uuid))
        self.species_positions = {}  # позиции пород в таблице перечётки
        self.not_cutting = []  # перечёт не подлежащих к рубке
        self.trf_height = {'': 0}
        self.attributes = {}
        self.restatement_data = []
        self.restatement_amount = []
        self.species_trf_height = {}
        self.data_wpulp_amount = {}
        self.data_wpulp_table = []
        self.temp()

    def import_from_db(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.import_from_db_thread = import_from_db.ImportData(uuid=self.uuid)
        self.import_from_db_thread.start()
        self.import_from_db_thread.signal_general.connect(self.render_static_data, QtCore.Qt.QueuedConnection)
        self.import_from_db_thread.signal_restatement.connect(self.render_restatement_table, QtCore.Qt.QueuedConnection)
        self.import_from_db_thread.signal_wpulp_info.connect(self.render_dynamic_data, QtCore.Qt.QueuedConnection)
        self.import_from_db_thread.signal_wpulp.connect(self.render_wpulp_table, QtCore.Qt.QueuedConnection)
        self.import_from_db_thread.signal_status.connect(lambda x: self.crit_message('Ошибка импорта', '', x), QtCore.Qt.QueuedConnection)

    def build_trf_height_table(self):
        for trf in Trf_height.select():  # получаю все возможные разряды высот
            self.trf_height[trf.name_trf_height] = trf.code_trf_height
        for spc in self.species_positions.keys():
            spc = Species.select().where(Species.name_species_latin == spc).get().name_species
            self.tableWidget_5.insertRow(self.tableWidget_5.rowCount())
            self.tableWidget_5.setItem(self.tableWidget_5.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(spc))
            cb = QtWidgets.QComboBox()
            cb.addItems(list(self.trf_height.keys()))
            self.tableWidget_5.setCellWidget(self.tableWidget_5.rowCount() - 1, 1, cb)
        QtWidgets.QApplication.restoreOverrideCursor()

    def render_static_data(self, data):  # Информация с лесосеки (с таблицы publick."Лесосеки")
        self.label_19.setText(data['enterprise'])
        self.label_20.setText(data['forestry'])
        self.label_21.setText(str(data['compartment']))
        self.label_22.setText(str(data['sub_compartment']))
        self.label_23.setText(str(data['cutting_area']))  # Номер лесосеки
        self.label_24.setText(str(data['area']))  # Площадь
        if str(data['person_name']) != 'None':
            self.lineEdit_4.setText(str(data['person_name']))
        if str(data['description']) != 'None':
            self.lineEdit_3.setText(str(data['description']))

    def render_dynamic_data(self, att):  # Информация с МДО (с таблицы mdo."ta_fund")
        self.comboBox_3.setCurrentText(att['selected_rank_trf'])
        self.comboBox_4.setCurrentText(att['selected_meth_real'])
        self.comboBox_5.setCurrentText(att['selected_author'])
        self.comboBox_6.setCurrentText(att['selected_gr_forest'])
        self.comboBox_7.setCurrentText(att['selected_kind_use'])
        self.comboBox.setCurrentText(att['selected_section'])
        self.comboBox_2.setCurrentText(att['selected_econ'])
        self.comboBox_8.setCurrentText(att['selected_wct_meth'])
        self.comboBox_14.setCurrentText(att['selected_wct_meth_group'])
        self.comboBox_9.setCurrentText(att['selected_acc_meth'])
        self.comboBox_10.setCurrentText(att['selected_rgn_meth'])
        self.comboBox_13.setCurrentText(att['selected_status'])
        self.comboBox_11.setCurrentText(att['selected_bonit'])
        self.comboBox_12.setCurrentText(att['selected_type_for'])
        self.lineEdit.setText(str(att['year_forest_fund']))
        self.lineEdit_6.setText(str(att['formula']))
        self.lineEdit_10.setText(str(att['diameter_avg']))
        self.lineEdit_9.setText(str(att['height_avg']))
        self.lineEdit_8.setText(str(att['density']))
        self.lineEdit_7.setText(str(att['age']))
        self.lineEdit_5.setText(str(att['year_for_inv']))
        self.lineEdit_2.setText(str(att['year_cutting_area']))
        if str(att['year_for_inv']) != 'None':
            self.lineEdit_5.setText(str(att['year_for_inv']))
        if str(att['person_name']) != 'None':
            self.lineEdit_4.setText(str(att['person_name']))
        if str(att['description']) != 'None':
            self.lineEdit_3.setText(str(att['description']))
        if att['selected_kind_use_for_trf_vl'] == 1:
            self.radioButton_3.setChecked(True)
        if att['selected_kind_use_for_trf_vl'] == 2:
            self.radioButton_4.setChecked(True)
        if att['sign_liquid_crown']:
            self.checkBox_10.setChecked(True)
        else:
            self.checkBox_10.setChecked(False)
        if att['sign_brushwood']:
            self.checkBox_11.setChecked(True)
        else:
            self.checkBox_11.setChecked(False)
        if att['sign_waste']:
            self.checkBox_12.setChecked(True)
        else:
            self.checkBox_12.setChecked(False)

        self.dateEdit.setDate(QtCore.QDate(QtCore.QDate.fromString(str(att['selected_date_filled']), "yyyy-MM-dd")))
        self.dateEdit_2.setDate(QtCore.QDate(QtCore.QDate.fromString(str(att['selected_date_taxes']), "yyyy-MM-dd")))

        """Записываю разряды высот"""
        for row in range(self.tableWidget_5.rowCount()):
            self.tableWidget_5.cellWidget(row, 1).setCurrentText(att['trf_s'][self.tableWidget_5.item(row, 0).text()])
        # self.calculate()

    def render_restatement_table(self, data):
        """
        Заношу данные в таблицу перечётки (вкладка "Перечёт деревьев" и "Бубки не подлежат")
        """
        self.restatement_data = data
        """Таблица Перечёт деревьев"""
        for one_record in data['quality_data']:
            if one_record['species'] not in list(self.species_positions.keys()):  # если породы нету в таблице-присваю ей позицию в dict
                self.species_positions[one_record['species']] = len(self.species_positions.keys()) * 2
            one_record['row'] = int(one_record['dmr'] / 4)
            one_record['column'] = self.species_positions[one_record['species']]
            self.tableWidget.showRow(one_record['row'])
            if self.tableWidget.columnCount() <= one_record['column'] + 1:  # Создаю колонки, если такой попроды нету
                self.tableWidget.insertColumn(one_record['column'] + 1)
                self.tableWidget.insertColumn(one_record['column'] + 2)
                # Sets the span of the table element at (row , column ) to the number of rows
                # and columns specified by (rowSpanCount , columnSpanCount ).
                self.tableWidget.setSpan(0, one_record['column'] + 1, 1, 2)
                self.tableWidget.setItem(0, one_record['column'] + 1, QtWidgets.QTableWidgetItem(
                    str(Species.select().where(Species.name_species_latin == one_record['species']).get().name_species)))
                self.tableWidget.item(0, one_record['column'] + 1).setTextAlignment(QtCore.Qt.AlignHCenter)
                self.tableWidget.setItem(1, one_record['column'] + 1, QtWidgets.QTableWidgetItem('Делов.'))
                self.tableWidget.setItem(1, one_record['column'] + 2, QtWidgets.QTableWidgetItem('Дрова'))

            if int(one_record['num_ind']) > 0:
                self.tableWidget.setItem(one_record['row'], one_record['column'] + 1, QtWidgets.QTableWidgetItem(str(one_record['num_ind'])))
                self.tableWidget.item(one_record['row'], one_record['column'] + 1).setTextAlignment(QtCore.Qt.AlignHCenter)

            if int(one_record['num_fuel']) > 0:
                self.tableWidget.setItem(one_record['row'], one_record['column'] + 2, QtWidgets.QTableWidgetItem(str(one_record['num_fuel'])))
                self.tableWidget.item(one_record['row'], one_record['column'] + 2).setTextAlignment(QtCore.Qt.AlignHCenter)
        """Считаю сумму"""
        amount = {}
        for column in range(1, self.tableWidget.columnCount()):
            amount[column] = 0
            for row in range(2, self.tableWidget.rowCount() - 1):
                if self.tableWidget.item(row, column):
                    amount[column] = amount[column] + int(self.tableWidget.item(row, column).text())
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, column,
                                         QtWidgets.QTableWidgetItem(str(amount[column])))
                self.tableWidget.item(self.tableWidget.rowCount() - 1, column).setTextAlignment(QtCore.Qt.AlignHCenter)
                self.tableWidget.item(self.tableWidget.rowCount() - 1, column).setBackground(QtGui.QColor('#bdf0ff'))
        total = 0
        for i in amount.values():
            total += i
        self.label_28.setText(str(total))
        self.restatement_amount = list(amount.values())
        self.build_trf_height_table()  # Строю таблицу с разрядами высот

        """Таблица биоразнообразия"""
        self.not_cutting_data = data['not_cutting_data']
        total = 0
        if len(data['not_cutting_data']) > 0:
            for record in data['not_cutting_data']:
                self.tableWidget_3.insertRow(self.tableWidget_3.rowCount())
                self.tableWidget_3.setItem(self.tableWidget_3.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(record['species']))
                self.tableWidget_3.setItem(self.tableWidget_3.rowCount() - 1, 1, QtWidgets.QTableWidgetItem('  Сохранение биоразнообразия  '))
                self.tableWidget_3.setItem(self.tableWidget_3.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(str(record['dmr'])))
                self.tableWidget_3.setItem(self.tableWidget_3.rowCount() - 1, 3, QtWidgets.QTableWidgetItem(str(record['num_biodiversity'])))
                total+=record['num_biodiversity']
        for column in range(self.tableWidget_3.columnCount()):
            for row in range(self.tableWidget_3.rowCount()):
                self.tableWidget_3.item(row, column).setTextAlignment(QtCore.Qt.AlignHCenter)
        self.label_6.setText('Итого деревьев : '+str(total))

    def render_not_cutting_table(self, data):
        data = data['not_cutting_data']
        self.not_cutting_data = data
        total = 0
        if len(data) > 0:
            for record in data:
                self.tableWidget_3.insertRow(self.tableWidget_3.rowCount())
                self.tableWidget_3.setItem(self.tableWidget_3.rowCount()-1, 0, QtWidgets.QTableWidgetItem(record['species']))
                self.tableWidget_3.setItem(self.tableWidget_3.rowCount()-1, 1, QtWidgets.QTableWidgetItem('  Сохранение биоразнообразия  '))
                self.tableWidget_3.setItem(self.tableWidget_3.rowCount()-1, 2, QtWidgets.QTableWidgetItem(str(record['dmr'])))
                self.tableWidget_3.setItem(self.tableWidget_3.rowCount()-1, 3, QtWidgets.QTableWidgetItem(str(record['num_biodiversity'])))
                total+=record['num_biodiversity']
        for column in range(self.tableWidget_3.columnCount()):
            for row in range(self.tableWidget_3.rowCount()):
                self.tableWidget_3.item(row, column).setTextAlignment(QtCore.Qt.AlignHCenter)
        self.label_6.setText('Итого деревьев : '+str(total))

    def render_wpulp_table(self, data):  # заношу данные в таблицу мдо (вкладка "Запас и стоимость древесины")
        self.data_wpulp_amount.clear()
        self.data_wpulp_table.clear()
        self.tableWidget_2.setRowCount(3)  # удаляю старые значения
        self.data_wpulp_table = data
        for rec in data:
            row = self.tableWidget_2.rowCount()
            self.tableWidget_2.insertRow(row)
            self.tableWidget_2.setItem(row, 0, QtWidgets.QTableWidgetItem(Species.get(Species.code_species == rec['code_species']).name_species))
            self.tableWidget_2.setItem(row, 1, QtWidgets.QTableWidgetItem(Trf_height.get(Trf_height.code_trf_height == rec['code_trf_height']).name_trf_height))
            self.tableWidget_2.setItem(row, 2, QtWidgets.QTableWidgetItem(str(rec['wpulp_ind_large'])))
            self.tableWidget_2.setItem(row, 3, QtWidgets.QTableWidgetItem(str(rec['wpulp_ind_medium'])))
            self.tableWidget_2.setItem(row, 4, QtWidgets.QTableWidgetItem(str(rec['wpulp_ind_small'])))
            self.tableWidget_2.setItem(row, 5, QtWidgets.QTableWidgetItem(str(rec['wpulp_ind'])))
            self.tableWidget_2.setItem(row, 6, QtWidgets.QTableWidgetItem(str(rec['wpulp_fuel'])))
            self.tableWidget_2.setItem(row, 7, QtWidgets.QTableWidgetItem(str(rec['wpulp_liquid'])))
            self.tableWidget_2.setItem(row, 8, QtWidgets.QTableWidgetItem(str(rec['wpulp_crw_lq'])))
            self.tableWidget_2.setItem(row, 9, QtWidgets.QTableWidgetItem(str(rec['wpulp_brushwood'])))
            self.tableWidget_2.setItem(row, 10, QtWidgets.QTableWidgetItem(str(rec['wpulp_waste'])))
            self.tableWidget_2.setItem(row, 11, QtWidgets.QTableWidgetItem(str(rec['wpulp_total'])))
            self.tableWidget_2.setItem(row, 12, QtWidgets.QTableWidgetItem(str(rec['trf_vl_ind'])))
            self.tableWidget_2.setItem(row, 13, QtWidgets.QTableWidgetItem(str(rec['trf_vl_fuel'])))
            self.tableWidget_2.setItem(row, 14, QtWidgets.QTableWidgetItem(str(rec['trf_vl_liquid'])))
            self.tableWidget_2.setItem(row, 15, QtWidgets.QTableWidgetItem(str(rec['trf_vl_crw_lq'])))
            self.tableWidget_2.setItem(row, 16, QtWidgets.QTableWidgetItem(str(rec['trf_vl_brushwood'])))
            self.tableWidget_2.setItem(row, 17, QtWidgets.QTableWidgetItem(str(rec['trf_vl_waste'])))
            self.tableWidget_2.setItem(row, 18, QtWidgets.QTableWidgetItem(str(rec['trf_vl_total'])))
            for i in list(rec.keys()):
                if i != 'code_species' and i != 'code_trf_height' and i != 'name_species':
                    if i not in list(self.data_wpulp_amount.keys()):
                        self.data_wpulp_amount[i] = 0
                        self.data_wpulp_amount[i] += rec[i]
                    else:
                        self.data_wpulp_amount[i] += rec[i]

        """Считаю и записываю сумму"""
        self.tableWidget_2.insertRow(self.tableWidget_2.rowCount())
        self.tableWidget_2.setItem(self.tableWidget_2.rowCount()-1, 0, QtWidgets.QTableWidgetItem("Итого"))
        self.tableWidget_2.setItem(self.tableWidget_2.rowCount()-1, 1, QtWidgets.QTableWidgetItem(""))

        row = self.tableWidget_2.rowCount()-1
        self.tableWidget_2.setItem(row, 2, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_ind_large'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 3, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_ind_medium'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 4, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_ind_small'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 5, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_ind'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 6, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_fuel'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 7, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_liquid'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 8, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_crw_lq'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 9, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_brushwood'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 10, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_waste'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 11, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['wpulp_total'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 12, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['trf_vl_ind'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 13, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['trf_vl_fuel'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 14, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['trf_vl_liquid'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 15, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['trf_vl_crw_lq'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 16, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['trf_vl_brushwood'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 17, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['trf_vl_waste'])).quantize(Decimal('0.01')))))
        self.tableWidget_2.setItem(row, 18, QtWidgets.QTableWidgetItem(
            str(Decimal(str(self.data_wpulp_amount['trf_vl_total'])).quantize(Decimal('0.01')))))

        for i in range(self.tableWidget_2.columnCount()):  # Крашу последнюю строку
            self.tableWidget_2.item(self.tableWidget_2.rowCount()-1, i).setBackground(QtGui.QColor('#bdf0ff'))

        self.progressBar.setValue(100)
        # self.tabWidget.setCurrentWidget(self.tabWidget.findChild(QtWidgets.QWidget, 'tab_3'))  # переход на 3 вкладку

    def render_wpulp_table_whip(self, data):
        self.label_27.setText(str(Decimal(str(data)).quantize(Decimal('0.01'))))

    def save_to_db(self):
        data = self.all_data()
        """Отправляю все данные в поток"""
        if data:  # Если таблица не пуста
            try:  # Проверяю существуют ли записи
                Ta_fund.select().where(Ta_fund.offset_uuid == self.uuid).get()
                Ta_fund_wpulp.select().where(Ta_fund_wpulp.offset_uuid == self.uuid).get()
                q = QtWidgets.QMessageBox.warning(self, "ПО \"Отвод\". Ведомость материальной оценки лесосеки",
                                                  'Ведомость материальной оценки лесосеки уже существует\n'
                                                   'Вы хотите перезаписать данные?',
                                                  buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if q == 16384:  # если нажали Yes
                    try:  # пробую удалять записи с данным UUID
                        Ta_fund.delete().where(Ta_fund.offset_uuid == self.uuid).execute()
                        Ta_fund_wpulp.delete().where(Ta_fund_wpulp.offset_uuid == self.uuid).execute()
                    except Exception as error:
                        self.crit_message('Ошибка записи в БД. Данные не сохранены.', error, traceback.format_exc())
                        return None

                    self.export_to_db_thread = export_to_db.Export_data(attributes=data,  # опции
                                                                        data=data['ta_fund_wpulp']['wpulp_data'],  # значения в таблице WPULP ("Запас и стоимость древесины")
                                                                        )
                    self.export_to_db_thread.start()
                    self.export_to_db_thread.signal_status.connect(lambda x: self.crit_message(x[0], x[1], x[2]), QtCore.Qt.QueuedConnection)
                if q == 65536:  # Если нажали No
                    return None
            except:
                self.export_to_db_thread = export_to_db.Export_data(attributes=data,  # опции
                                                                    data=data['ta_fund_wpulp']['wpulp_data'],  # значения в таблице WPULP ("Запас и стоимость древесины")
                                                                    )
                self.export_to_db_thread.start()
                self.export_to_db_thread.signal_status.connect(lambda x: self.crit_message(x[0], x[1], x[2]), QtCore.Qt.QueuedConnection)
        else:
            # self.crit_message('Не рассчитаны запас и стоимость древесин', '', '')
            return None

    def calculate(self):
        self.progressBar.setValue(0)
        self.data_wpulp_table = []
        if self.all_data():
            self.calculate_thread = calculate.Export_data(uuid=self.uuid, attributes=self.all_data())
            self.calculate_thread.start()
            self.calculate_thread.signal_status_bar.connect(lambda x: self.progressBar.setValue(self.progressBar.value()+x))
            self.calculate_thread.signal_data_by_spc.connect(self.render_wpulp_table, QtCore.Qt.QueuedConnection)
            self.calculate_thread.signal_whip.connect(self.render_wpulp_table_whip, QtCore.Qt.QueuedConnection)

    def export_restetement_xls(self):
        data = self.all_data()
        if data:
            data = self.all_data()
            path = QtWidgets.QFileDialog.getSaveFileName(self, caption='Сохранение ведомости перечёта деревьев',
                                                         directory=self.uuid[-12:]+'_Перечётная_ведомость.xlsx')
            if path[0] != '':
                self.export_restatement_xls_thread = export_to_xls.Export_restatement_xls(data=data, path=path[0])
                self.export_restatement_xls_thread.signal_status.connect(lambda x: self.crit_message(x[0], x[1], x[2]))
                self.export_restatement_xls_thread.start()
            else:
                return

    def export_evaluation_lp(self):
        """Метод запускает поток для экспорта всей МДО (включая перечётку) в формат для АРМ Лесопользования"""
        data = self.all_data()
        if data:
            path = QtWidgets.QFileDialog.getSaveFileName(self, caption='Экспорт данных',
                                                         directory=self.uuid+'.fad')
            if path[0] != '':
                self.export_evaluation_lp_thread = export_to_lp.ExportData(data=data, filename=path)
                self.export_evaluation_lp_thread.start()
                self.export_evaluation_lp_thread.signal_status.connect(lambda x: self.crit_message(x[0], x[1], x[2]))
            else:
                return

    def all_data(self):
        """Получаю все данные из окна приллжения"""
        big_data = {}  # надо очищать
        ta_fund = {}
        ta_fund_wpulp = {}
        ta_fund_enum = {}
        system = {}
        """Получаю разряды высот для пород"""
        for row in range(self.tableWidget_5.rowCount()):
            if self.tableWidget_5.cellWidget(row, 1).currentText() == '':
                self.crit_message('Выберите разряд высот для породы ' + self.tableWidget_5.item(row, 0).text(), '', '')
                return None
            else:
                code_spc = Species.select().where(
                    Species.name_species == self.tableWidget_5.item(row, 0).text()).get().code_species
                self.species_trf_height[code_spc] = Trf_height.select().where(
                    Trf_height.name_trf_height == self.tableWidget_5.cellWidget(row,
                                                                                1).currentText()).get().code_trf_height
        system['species_trf_height'] = self.species_trf_height
        if len(self.species_trf_height) == 0:
            self.crit_message('Отсутсвуют данные перечёта деревьев.', '', '')
            return None

        """Таблица для расчёта запаса"""
        if self.comboBox_5.currentText() == '':
            self.crit_message('Выберите таблицу для расчёта запаса.', '', '')
            return None
        else:
            ta_fund['code_author'] = self.comboBox_5.itemData(self.comboBox_5.currentIndex(), QtCore.Qt.UserRole)

        """Используемые таксы рубок"""
        if self.radioButton_3.isChecked():
            ta_fund['code_kind_use_for_trf_vl'] = 1
        elif self.radioButton_4.isChecked():
            ta_fund['code_kind_use_for_trf_vl'] = 2
        else:
            self.crit_message('Выберите используемые таксы рубок.', '', '')
            return None

        """Разряд такс"""
        if self.comboBox_3.currentText() == '':
            self.crit_message('Выберите разряд такс.', '', '')
            return None
        else:
            ta_fund['code_rank_trf'] = self.comboBox_3.itemData(self.comboBox_3.currentIndex(), QtCore.Qt.UserRole)

        """Вид пользования"""
        if self.comboBox_7.currentText() == '':
            self.crit_message('Выберите вид пользования.', '', '')
            return None
        else:
            ta_fund['code_kind_use'] = self.comboBox_7.itemData(self.comboBox_7.currentIndex(), QtCore.Qt.UserRole)

        """Категория леса"""
        if self.comboBox_6.currentText() == '':
            self.crit_message('Выберите категорию леса.', '', '')
            return None
        else:
            ta_fund['code_gr_forest'] = self.comboBox_6.itemData(self.comboBox_6.currentIndex(), QtCore.Qt.UserRole)

        """Тип реализации"""
        if self.comboBox_4.currentText() == '':
            self.crit_message('Выберите тип реализации.', '', '')
            return None
        else:
            ta_fund['code_meth_real'] = self.comboBox_4.itemData(self.comboBox_4.currentIndex(), QtCore.Qt.UserRole)

        """Хозсецкия"""
        if self.comboBox.currentText() == '':
            self.crit_message('Выберите хозсекцию.', '', '')
            return None
        else:
            ta_fund['code_section'] = self.comboBox.itemData(self.comboBox.currentIndex(), QtCore.Qt.UserRole)

        """Группа пород"""
        if self.comboBox_2.currentText() == '':
            self.crit_message('Выберите группу пород.', '', '')
            return None
        else:
            ta_fund['code_econ'] = self.comboBox_2.itemData(self.comboBox_2.currentIndex(), QtCore.Qt.UserRole)

        """Вид рубки"""
        if self.comboBox_8.currentText() == '':
            self.crit_message('Выберите вид рубки.', '', '')
            return None
        else:
            ta_fund['code_wct_meth'] = self.comboBox_14.itemData(self.comboBox_14.currentIndex(), QtCore.Qt.UserRole)

        """Метод учёта"""
        if self.comboBox_9.currentText() == '':
            self.crit_message('Выберите метод учёта.', '', '')
            return None
        else:
            ta_fund['code_acc_meth'] = self.comboBox_9.itemData(self.comboBox_9.currentIndex(), QtCore.Qt.UserRole)

        """Состав насаждений"""
        if self.comboBox_13.currentText() == '':
            self.crit_message('Выберите состав насаждений.', '', '')
            return None
        else:
            ta_fund['code_status'] = self.comboBox_13.itemData(self.comboBox_13.currentIndex(), QtCore.Qt.UserRole)

        """Бонитет"""
        if self.comboBox_11.currentText() == '':
            self.crit_message('Выберите бонитет.', '', '')
            return None
        else:
            ta_fund['code_bonit'] = self.comboBox_11.itemData(self.comboBox_11.currentIndex(), QtCore.Qt.UserRole)

        """Тип леса"""
        if self.comboBox_12.currentText() == '':
            self.crit_message('Выберите тип леса.', '', '')
            return None
        else:
            ta_fund['code_type_for'] = self.comboBox_12.itemData(self.comboBox_12.currentIndex(), QtCore.Qt.UserRole)

        """Год лесного фонда (Год лесного фонда (год плановой рубки))"""
        if self.lineEdit.text() == '':
            self.crit_message('Определите год лесного фонда.', '', '')
            return None
        else:
            ta_fund['year_forest_fund'] = self.lineEdit.text()

        """Год отвода"""
        if self.lineEdit_2.text() == '':
            self.crit_message('Определите год отвода.', '', '')
            return None
        else:
            ta_fund['year_cutting_area'] = self.lineEdit_2.text()

        """Состав"""
        if self.lineEdit_6.text() == '':
            self.crit_message('Определите формулу состава.', '', '')
            return None
        else:
            ta_fund['formula'] = self.lineEdit_6.text()

        """Год лесоустройства"""
        if self.lineEdit_5.text() == '':
            ta_fund['year_for_inv'] = None
        else:
            ta_fund['year_for_inv'] = self.lineEdit_5.text()

        """Диаметр средний"""
        if self.lineEdit_10.text() == '':
            ta_fund['diameter_avg'] = None
        else:
            ta_fund['diameter_avg'] = self.lineEdit_10.text()

        """Высота средняя"""
        if self.lineEdit_9.text() == '':
            ta_fund['height_avg'] = None
        else:
            ta_fund['height_avg'] = self.lineEdit_9.text()

        """Полнота"""
        if self.lineEdit_8.text() == '':
            ta_fund['density'] = None
        else:
            ta_fund['density'] = self.lineEdit_8.text()

        """Возраст"""
        if self.lineEdit_7.text() == '':
            ta_fund['age'] = None
        else:
            ta_fund['age'] = self.lineEdit_7.text()

        ta_fund['date_filled'] = self.dateEdit.date().toPyDate()  # дата заполнения
        ta_fund['date_taxes'] = self.dateEdit_2.date().toPyDate()  # дата оценки
        system['enterprise'] = self.label_19.text()  # название лесхоза
        system['forestry'] = self.label_20.text()  # название лесничества
        system['num_compartment'] = self.label_21.text()  # номер квартала
        system['num_sub_compartment'] = self.label_22.text()  # номер выдела
        system['num_cutting_area'] = self.label_23.text()  # номер лесосеки
        system['area'] = self.label_24.text()  # площадь экспл.
        ta_fund['person_name'] = self.lineEdit_4.text()  # ФИО работника
        ta_fund['description'] = self.lineEdit_3.text()  # дополнительная информация
        ta_fund['code_rgn_meth'] = self.comboBox_10.itemData(self.comboBox_10.currentIndex(), QtCore.Qt.UserRole)  # Способ восстановления
        ta_fund['offset_uuid'] = self.uuid  # uuid отвода
        system['offset_uuid'] = self.uuid  # uuid отвода
        ta_fund_enum['offset_uuid'] = self.uuid  # uuid отвода
        ta_fund_wpulp['offset_uuid'] = self.uuid  # uuid отвода
        ta_fund['sign_liquid_crown'] = self.checkBox_10.isChecked()  # входит ли ликвид из кроны в общий запас
        ta_fund['sign_brushwood'] = self.checkBox_11.isChecked()  # входит ли хворост в общий запас
        ta_fund['sign_waste'] = self.checkBox_12.isChecked()  # входят ли отходы в общий запас
        system['calculate_whip'] = self.checkBox_3.isChecked()  # считать ли объём хлыста
        system['amount_trees'] = int(self.label_28.text())  # колиичество деревьев на лесосеке (дел\дров)
        ta_fund_enum['restatement_data'] = self.restatement_data
        ta_fund_enum['restatement_data_amount'] = self.restatement_amount
        ta_fund_wpulp['wpulp_data'] = self.data_wpulp_table
        ta_fund_wpulp['wpulp_data_amount'] = self.data_wpulp_amount
        """Получаю колличество записей перечётки для текущей лесосеки"""
        system['count_records_enum'] = 0
        for rec in Ta_fund_enum.select().where(Ta_fund_enum.offset_uuid == self.uuid):
            system['count_records_enum'] += 1

        big_data = {'ta_fund': ta_fund, 'ta_fund_enum': ta_fund_enum, 'ta_fund_wpulp': ta_fund_wpulp, 'system': system}
        return big_data

    # def closeEvent(self, event):
    #     try:
    #         PostgreSQL().set_connection().close()
    #     except:
    #         None

    def crit_message(self, error, info, detailed_text):
        """
        Это метод для вызова окна ошибки
        """
        dlg = QtWidgets.QMessageBox(self)
        dlg.setIcon(QtWidgets.QMessageBox.Warning)
        dlg.setWindowModality(QtCore.Qt.WindowModal)
        dlg.setWindowTitle("ПО \"Отвод\". Ведомость материальной оценки лесосеки")
        dlg.setText(error)
        dlg.setInformativeText(str(info))
        dlg.setDetailedText(str(detailed_text))
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dlg.show()

    def temp(self):
        """Временный метод для срытия неиспользуемых виджетов"""
        # self.menuBar().hide()
        self.label_26.hide()
        self.checkBox_3.hide()
        self.checkBox.hide()
        self.checkBox_2.hide()
        self.checkBox_4.hide()
        self.checkBox_5.hide()
        self.checkBox_6.hide()
        self.checkBox_7.hide()
        self.checkBox_8.hide()
        # self.checkBox_10.hide()
        # self.checkBox_11.hide()
        # self.checkBox_12.hide()
        self.radioButton.hide()
        self.radioButton_2.hide()
        self.tableWidget_4.hide()
        # self.pushButton.hide()
        self.pushButton_2.hide()
        # self.pushButton_3.hide()
        self.pushButton_4.hide()

