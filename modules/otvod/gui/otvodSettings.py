# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\OSGeo4W64\apps\qgis\python\plugins\QgsLes\modules\otvod\ui\otvodSettings.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(320, 254)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 200, 301, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10, 20, 101, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(10, 50, 101, 16))
        self.label_5.setObjectName("label_5")
        self.tabletype_comboBox = QtWidgets.QComboBox(Dialog)
        self.tabletype_comboBox.setGeometry(QtCore.QRect(130, 20, 171, 22))
        self.tabletype_comboBox.setObjectName("tabletype_comboBox")
        self.coordtype_comboBox = QtWidgets.QComboBox(Dialog)
        self.coordtype_comboBox.setGeometry(QtCore.QRect(130, 50, 171, 22))
        self.coordtype_comboBox.setObjectName("coordtype_comboBox")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 80, 121, 16))
        self.label.setObjectName("label")
        self.magnIncl_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.magnIncl_lineEdit.setGeometry(QtCore.QRect(130, 80, 171, 20))
        self.magnIncl_lineEdit.setObjectName("magnIncl_lineEdit")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Настройки отвода"))
        self.label_4.setText(_translate("Dialog", "Формат координат:"))
        self.label_5.setText(_translate("Dialog", "Формат ввода:"))
        self.label.setText(_translate("Dialog", "Магнитное склонение:"))


