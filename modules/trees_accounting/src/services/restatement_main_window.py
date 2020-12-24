from PyQt5 import QtWidgets, uic, QtGui, QtCore
from . import select_species, settings_caliper
from .config import Settings, BasicDir


class MainWindow(
    QtWidgets.QMainWindow,
    uic.loadUiType(BasicDir().get_basic_dir("gui/restatement.ui"))[0],
):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        """Применяю стиль"""
        styles = open(BasicDir().get_basic_dir("gui/stylesheets/base.qss"))
        styleData = styles.read()
        styles.close()
        self.setStyleSheet(styleData)

        """Атрибуты верхнего меню"""
        self.action.triggered.connect(lambda: select_species.Select_species().exec())
        self.action_2.triggered.connect(
            lambda: settings_caliper.Settings_caliper().exec()
        )
        self.action_4.triggered.connect(lambda: self.export_to_xls())
        self.action_3.triggered.connect(lambda: self.export_to_json_lp())

        """Атрибуты кнопок"""
        self.pushButton.clicked.connect(self.save_to_db)
        self.pushButton_2.clicked.connect(self.add_by_caliper)
        self.pushButton_3.clicked.connect(self.add_by_hand)
        self.pushButton_4.clicked.connect(self.delete_one_tree)
        self.pushButton_5.clicked.connect(self.add_one_tree)
        self.pushButton_6.clicked.connect(self.export_to_json)
        self.pushButton_7.clicked.connect(self.import_from_json)
        self.pushButton_8.clicked.connect(self.export_to_xls)

        """Атрибуты таблицы"""
        self.tableWidget.horizontalHeader().setDefaultSectionSize(
            50
        )  # Стандартный ширина столбцов
        self.tableWidget.verticalHeader().setDefaultSectionSize(
            30
        )  # Стандартный высота столбцов
        # self.tableWidget.horizontalHeader().setSectionResizeMode(
        #     QtWidgets.QHeaderView.ResizeToContents)  # растягиваю столбец по контенту
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )  # можно выделять только одну ячейку

        """Атрибуты кнопок"""
        self.pushButton_5.setIcon(
            QtGui.QIcon(BasicDir().get_basic_dir("gui/images/plus_60.png"))
        )
        self.pushButton_5.setIconSize(QtCore.QSize(60, 60))
        self.pushButton_4.setIcon(
            QtGui.QIcon(BasicDir().get_basic_dir("gui/images/minus_60.png"))
        )
        self.pushButton_4.setIconSize(QtCore.QSize(60, 60))
        self.pushButton_8.hide()  # Спрятал временно работу с XLS
        self.pushButton_7.hide()  # Спрятал временно работу с JSON
        self.pushButton_6.hide()  # Спрятал временно работу с JSON

        """Атрибуты полей ввода"""
        area_validator = QtGui.QRegExpValidator(
            QtCore.QRegExp(r"^\d*\.?\d*$"), self.lineEdit
        )
        self.lineEdit.setValidator(area_validator)

        """Создаю заголовок"""
        self.tableWidget.insertRow(0)
        self.tableWidget.insertRow(0)
        self.tableWidget.insertColumn(
            0
        )  # первый столбец с диаметрами (не нужен, но удалить нельзя)
        self.tableWidget.hideColumn(0)  # поэтому тут прячу
        # Sets the span of the table element at (row , column ) to the number of rows
        # and columns specified by (rowSpanCount , columnSpanCount ).
        self.tableWidget.setSpan(0, 0, 2, 1)
        self.tableWidget.setVerticalHeaderItem(0, QtWidgets.QTableWidgetItem("Диам."))
        self.tableWidget.setVerticalHeaderItem(1, QtWidgets.QTableWidgetItem("см."))

        """Строю диаметры"""
        for i in Settings(group="Diameters", key="dmrs").read_setting():
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.tableWidget.hideRow(self.tableWidget.rowCount() - 1)
            self.tableWidget.setItem(
                self.tableWidget.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(i)
            )
            self.tableWidget.setVerticalHeaderItem(
                self.tableWidget.rowCount() - 1, QtWidgets.QTableWidgetItem(i)
            )

        """Сумма"""
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        self.tableWidget.setVerticalHeaderItem(
            self.tableWidget.rowCount() - 1, QtWidgets.QTableWidgetItem("Сумма")
        )
        self.tableWidget.verticalHeaderItem(
            self.tableWidget.rowCount() - 1
        ).setBackground(QtGui.QColor("#bdf0ff"))
