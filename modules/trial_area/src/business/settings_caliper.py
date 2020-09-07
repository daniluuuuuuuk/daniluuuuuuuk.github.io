import sys
import time
import serial.tools.list_ports

from PyQt5 import QtWidgets, uic

from modules.trial_area.src.config import Settings, BasicDir


class Settings_caliper(QtWidgets.QDialog, uic.loadUiType(BasicDir().get_basic_dir("gui/settings_caliper.ui"))[0]):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        styles = open(BasicDir().get_basic_dir("gui/stylesheets/base.qss"))
        self.styleData = styles.read()
        styles.close()
        self.setStyleSheet(self.styleData)

        self.coms = []
        self.comboBox.addItems(Settings(group='Caliper', key='existing_ports').read_setting())
        self.comboBox.setCurrentText(Settings(group='Default_Settings', key='caliper_port').read_setting())
        self.pushButton.clicked.connect(self.update_com_ports)
        self.pushButton_2.clicked.connect(lambda x: [Settings(group='Default_Settings', key='caliper_port').add_setting(
            self.comboBox.currentText()), self.close()])
        self.pushButton_3.clicked.connect(self.test_port)

    def update_com_ports(self):
        for element in serial.tools.list_ports.comports():
            self.coms.append(element.device)

        self.comboBox.clear()
        self.comboBox.addItems(self.coms)
        Settings(group='Caliper', key='existing_ports').add_setting(self.coms)

    def test_port(self):
        try:
            ser = serial.Serial(self.comboBox.currentText(), 9600)
            if ser.getCTS() or self.ser.getDSR():
                QtWidgets.QMessageBox.information(None, 'Успешно', 'Подключение к вилке успешно.')
            else:
                QtWidgets.QMessageBox.critical(None, 'Ошибка', 'Ошибка подключения к вилке')
        except:
            QtWidgets.QMessageBox.critical(None, 'Ошибка', 'Ошибка подключения к вилке')