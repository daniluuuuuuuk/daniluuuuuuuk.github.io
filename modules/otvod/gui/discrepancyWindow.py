# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\NLK\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QgsLes\modules\otvod\ui\discrepancyWindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(414, 118)
        Dialog.setMinimumSize(QtCore.QSize(414, 118))
        Dialog.setMaximumSize(QtCore.QSize(414, 118))
        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 15, 296, 92))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.line_8 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_8.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.gridLayout.addWidget(self.line_8, 5, 4, 1, 1)
        self.linearDiscrepancyMeasured = QtWidgets.QLabel(self.gridLayoutWidget)
        self.linearDiscrepancyMeasured.setText("")
        self.linearDiscrepancyMeasured.setAlignment(QtCore.Qt.AlignCenter)
        self.linearDiscrepancyMeasured.setObjectName("linearDiscrepancyMeasured")
        self.gridLayout.addWidget(self.linearDiscrepancyMeasured, 5, 3, 1, 1)
        self.line_7 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_7.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.gridLayout.addWidget(self.line_7, 3, 4, 1, 1)
        self.line_6 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.gridLayout.addWidget(self.line_6, 4, 1, 1, 5)
        self.line_2 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 1, 2, 1, 1)
        self.line_10 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_10.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_10.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_10.setObjectName("line_10")
        self.gridLayout.addWidget(self.line_10, 1, 0, 5, 1)
        self.maxDiscr = QtWidgets.QLabel(self.gridLayoutWidget)
        self.maxDiscr.setAlignment(QtCore.Qt.AlignCenter)
        self.maxDiscr.setObjectName("maxDiscr")
        self.gridLayout.addWidget(self.maxDiscr, 1, 5, 1, 1)
        self.line = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 1, 1, 5)
        self.linearDiscrName = QtWidgets.QLabel(self.gridLayoutWidget)
        self.linearDiscrName.setAlignment(QtCore.Qt.AlignCenter)
        self.linearDiscrName.setObjectName("linearDiscrName")
        self.gridLayout.addWidget(self.linearDiscrName, 5, 1, 1, 1)
        self.line_11 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_11.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_11.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_11.setObjectName("line_11")
        self.gridLayout.addWidget(self.line_11, 1, 6, 5, 1)
        self.line_9 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_9.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_9.setObjectName("line_9")
        self.gridLayout.addWidget(self.line_9, 6, 1, 1, 5)
        self.angleDiscrName_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.angleDiscrName_2.setAlignment(QtCore.Qt.AlignCenter)
        self.angleDiscrName_2.setObjectName("angleDiscrName_2")
        self.gridLayout.addWidget(self.angleDiscrName_2, 1, 1, 1, 1)
        self.angleDiscrepancyMeasured = QtWidgets.QLabel(self.gridLayoutWidget)
        self.angleDiscrepancyMeasured.setText("")
        self.angleDiscrepancyMeasured.setAlignment(QtCore.Qt.AlignCenter)
        self.angleDiscrepancyMeasured.setObjectName("angleDiscrepancyMeasured")
        self.gridLayout.addWidget(self.angleDiscrepancyMeasured, 3, 3, 1, 1)
        self.maxAngleDiscrepancy = QtWidgets.QLabel(self.gridLayoutWidget)
        self.maxAngleDiscrepancy.setText("")
        self.maxAngleDiscrepancy.setAlignment(QtCore.Qt.AlignCenter)
        self.maxAngleDiscrepancy.setObjectName("maxAngleDiscrepancy")
        self.gridLayout.addWidget(self.maxAngleDiscrepancy, 3, 5, 1, 1)
        self.angleDiscrName = QtWidgets.QLabel(self.gridLayoutWidget)
        self.angleDiscrName.setAlignment(QtCore.Qt.AlignCenter)
        self.angleDiscrName.setObjectName("angleDiscrName")
        self.gridLayout.addWidget(self.angleDiscrName, 3, 1, 1, 1)
        self.line_5 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.gridLayout.addWidget(self.line_5, 5, 2, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 1, 4, 1, 1)
        self.line_4 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout.addWidget(self.line_4, 3, 2, 1, 1)
        self.measuredDiscrName = QtWidgets.QLabel(self.gridLayoutWidget)
        self.measuredDiscrName.setAlignment(QtCore.Qt.AlignCenter)
        self.measuredDiscrName.setObjectName("measuredDiscrName")
        self.gridLayout.addWidget(self.measuredDiscrName, 1, 3, 1, 1)
        self.maxLinearDiscrepancy = QtWidgets.QLabel(self.gridLayoutWidget)
        self.maxLinearDiscrepancy.setText("")
        self.maxLinearDiscrepancy.setAlignment(QtCore.Qt.AlignCenter)
        self.maxLinearDiscrepancy.setObjectName("maxLinearDiscrepancy")
        self.gridLayout.addWidget(self.maxLinearDiscrepancy, 5, 5, 1, 1)
        self.line_12 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_12.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_12.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_12.setObjectName("line_12")
        self.gridLayout.addWidget(self.line_12, 0, 1, 1, 5)
        self.gridLayoutWidget_2 = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(323, 34, 77, 73))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.buttonBox = QtWidgets.QDialogButtonBox(self.gridLayoutWidget_2)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Невязки построения площади"))
        self.maxDiscr.setText(_translate("Dialog", "Допустимая"))
        self.linearDiscrName.setText(_translate("Dialog", "Линейная"))
        self.angleDiscrName_2.setText(_translate("Dialog", "Невязка"))
        self.angleDiscrName.setText(_translate("Dialog", "Угловая"))
        self.measuredDiscrName.setText(_translate("Dialog", "Фактическая"))
        self.label.setText(_translate("Dialog", "Продолжить?"))

