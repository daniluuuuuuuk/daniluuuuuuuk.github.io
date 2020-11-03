from PyQt5 import QtWidgets, uic, QtGui, QtCore
from ..config import Settings, BasicDir


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

        """Атрибуты верхнего меню"""

    def create_table_header(self):
        """Создаю шапку таблицы"""
        # Устанавливаем заголовки таблицы
        headers = ["Лесничество", "Квартал", "Выдел", "Дата", "UUID"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        self.tableWidget.horizontalHeader().setDefaultSectionSize(252)
