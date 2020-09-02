from PyQt5 import QtWidgets, uic, QtGui, QtCore
from ..config import Settings, BasicDir

from ...src.models.nri import *


class MainWindow(QtWidgets.QMainWindow, uic.loadUiType(BasicDir().get_basic_dir('ui/evaluation.ui'))[0]):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        """Применяю таблицу стилей"""
        styles = open(BasicDir().get_basic_dir('ui/stylesheets/base.qss'))
        # styles = open(Settings().resolve('base.qss'), 'r')
        styleData = styles.read()
        self.setStyleSheet(styleData)
        styles.close()
        """Локальные справочники"""
        self.rank_trf = {}
        self.meth_real = {}
        self.author = {}
        """Атрибуты кнопок"""
        self.pushButton.clicked.connect(self.save_to_db)
        self.pushButton_3.clicked.connect(self.export_evaluation_lp)
        self.pushButton_5.clicked.connect(self.calculate)
        self.pushButton_6.clicked.connect(self.export_restetement_xls)
        """Атрибуты таблицы перечёта"""
        self.tableWidget.horizontalHeader().setDefaultSectionSize(65)  # Стандартный размер столбцов
        # self.tableWidget.horizontalHeader().setSectionResizeMode(
        #     QtWidgets.QHeaderView.ResizeToContents)  # растягиваю столбец по контенту
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.verticalHeader().show()
        """Атрибуты таблицы "Рубки не подлежат" """
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)  # растягиваю столбец по контенту
        self.tableWidget_3.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        """Атрибуты таблицы "Разряды пород" """
        self.tableWidget_5.horizontalHeader().resizeSection(0, 100)  # Выставляю ширину столбца
        self.tableWidget_5.horizontalHeader().resizeSection(1, 30)  # Выставляю ширину столбца
        self.tableWidget_5.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        """Атрибуты таблицы "Условия снижения такс" """
        self.tableWidget_4.horizontalHeader().resizeSection(0, 10)  # Выставляю ширину столбца
        self.tableWidget_4.horizontalHeader().resizeSection(1, 385)
        self.tableWidget_4.horizontalHeader().resizeSection(2, 50)
        self.tableWidget_4.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        """Атрибуты таблицы "Запас и стоимость древесины" """
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(66)  # Стандартный размер столбцов
        self.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        """Атрибуты полей с датой"""
        self.dateEdit.setDate(QtCore.QDate.currentDate())
        self.dateEdit_2.setDate(QtCore.QDate.currentDate())

        """Загружаю справочники"""
        c = 1
        self.comboBox_3.addItem('')
        for i in Rank_trf.select().order_by(Rank_trf.name_rank_trf):
            self.comboBox_3.addItem(i.name_rank_trf)
            self.comboBox_3.setItemData(c, i.code_rank_trf, QtCore.Qt.UserRole)
            c += 1
            self.rank_trf[i.name_rank_trf] = i.code_rank_trf

        c = 1
        self.comboBox_4.addItem('')
        for i in Meth_real.select().order_by(Meth_real.name_meth_real):
            self.comboBox_4.addItem(i.name_meth_real)
            self.comboBox_4.setItemData(c, i.code_meth_real, QtCore.Qt.UserRole)
            c += 1
            self.meth_real[i.name_meth_real] = i.code_meth_real

        c = 1
        self.comboBox_5.addItem('')
        for i in Author.select().order_by(Author.name_author):
            # if i.code_author == 22 or i.code_author == 21 or i.code_author == 1:
            if i.code_author == 21:
                self.comboBox_5.addItem(i.name_author)
                self.comboBox_5.setItemData(c, i.code_author, QtCore.Qt.UserRole)
                c += 1
                self.author[i.name_author] = i.code_author

        # self.comboBox.addItem('')
        # dates = []
        # for i in Def_trf_vl.select().order_by(Def_trf_vl.start_date):
        #     if str(i.start_date) not in dates:
        #         dates.append(str(i.start_date))
        # self.comboBox.addItems(dates)

        self.comboBox_7.addItem('')
        c = 1
        for i in Kind_use.select().order_by(Kind_use.name_kind_use):
            self.comboBox_7.addItem(i.name_kind_use)
            self.comboBox_7.setItemData(c, i.code_kind_use, QtCore.Qt.UserRole)
            c += 1
        self.comboBox_7.currentIndexChanged.connect(self.change_wct_meth)

        c = 1
        self.comboBox_6.addItem('')
        for i in Gr_forest.select().order_by(Gr_forest.name_gr_forest):
            self.comboBox_6.addItem(i.name_gr_forest)
            self.comboBox_6.setItemData(c, i.code_gr_forest, QtCore.Qt.UserRole)
            c += 1

        c = 1
        self.comboBox.addItem('')
        for i in Section.select().order_by(Section.name_section):
            self.comboBox.addItem(i.name_section)
            self.comboBox.setItemData(c, i.code_section, QtCore.Qt.UserRole)
            c += 1

        c = 1
        self.comboBox_9.addItem('')
        for i in Acc_meth.select().order_by(Acc_meth.name_acc_meth):
            self.comboBox_9.addItem(i.name_acc_meth)
            self.comboBox_9.setItemData(c, i.code_acc_meth, QtCore.Qt.UserRole)
            c += 1

        c = 1
        self.comboBox_10.addItem('')
        for i in Rgn_meth.select().order_by(Rgn_meth.name_rgn_meth):
            self.comboBox_10.addItem(i.name_rgn_meth)
            self.comboBox_10.setItemData(c, i.code_rgn_meth, QtCore.Qt.UserRole)
            c += 1

        c = 1
        self.comboBox_13.addItem('')
        for i in Status.select().order_by(Status.name_status):
            self.comboBox_13.addItem(i.name_status)
            self.comboBox_13.setItemData(c, i.code_status, QtCore.Qt.UserRole)
            c += 1

        c = 1
        self.comboBox_11.addItem('')
        for i in Bonit.select():
            self.comboBox_11.addItem(i.name_bonit)
            self.comboBox_11.setItemData(c, i.code_bonit, QtCore.Qt.UserRole)
            c += 1

        c = 1
        self.comboBox_12.addItem('')
        for i in Type_for.select().order_by(Type_for.name_type_for):
            self.comboBox_12.addItem(i.name_type_for)
            self.comboBox_12.setItemData(c, i.code_type_for, QtCore.Qt.UserRole)
            c += 1

        c = 1
        self.comboBox_2.addItem('')
        for i in Econ.select().order_by(Econ.name_econ):
            if i.code_econ == 1 or i.code_econ == 2 or i.code_econ == 3:
                self.comboBox_2.addItem(str(i.name_econ))
                self.comboBox_2.setItemData(c, i.code_econ, QtCore.Qt.UserRole)
                c += 1

        self.comboBox_8.currentIndexChanged.connect(self.change_wct_meth_group)

        self.build_restatement_headers()  # Строю заголовки таблицы перечёта
        self.build_not_cutting_headers()  # Строю заголовки таблицы "Рубки не подлежат"
        self.build_wpulp_table()  # Строю заголовки таблицы Объёмов и стоимости

    def build_restatement_headers(self):
        """Создаю заголовок"""
        self.tableWidget.insertRow(0)
        self.tableWidget.insertRow(0)
        self.tableWidget.insertColumn(0)  # первый столбец с диаметрами (не нужен, но удалить нельзя)
        self.tableWidget.hideColumn(0)  # поэтому тут прячу
        # Sets the span of the table element at (row , column ) to the number of rows
        # and columns specified by (rowSpanCount , columnSpanCount ).
        self.tableWidget.setSpan(0, 0, 2, 1)
        # self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem('Кат.\nдиам.'))
        self.tableWidget.setVerticalHeaderItem(0, QtWidgets.QTableWidgetItem('Диам.'))
        self.tableWidget.setVerticalHeaderItem(1, QtWidgets.QTableWidgetItem('см.'))
        """Строю диаметры"""
        # all_dmr = [8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64]
        for i in Settings(group='Diameters', key='dmrs').read_setting():
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.tableWidget.hideRow(self.tableWidget.rowCount() - 1)
            self.tableWidget.setVerticalHeaderItem(self.tableWidget.rowCount() - 1, QtWidgets.QTableWidgetItem(i))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(str(i)))
            # self.tableWidget.item(self.tableWidget.rowCount()-1, 0).setTextAlignment(QtCore.Qt.AlignHCenter)

        """Сумма"""
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        self.tableWidget.setVerticalHeaderItem(self.tableWidget.rowCount() - 1, QtWidgets.QTableWidgetItem('Сумма'))
        self.tableWidget.verticalHeaderItem(self.tableWidget.rowCount() - 1).setBackground(QtGui.QColor('#bdf0ff'))

    def build_not_cutting_headers(self):
        """Создаю заголовок"""
        self.tableWidget_3.insertRow(0)
        self.tableWidget_3.insertColumn(0)
        self.tableWidget_3.insertColumn(0)
        self.tableWidget_3.insertColumn(0)
        self.tableWidget_3.insertColumn(0)
        self.tableWidget_3.setItem(0, 0, QtWidgets.QTableWidgetItem('Порода'))
        self.tableWidget_3.setItem(0, 1, QtWidgets.QTableWidgetItem('Вид семеников'))
        self.tableWidget_3.setItem(0, 2, QtWidgets.QTableWidgetItem('Категория диаметров'))
        self.tableWidget_3.setItem(0, 3, QtWidgets.QTableWidgetItem('Колличество'))

    def build_wpulp_table(self):
        self.tableWidget_2.insertRow(0)
        self.tableWidget_2.insertRow(1)
        self.tableWidget_2.insertRow(2)
        for _ in range(19):
            self.tableWidget_2.insertColumn(_)

        # Sets the span of the table element at (row , column ) to the number of rows
        # and columns specified by (rowSpanCount , columnSpanCount ).
        self.tableWidget_2.setSpan(0, 0, 3, 1)  # Древесная порода
        self.tableWidget_2.setItem(0, 0, QtWidgets.QTableWidgetItem('Порода'))
        self.tableWidget_2.setSpan(0, 1, 3, 1)  # Разряд высоты
        self.tableWidget_2.setItem(0, 1, QtWidgets.QTableWidgetItem('Разряд\nвысот'))
        self.tableWidget_2.setSpan(0, 2, 1, 10)  # Запас древесины, куб. м.
        self.tableWidget_2.setItem(0, 2, QtWidgets.QTableWidgetItem('Запас древесины, куб. м.'))
        self.tableWidget_2.setSpan(1, 2, 1, 3)  # Деловой
        self.tableWidget_2.setItem(1, 2, QtWidgets.QTableWidgetItem('Деловой'))
        self.tableWidget_2.setItem(2, 2, QtWidgets.QTableWidgetItem('Крупная'))
        self.tableWidget_2.setItem(2, 3, QtWidgets.QTableWidgetItem('Средняя'))
        self.tableWidget_2.setItem(2, 4, QtWidgets.QTableWidgetItem('Мелкая'))
        self.tableWidget_2.setSpan(1, 5, 2, 1)  # Итого деловой
        self.tableWidget_2.setItem(1, 5, QtWidgets.QTableWidgetItem('Итого\nделовой'))
        self.tableWidget_2.setSpan(1, 6, 2, 1)  # Дровяной
        self.tableWidget_2.setItem(1, 6, QtWidgets.QTableWidgetItem('Дрова'))
        self.tableWidget_2.setSpan(1, 7, 2, 1)  # Итого ликвида
        self.tableWidget_2.setItem(1, 7, QtWidgets.QTableWidgetItem('Итого\nликвида'))
        self.tableWidget_2.setSpan(1, 8, 2, 1)  # Ликвида из кроны
        self.tableWidget_2.setItem(1, 8, QtWidgets.QTableWidgetItem('Ликвида из\nкроны'))
        self.tableWidget_2.setSpan(1, 9, 2, 1)  # Хвороста (неликвид)
        self.tableWidget_2.setItem(1, 9, QtWidgets.QTableWidgetItem('Хвороста\n(неликвид)'))
        self.tableWidget_2.setSpan(1, 10, 2, 1)  # Отходов
        self.tableWidget_2.setItem(1, 10, QtWidgets.QTableWidgetItem('Отходов'))
        self.tableWidget_2.setSpan(1, 11, 2, 1)  # Всего
        self.tableWidget_2.setItem(1, 11, QtWidgets.QTableWidgetItem('Всего'))
        self.tableWidget_2.setSpan(0, 12, 1, 7)  # Таксовая стоимость, руб.
        self.tableWidget_2.setItem(0, 12, QtWidgets.QTableWidgetItem('Таксовая стоимость, руб.'))
        self.tableWidget_2.setSpan(1, 12, 2, 1)  # Деловой
        self.tableWidget_2.setItem(1, 12, QtWidgets.QTableWidgetItem('Деловой'))
        self.tableWidget_2.setSpan(1, 13, 2, 1)  # Дровяной
        self.tableWidget_2.setItem(1, 13, QtWidgets.QTableWidgetItem('Дрова'))
        self.tableWidget_2.setSpan(1, 14, 2, 1)  # Итого ликвида
        self.tableWidget_2.setItem(1, 14, QtWidgets.QTableWidgetItem('Итого\nликвида'))
        self.tableWidget_2.setSpan(1, 15, 2, 1)  # Ликвида из кроны
        self.tableWidget_2.setItem(1, 15, QtWidgets.QTableWidgetItem('Ликвида\nиз кроны'))
        self.tableWidget_2.setSpan(1, 16, 2, 1)  # Хворост (неликвид)
        self.tableWidget_2.setItem(1, 16, QtWidgets.QTableWidgetItem('Хворост\n(неликвид)'))
        self.tableWidget_2.setSpan(1, 17, 2, 1)  # Отходов
        self.tableWidget_2.setItem(1, 17, QtWidgets.QTableWidgetItem('Отходов'))
        self.tableWidget_2.setSpan(1, 18, 2, 1)  # Всего
        self.tableWidget_2.setItem(1, 18, QtWidgets.QTableWidgetItem('Всего'))

        for column in range(self.tableWidget_2.columnCount()):
            for row in range(self.tableWidget_2.rowCount()):
                if self.tableWidget_2.item(row, column):
                    self.tableWidget_2.item(row, column).setTextAlignment(QtCore.Qt.AlignCenter)

    def build_condition_reduction_table(self):
        for con in Condition_reduction.select():
            self.tableWidget_4.insertRow(self.tableWidget_4.rowCount())
            ch_box = QtWidgets.QCheckBox()
            ch_box.setStyleSheet("margin-left:6%;")
            self.tableWidget_4.setCellWidget(self.tableWidget_4.rowCount() - 1, 0, ch_box)
            self.tableWidget_4.setItem(self.tableWidget_4.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(con.name_condition_reduction))

    def change_wct_meth(self):
        """Метод меняет виды рубок при изменении вида пользования"""
        self.comboBox_8.clear()
        self.comboBox_8.addItem('')
        c = 1
        for i in Wct_meth.select().where(Wct_meth.code_kind_use == self.comboBox_7.itemData(self.comboBox_7.currentIndex(), QtCore.Qt.UserRole)):
            if str(i.code_wct_meth)[-1] == '0':
                self.comboBox_8.addItem(i.name_wct_meth)
                self.comboBox_8.setItemData(c, i.code_wct_meth, QtCore.Qt.UserRole)
                c += 1

    def change_wct_meth_group(self):
        """Метод меняет приём вида рубок при изменении вида рубок"""
        self.comboBox_14.clear()
        index = self.comboBox_8.itemData(self.comboBox_8.currentIndex(), QtCore.Qt.UserRole)  # code_wct_meth
        c = 1
        self.comboBox_14.addItem('нет')
        self.comboBox_14.setItemData(0, index, QtCore.Qt.UserRole)
        if index:
            for i in Wct_meth.select():
                if str(i.code_wct_meth)[0:-1] == str(index)[0:-1] and str(i.code_wct_meth)[-1] != '0':
                    self.comboBox_14.addItem(i.name_wct_meth)
                    self.comboBox_14.setItemData(c, i.code_wct_meth, QtCore.Qt.UserRole)
                    c += 1
