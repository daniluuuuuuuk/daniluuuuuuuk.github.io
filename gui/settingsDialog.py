# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\omelchuk-ev\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\gisles-for-qgis\ui\settingsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_settingsDialog(object):
    def setupUi(self, settingsDialog):
        settingsDialog.setObjectName("settingsDialog")
        settingsDialog.resize(380, 256)
        self.buttonBox = QtWidgets.QDialogButtonBox(settingsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(60, 220, 301, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.settingsWidget = QtWidgets.QTabWidget(settingsDialog)
        self.settingsWidget.setEnabled(True)
        self.settingsWidget.setGeometry(QtCore.QRect(10, 10, 351, 201))
        self.settingsWidget.setAutoFillBackground(False)
        self.settingsWidget.setObjectName("settingsWidget")
        self.otvodSettings = QtWidgets.QWidget()
        self.otvodSettings.setObjectName("otvodSettings")
        self.reportLabel = QtWidgets.QLabel(self.otvodSettings)
        self.reportLabel.setGeometry(QtCore.QRect(10, 20, 81, 16))
        self.reportLabel.setObjectName("reportLabel")
        self.lineEdit = QtWidgets.QLineEdit(self.otvodSettings)
        self.lineEdit.setGeometry(QtCore.QRect(120, 20, 181, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.toolButton = QtWidgets.QToolButton(self.otvodSettings)
        self.toolButton.setGeometry(QtCore.QRect(314, 20, 21, 20))
        self.toolButton.setObjectName("toolButton")
        self.saveOtvodSettingsButton = QtWidgets.QPushButton(self.otvodSettings)
        self.saveOtvodSettingsButton.setGeometry(QtCore.QRect(260, 140, 75, 23))
        self.saveOtvodSettingsButton.setObjectName("saveOtvodSettingsButton")
        self.label = QtWidgets.QLabel(self.otvodSettings)
        self.label.setGeometry(QtCore.QRect(10, 50, 101, 41))
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.tableType_comboBox = QtWidgets.QComboBox(self.otvodSettings)
        self.tableType_comboBox.setGeometry(QtCore.QRect(120, 60, 211, 22))
        self.tableType_comboBox.setObjectName("tableType_comboBox")
        self.label_2 = QtWidgets.QLabel(self.otvodSettings)
        self.label_2.setGeometry(QtCore.QRect(10, 90, 101, 31))
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.coordType_comboBox = QtWidgets.QComboBox(self.otvodSettings)
        self.coordType_comboBox.setGeometry(QtCore.QRect(120, 100, 211, 22))
        self.coordType_comboBox.setObjectName("coordType_comboBox")
        self.settingsWidget.addTab(self.otvodSettings, "")
        self.mdolSettings = QtWidgets.QWidget()
        self.mdolSettings.setObjectName("mdolSettings")
        self.gplho_label = QtWidgets.QLabel(self.mdolSettings)
        self.gplho_label.setGeometry(QtCore.QRect(10, 40, 101, 16))
        self.gplho_label.setObjectName("gplho_label")
        self.leshoz_label = QtWidgets.QLabel(self.mdolSettings)
        self.leshoz_label.setGeometry(QtCore.QRect(10, 70, 91, 16))
        self.leshoz_label.setObjectName("leshoz_label")
        self.lesnich_label = QtWidgets.QLabel(self.mdolSettings)
        self.lesnich_label.setGeometry(QtCore.QRect(10, 100, 91, 16))
        self.lesnich_label.setObjectName("lesnich_label")
        self.saveEnterpriseSettingsButton = QtWidgets.QPushButton(self.mdolSettings)
        self.saveEnterpriseSettingsButton.setGeometry(QtCore.QRect(260, 140, 75, 23))
        self.saveEnterpriseSettingsButton.setObjectName("saveEnterpriseSettingsButton")
        self.leshoz_comboBox = QtWidgets.QComboBox(self.mdolSettings)
        self.leshoz_comboBox.setGeometry(QtCore.QRect(120, 70, 211, 22))
        self.leshoz_comboBox.setObjectName("leshoz_comboBox")
        self.lesnich_comboBox = QtWidgets.QComboBox(self.mdolSettings)
        self.lesnich_comboBox.setGeometry(QtCore.QRect(120, 100, 211, 22))
        self.lesnich_comboBox.setObjectName("lesnich_comboBox")
        self.gplho_comboBox = QtWidgets.QComboBox(self.mdolSettings)
        self.gplho_comboBox.setGeometry(QtCore.QRect(120, 40, 211, 22))
        self.gplho_comboBox.setObjectName("gplho_comboBox")
        self.location_label = QtWidgets.QLabel(self.mdolSettings)
        self.location_label.setGeometry(QtCore.QRect(10, 10, 101, 16))
        self.location_label.setObjectName("location_label")
        self.locationLineEdit = QtWidgets.QLineEdit(self.mdolSettings)
        self.locationLineEdit.setGeometry(QtCore.QRect(120, 10, 211, 20))
        self.locationLineEdit.setObjectName("locationLineEdit")
        self.settingsWidget.addTab(self.mdolSettings, "")
        self.bdSettings = QtWidgets.QWidget()
        self.bdSettings.setObjectName("bdSettings")
        self.hostLabel = QtWidgets.QLabel(self.bdSettings)
        self.hostLabel.setGeometry(QtCore.QRect(10, 20, 101, 16))
        self.hostLabel.setObjectName("hostLabel")
        self.portLabel = QtWidgets.QLabel(self.bdSettings)
        self.portLabel.setGeometry(QtCore.QRect(10, 50, 47, 13))
        self.portLabel.setObjectName("portLabel")
        self.connectionLineEdit = QtWidgets.QLineEdit(self.bdSettings)
        self.connectionLineEdit.setGeometry(QtCore.QRect(120, 20, 211, 20))
        self.connectionLineEdit.setObjectName("connectionLineEdit")
        self.usernameLabel = QtWidgets.QLabel(self.bdSettings)
        self.usernameLabel.setGeometry(QtCore.QRect(10, 80, 101, 16))
        self.usernameLabel.setObjectName("usernameLabel")
        self.passwordLabel = QtWidgets.QLabel(self.bdSettings)
        self.passwordLabel.setGeometry(QtCore.QRect(10, 110, 47, 13))
        self.passwordLabel.setObjectName("passwordLabel")
        self.portLineEdit = QtWidgets.QLineEdit(self.bdSettings)
        self.portLineEdit.setGeometry(QtCore.QRect(120, 50, 41, 20))
        self.portLineEdit.setObjectName("portLineEdit")
        self.usernameLineEdit = QtWidgets.QLineEdit(self.bdSettings)
        self.usernameLineEdit.setGeometry(QtCore.QRect(120, 80, 211, 20))
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.passwordLineEdit = QtWidgets.QLineEdit(self.bdSettings)
        self.passwordLineEdit.setGeometry(QtCore.QRect(120, 110, 211, 20))
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.saveConfigButton = QtWidgets.QPushButton(self.bdSettings)
        self.saveConfigButton.setGeometry(QtCore.QRect(260, 140, 75, 23))
        self.saveConfigButton.setCheckable(False)
        self.saveConfigButton.setObjectName("saveConfigButton")
        self.testDBConnection_pushButton = QtWidgets.QPushButton(self.bdSettings)
        self.testDBConnection_pushButton.setGeometry(QtCore.QRect(14, 140, 101, 23))
        self.testDBConnection_pushButton.setObjectName("testDBConnection_pushButton")
        self.BDNameLabel = QtWidgets.QLabel(self.bdSettings)
        self.BDNameLabel.setGeometry(QtCore.QRect(170, 50, 47, 13))
        self.BDNameLabel.setObjectName("BDNameLabel")
        self.BDNameLineEdit = QtWidgets.QLineEdit(self.bdSettings)
        self.BDNameLineEdit.setGeometry(QtCore.QRect(210, 50, 121, 20))
        self.BDNameLineEdit.setObjectName("BDNameLineEdit")
        self.importDB_pushButton = QtWidgets.QPushButton(self.bdSettings)
        self.importDB_pushButton.setGeometry(QtCore.QRect(120, 140, 131, 23))
        self.importDB_pushButton.setObjectName("importDB_pushButton")
        self.settingsWidget.addTab(self.bdSettings, "")

        self.retranslateUi(settingsDialog)
        self.settingsWidget.setCurrentIndex(2)
        self.buttonBox.accepted.connect(settingsDialog.accept)
        self.buttonBox.rejected.connect(settingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(settingsDialog)

    def retranslateUi(self, settingsDialog):
        _translate = QtCore.QCoreApplication.translate
        settingsDialog.setWindowTitle(_translate("settingsDialog", "Настройки QgsLes"))
        self.reportLabel.setText(_translate("settingsDialog", "Путь к отчету"))
        self.toolButton.setText(_translate("settingsDialog", "..."))
        self.saveOtvodSettingsButton.setText(_translate("settingsDialog", "Сохранить"))
        self.label.setText(_translate("settingsDialog", "Формат данных"))
        self.label_2.setText(_translate("settingsDialog", "Формат координат"))
        self.settingsWidget.setTabText(self.settingsWidget.indexOf(self.otvodSettings), _translate("settingsDialog", "Отвод лесосек"))
        self.gplho_label.setText(_translate("settingsDialog", "ГПЛХО/ Ведомство"))
        self.leshoz_label.setText(_translate("settingsDialog", "Учреждение"))
        self.lesnich_label.setText(_translate("settingsDialog", "Лесничество"))
        self.saveEnterpriseSettingsButton.setText(_translate("settingsDialog", "Сохранить"))
        self.location_label.setText(_translate("settingsDialog", "Местоположение"))
        self.settingsWidget.setTabText(self.settingsWidget.indexOf(self.mdolSettings), _translate("settingsDialog", "Хозяйство"))
        self.hostLabel.setText(_translate("settingsDialog", "Адрес соединения"))
        self.portLabel.setText(_translate("settingsDialog", "Порт"))
        self.usernameLabel.setText(_translate("settingsDialog", "Имя пользователя"))
        self.passwordLabel.setText(_translate("settingsDialog", "Пароль"))
        self.saveConfigButton.setText(_translate("settingsDialog", "Сохранить"))
        self.testDBConnection_pushButton.setText(_translate("settingsDialog", "Тест соединения"))
        self.BDNameLabel.setText(_translate("settingsDialog", "Имя БД"))
        self.importDB_pushButton.setText(_translate("settingsDialog", "Импортировать БД"))
        self.settingsWidget.setTabText(self.settingsWidget.indexOf(self.bdSettings), _translate("settingsDialog", "База данных"))
