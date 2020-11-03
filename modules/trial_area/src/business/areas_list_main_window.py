from PyQt5 import QtWidgets, uic, QtGui, QtCore
from ..config import BasicDir


class MainWindow(
    QtWidgets.QMainWindow,
    uic.loadUiType(BasicDir().get_basic_dir("gui/areas_list.ui"))[0],
):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        """Применяю стиль"""
        styles = open(BasicDir().get_basic_dir("gui/stylesheets/base.qss"))
        styleData = styles.read()
        styles.close()
        self.setStyleSheet(styleData)
        self.create_table_header()
        """Атрибуты таблицы"""
        self.tableWidget.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSortingEnabled(True)

        self.tableWidget.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        self.tableWidget.horizontalHeader().resizeSection(2, 100)
        self.tableWidget.horizontalHeader().resizeSection(3, 100)
        self.tableWidget.horizontalHeader().resizeSection(4, 150)
        """Атрибуты кнопок"""
        self.pushButton.setIcon(
            QtGui.QIcon(BasicDir().get_basic_dir("gui/images/plus_2.png"))
        )
        self.pushButton.setIconSize(QtCore.QSize(32, 37))

        self.pushButton_2.setIcon(
            QtGui.QIcon(BasicDir().get_basic_dir("gui/images/trash.png"))
        )
        self.pushButton_2.setIconSize(QtCore.QSize(32, 37))

        self.pushButton_3.setIcon(
            QtGui.QIcon(BasicDir().get_basic_dir("gui/images/update.png"))
        )
        self.pushButton_3.setIconSize(QtCore.QSize(32, 37))
        """Атрибуты верхнего меню"""

    def create_table_header(self):
        """Создаю шапку таблицы"""
        # Устанавливаем заголовки таблицы
        headers = [
            "Лесхоз",
            "Лесничество",
            "Квартал",
            "Выдел",
            "Дата",
            "Площадь",
            "UUID",
        ]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
