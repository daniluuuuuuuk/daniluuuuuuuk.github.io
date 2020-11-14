from PyQt5 import QtWidgets, uic, QtGui, QtCore
from .config import BasicDir
from ..models.nri import Organization


class MainWindow(
    QtWidgets.QMainWindow,
    uic.loadUiType(BasicDir().get_basic_dir("gui/area_property.ui"))[0],
):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        """Применяю стиль"""
        styles = open(BasicDir().get_basic_dir("gui/stylesheets/base.qss"))
        self.styleData = styles.read()
        styles.close()
        self.setStyleSheet(self.styleData)
        self.get_gplho()
        self.comboBox.currentIndexChanged.connect(self.get_enterprise)
        self.comboBox_2.currentIndexChanged.connect(self.get_forestry)
        self.pushButton.clicked.connect(self.create_area)

    def get_gplho(self):
        """Получаю список ГПЛХО и их код => добавляю в comboBox"""
        self.comboBox.addItem("")
        orgs = Organization.select(
            Organization.id_organization, Organization.name_organization
        ).where(Organization.type_organization == "ГПЛХО")
        for org in orgs:
            self.comboBox.addItem(org.name_organization, userData=org.id_organization)

    def get_enterprise(self):
        """Получаю список Лесхозов и их код => добавляю в comboBox_2"""
        self.comboBox_2.clear()
        self.comboBox_2.addItem("")
        orgs = Organization.select(
            Organization.id_organization, Organization.name_organization
        ).where(Organization.parent_id_organization == self.comboBox.currentData())

        for org in orgs:
            self.comboBox_2.addItem(org.name_organization, userData=org.id_organization)

    def get_forestry(self):
        """Получаю список Лесничеств и их код => добавляю в comboBox_3"""
        self.comboBox_3.clear()
        self.comboBox_3.addItem("")
        orgs = Organization.select(
            Organization.id_organization, Organization.name_organization
        ).where(Organization.parent_id_organization == self.comboBox_2.currentData())

        for org in orgs:
            self.comboBox_3.addItem(org.name_organization, userData=org.id_organization)
