# -*- coding: utf-8 -*-

# Form implementation generated from reading gui file 'C:\OSGeo4W64\apps\qgis\python\plugins\QgsLes\modules\otvod\gui\lesosekainfo.gui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(320, 367)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 320, 301, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10, 170, 91, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(10, 200, 47, 13))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(10, 240, 91, 16))
        self.label_6.setObjectName("label_6")
        self.fio = QtWidgets.QLineEdit(Dialog)
        self.fio.setGeometry(QtCore.QRect(110, 170, 191, 20))
        self.fio.setObjectName("fio")
        self.info = QtWidgets.QTextEdit(Dialog)
        self.info.setGeometry(QtCore.QRect(110, 240, 191, 71))
        self.info.setObjectName("info")
        self.num = QtWidgets.QLineEdit(Dialog)
        self.num.setGeometry(QtCore.QRect(110, 140, 191, 20))
        self.num.setObjectName("num")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(10, 140, 91, 16))
        self.label_7.setObjectName("label_7")
        self.date = QtWidgets.QDateEdit(Dialog)
        self.date.setGeometry(QtCore.QRect(110, 200, 191, 22))
        self.date.setObjectName("date")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 20, 47, 13))
        self.label.setObjectName("label")
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(10, 50, 71, 16))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(10, 82, 47, 13))
        self.label_9.setObjectName("label_9")
        self.num_kv = QtWidgets.QLineEdit(Dialog)
        self.num_kv.setGeometry(QtCore.QRect(110, 80, 191, 20))
        self.num_kv.setObjectName("num_kv")
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(10, 110, 81, 16))
        self.label_10.setObjectName("label_10")
        self.num_vds = QtWidgets.QLineEdit(Dialog)
        self.num_vds.setGeometry(QtCore.QRect(110, 110, 191, 20))
        self.num_vds.setObjectName("num_vds")
        self.lesnich = QtWidgets.QComboBox(Dialog)
        self.lesnich.setGeometry(QtCore.QRect(110, 50, 191, 22))
        self.lesnich.setEditable(True)
        self.lesnich.setObjectName("lesnich")
        self.leshos = QtWidgets.QComboBox(Dialog)
        self.leshos.setGeometry(QtCore.QRect(110, 20, 191, 22))
        self.leshos.setObjectName("leshos")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Данные лесосеки"))
        self.label_4.setText(_translate("Dialog", "Исполнитель"))
        self.label_5.setText(_translate("Dialog", "Дата"))
        self.label_6.setText(_translate("Dialog", "Дополнительно"))
        self.label_7.setText(_translate("Dialog", "Номер лесосеки"))
        self.label.setText(_translate("Dialog", "Лесхоз"))
        self.label_8.setText(_translate("Dialog", "Лесничество"))
        self.label_9.setText(_translate("Dialog", "Квартал"))
        self.label_10.setText(_translate("Dialog", "Выдел (а)"))

