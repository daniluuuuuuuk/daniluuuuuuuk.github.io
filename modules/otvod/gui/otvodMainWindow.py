# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\NLK\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\trial_area\modules\otvod\ui\otvodMainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(825, 455)
        MainWindow.setMinimumSize(QtCore.QSize(825, 455))
        MainWindow.setMaximumSize(QtCore.QSize(825, 455))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.bindingPoint_Label = QtWidgets.QLabel(self.centralwidget)
        self.bindingPoint_Label.setGeometry(QtCore.QRect(10, 10, 101, 16))
        self.bindingPoint_Label.setObjectName("bindingPoint_Label")
        self.x_coord_LineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.x_coord_LineEdit.setGeometry(QtCore.QRect(140, 10, 101, 20))
        self.x_coord_LineEdit.setObjectName("x_coord_LineEdit")
        self.y_coord_LineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.y_coord_LineEdit.setGeometry(QtCore.QRect(270, 10, 101, 20))
        self.y_coord_LineEdit.setObjectName("y_coord_LineEdit")
        self.x_Label = QtWidgets.QLabel(self.centralwidget)
        self.x_Label.setGeometry(QtCore.QRect(120, 10, 16, 16))
        self.x_Label.setObjectName("x_Label")
        self.y_Label = QtWidgets.QLabel(self.centralwidget)
        self.y_Label.setGeometry(QtCore.QRect(250, 10, 16, 16))
        self.y_Label.setObjectName("y_Label")
        self.peekFromMap_PushButton = QtWidgets.QPushButton(self.centralwidget)
        self.peekFromMap_PushButton.setGeometry(QtCore.QRect(380, 10, 21, 21))
        self.peekFromMap_PushButton.setText("")
        self.peekFromMap_PushButton.setCheckable(True)
        self.peekFromMap_PushButton.setObjectName("peekFromMap_PushButton")
        self.peekFromGPSPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.peekFromGPSPushButton.setGeometry(QtCore.QRect(410, 10, 21, 21))
        self.peekFromGPSPushButton.setText("")
        self.peekFromGPSPushButton.setObjectName("peekFromGPSPushButton")
        self.deleteNode_button = QtWidgets.QToolButton(self.centralwidget)
        self.deleteNode_button.setGeometry(QtCore.QRect(5, 100, 21, 21))
        self.deleteNode_button.setObjectName("deleteNode_button")
        self.addNode_button = QtWidgets.QToolButton(self.centralwidget)
        self.addNode_button.setGeometry(QtCore.QRect(5, 70, 21, 21))
        self.addNode_button.setObjectName("addNode_button")
        self.clearNodes_button = QtWidgets.QPushButton(self.centralwidget)
        self.clearNodes_button.setGeometry(QtCore.QRect(5, 190, 21, 21))
        self.clearNodes_button.setObjectName("clearNodes_button")
        self.canvasWidget = QtWidgets.QWidget(self.centralwidget)
        self.canvasWidget.setGeometry(QtCore.QRect(440, 40, 371, 341))
        self.canvasWidget.setObjectName("canvasWidget")
        self.sliderLabel = QtWidgets.QLabel(self.centralwidget)
        self.sliderLabel.setGeometry(QtCore.QRect(690, 390, 21, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.sliderLabel.setFont(font)
        self.sliderLabel.setObjectName("sliderLabel")
        self.canvas_scale_combo = QtWidgets.QComboBox(self.centralwidget)
        self.canvas_scale_combo.setGeometry(QtCore.QRect(730, 350, 71, 22))
        self.canvas_scale_combo.setObjectName("canvas_scale_combo")
        self.azimuthTool_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.azimuthTool_pushButton.setGeometry(QtCore.QRect(530, 10, 21, 21))
        self.azimuthTool_pushButton.setText("")
        self.azimuthTool_pushButton.setCheckable(True)
        self.azimuthTool_pushButton.setChecked(False)
        self.azimuthTool_pushButton.setObjectName("azimuthTool_pushButton")
        self.outputLabel = QtWidgets.QLabel(self.centralwidget)
        self.outputLabel.setGeometry(QtCore.QRect(440, 389, 251, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.outputLabel.setFont(font)
        self.outputLabel.setText("")
        self.outputLabel.setObjectName("outputLabel")
        self.tableWidget = QtWidgets.QWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(30, 40, 401, 341))
        self.tableWidget.setObjectName("tableWidget")
        self.peekVydelFromMap_pushButton = QtWidgets.QPushButton(
            self.centralwidget
        )
        self.peekVydelFromMap_pushButton.setGeometry(
            QtCore.QRect(500, 10, 21, 21)
        )
        self.peekVydelFromMap_pushButton.setText("")
        self.peekVydelFromMap_pushButton.setCheckable(True)
        self.peekVydelFromMap_pushButton.setObjectName(
            "peekVydelFromMap_pushButton"
        )
        self.lesoseka_from_map_button = QtWidgets.QPushButton(
            self.centralwidget
        )
        self.lesoseka_from_map_button.setGeometry(
            QtCore.QRect(560, 10, 21, 21)
        )
        self.lesoseka_from_map_button.setText("")
        self.lesoseka_from_map_button.setCheckable(True)
        self.lesoseka_from_map_button.setObjectName("lesoseka_from_map_button")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(346, 390, 81, 21))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.switchPadLayout = QtWidgets.QHBoxLayout(
            self.horizontalLayoutWidget
        )
        self.switchPadLayout.setContentsMargins(0, 0, 0, 0)
        self.switchPadLayout.setObjectName("switchPadLayout")
        self.label_3 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.switchPadLayout.addWidget(self.label_3)
        self.switchLayout = QtWidgets.QHBoxLayout()
        self.switchLayout.setObjectName("switchLayout")
        self.switchPadLayout.addLayout(self.switchLayout)
        self.label_2 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.switchPadLayout.addWidget(self.label_2)
        self.exportAsImage_PushButton = QtWidgets.QPushButton(
            self.centralwidget
        )
        self.exportAsImage_PushButton.setGeometry(
            QtCore.QRect(620, 10, 21, 21)
        )
        self.exportAsImage_PushButton.setText("")
        self.exportAsImage_PushButton.setCheckable(False)
        self.exportAsImage_PushButton.setObjectName("exportAsImage_PushButton")
        self.lesoseka_from_map_points_button = QtWidgets.QPushButton(
            self.centralwidget
        )
        self.lesoseka_from_map_points_button.setGeometry(
            QtCore.QRect(590, 10, 21, 21)
        )
        self.lesoseka_from_map_points_button.setText("")
        self.lesoseka_from_map_points_button.setCheckable(True)
        self.lesoseka_from_map_points_button.setObjectName(
            "lesoseka_from_map_points_button"
        )
        self.inclinationSlider = QtWidgets.QSlider(self.centralwidget)
        self.inclinationSlider.setGeometry(QtCore.QRect(710, 390, 71, 22))
        self.inclinationSlider.setMinimum(-200)
        self.inclinationSlider.setMaximum(200)
        self.inclinationSlider.setSingleStep(1)
        self.inclinationSlider.setPageStep(5)
        self.inclinationSlider.setProperty("value", 0)
        self.inclinationSlider.setSliderPosition(0)
        self.inclinationSlider.setTracking(False)
        self.inclinationSlider.setOrientation(QtCore.Qt.Horizontal)
        self.inclinationSlider.setInvertedAppearance(False)
        self.inclinationSlider.setInvertedControls(False)
        self.inclinationSlider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.inclinationSlider.setTickInterval(100)
        self.inclinationSlider.setObjectName("inclinationSlider")
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_3.setGeometry(
            QtCore.QRect(30, 390, 296, 21)
        )
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(
            self.horizontalLayoutWidget_3
        )
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.coord_radio_button = QtWidgets.QRadioButton(
            self.horizontalLayoutWidget_3
        )
        self.coord_radio_button.setObjectName("coord_radio_button")
        self.horizontalLayout_2.addWidget(self.coord_radio_button)
        self.azimuth_radio_button = QtWidgets.QRadioButton(
            self.horizontalLayoutWidget_3
        )
        self.azimuth_radio_button.setObjectName("azimuth_radio_button")
        self.horizontalLayout_2.addWidget(self.azimuth_radio_button)
        self.rumb_radio_button = QtWidgets.QRadioButton(
            self.horizontalLayoutWidget_3
        )
        self.rumb_radio_button.setObjectName("rumb_radio_button")
        self.horizontalLayout_2.addWidget(self.rumb_radio_button)
        self.left_angle_radio_button = QtWidgets.QRadioButton(
            self.horizontalLayoutWidget_3
        )
        self.left_angle_radio_button.setObjectName("left_angle_radio_button")
        self.horizontalLayout_2.addWidget(self.left_angle_radio_button)
        self.right_angle_radio_button = QtWidgets.QRadioButton(
            self.horizontalLayoutWidget_3
        )
        self.right_angle_radio_button.setObjectName("right_angle_radio_button")
        self.horizontalLayout_2.addWidget(self.right_angle_radio_button)
        self.handTool_button = QtWidgets.QPushButton(self.centralwidget)
        self.handTool_button.setGeometry(QtCore.QRect(440, 10, 21, 21))
        self.handTool_button.setText("")
        self.handTool_button.setObjectName("handTool_button")
        self.manageLayers_button = QtWidgets.QPushButton(self.centralwidget)
        self.manageLayers_button.setGeometry(QtCore.QRect(470, 10, 21, 21))
        self.manageLayers_button.setText("")
        self.manageLayers_button.setObjectName("manageLayers_button")
        self.generateReport_Button = QtWidgets.QPushButton(self.centralwidget)
        self.generateReport_Button.setGeometry(QtCore.QRect(770, 10, 21, 21))
        self.generateReport_Button.setText("")
        self.generateReport_Button.setObjectName("generateReport_Button")
        self.buildLesoseka_Button = QtWidgets.QPushButton(self.centralwidget)
        self.buildLesoseka_Button.setGeometry(QtCore.QRect(650, 10, 21, 21))
        self.buildLesoseka_Button.setText("")
        self.buildLesoseka_Button.setObjectName("buildLesoseka_Button")
        self.editAttributes_button = QtWidgets.QPushButton(self.centralwidget)
        self.editAttributes_button.setGeometry(QtCore.QRect(680, 10, 21, 21))
        self.editAttributes_button.setText("")
        self.editAttributes_button.setObjectName("editAttributes_button")
        self.deleteLesoseka_Button = QtWidgets.QPushButton(self.centralwidget)
        self.deleteLesoseka_Button.setGeometry(QtCore.QRect(740, 10, 21, 21))
        self.deleteLesoseka_Button.setText("")
        self.deleteLesoseka_Button.setObjectName("deleteLesoseka_Button")
        self.saveLesoseka_Button = QtWidgets.QPushButton(self.centralwidget)
        self.saveLesoseka_Button.setGeometry(QtCore.QRect(710, 10, 21, 21))
        self.saveLesoseka_Button.setText("")
        self.saveLesoseka_Button.setObjectName("saveLesoseka_Button")
        self.saveData_pushButton = QtWidgets.QToolButton(self.centralwidget)
        self.saveData_pushButton.setGeometry(QtCore.QRect(5, 130, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.saveData_pushButton.setFont(font)
        self.saveData_pushButton.setText("")
        self.saveData_pushButton.setObjectName("saveData_pushButton")
        self.loadData_pushButton = QtWidgets.QToolButton(self.centralwidget)
        self.loadData_pushButton.setGeometry(QtCore.QRect(5, 160, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.loadData_pushButton.setFont(font)
        self.loadData_pushButton.setText("")
        self.loadData_pushButton.setObjectName("loadData_pushButton")
        self.magneticDeclination_pushButton = QtWidgets.QPushButton(
            self.centralwidget
        )
        self.magneticDeclination_pushButton.setGeometry(
            QtCore.QRect(790, 390, 21, 21)
        )
        self.magneticDeclination_pushButton.setText("")
        self.magneticDeclination_pushButton.setObjectName(
            "magneticDeclination_pushButton"
        )
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setEnabled(True)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 825, 21))
        self.menubar.setObjectName("menubar")
        self.menu_3 = QtWidgets.QMenu(self.menubar)
        self.menu_3.setObjectName("menu_3")
        self.menu_info = QtWidgets.QMenu(self.menubar)
        self.menu_info.setEnabled(True)
        self.menu_info.setObjectName("menu_info")
        MainWindow.setMenuBar(self.menubar)
        self.action = QtWidgets.QAction(MainWindow)
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction(MainWindow)
        self.action_2.setObjectName("action_2")
        self.otvodSettingsAction = QtWidgets.QAction(MainWindow)
        self.otvodSettingsAction.setObjectName("otvodSettingsAction")
        self.saveData_action = QtWidgets.QAction(MainWindow)
        self.saveData_action.setObjectName("saveData_action")
        self.loadData_action = QtWidgets.QAction(MainWindow)
        self.loadData_action.setObjectName("loadData_action")
        self.menu_3.addAction(self.saveData_action)
        self.menu_3.addAction(self.loadData_action)
        self.menubar.addAction(self.menu_3.menuAction())
        self.menubar.addAction(self.menu_info.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(
            _translate("MainWindow", "Модуль отвода лесосеки")
        )
        self.bindingPoint_Label.setText(
            _translate("MainWindow", "Точка привязки:")
        )
        self.x_Label.setText(_translate("MainWindow", "N:"))
        self.y_Label.setText(_translate("MainWindow", "E:"))
        self.peekFromMap_PushButton.setToolTip(
            _translate("MainWindow", "Выбрать точку на карте (Ctrl+Q)")
        )
        self.peekFromGPSPushButton.setToolTip(
            _translate("MainWindow", "Точка привязки по GPS")
        )
        self.deleteNode_button.setToolTip(
            _translate("MainWindow", "Удалить последнюю точку (Ctrl + -)")
        )
        self.deleteNode_button.setText(_translate("MainWindow", "-"))
        self.addNode_button.setToolTip(
            _translate("MainWindow", "Добавить точку (Ctrl + +)")
        )
        self.addNode_button.setText(_translate("MainWindow", "+"))
        self.clearNodes_button.setToolTip(
            _translate("MainWindow", "Удалить все узлы")
        )
        self.clearNodes_button.setText(_translate("MainWindow", "✕"))
        self.sliderLabel.setText(_translate("MainWindow", "0"))
        self.azimuthTool_pushButton.setToolTip(
            _translate("MainWindow", "Измерение расстояния и азимута (Ctrl+A)")
        )
        self.peekVydelFromMap_pushButton.setToolTip(
            _translate("MainWindow", "Загрузить данные лесосеки")
        )
        self.lesoseka_from_map_button.setToolTip(
            _translate("MainWindow", "Вынос по границам выдела (Ctrl+W)")
        )
        self.label_3.setToolTip(
            _translate(
                "MainWindow",
                "Decimal Degrees (Десятичный формат) (Ctrl+Shift+R)",
            )
        )
        self.label_3.setText(_translate("MainWindow", "DD"))
        self.label_2.setToolTip(
            _translate(
                "MainWindow",
                "Degrees Minutes Seconds (Градусы, Минуты, Секунды) (Ctrl+Shift+R)",
            )
        )
        self.label_2.setText(_translate("MainWindow", "DMS"))
        self.exportAsImage_PushButton.setToolTip(
            _translate("MainWindow", "Экспортировать как изображение")
        )
        self.lesoseka_from_map_points_button.setToolTip(
            _translate("MainWindow", "Вынос по произвольным точкам (Ctrl+E)")
        )
        self.inclinationSlider.setToolTip(
            _translate(
                "MainWindow",
                "Магнитное склонение (Ctrl+Вниз/Вверх, Ctrl+Shift+Вниз/Вверх)",
            )
        )
        self.coord_radio_button.setToolTip(
            _translate("MainWindow", "Координаты (Ctrl+1)")
        )
        self.coord_radio_button.setText(_translate("MainWindow", "КРД"))
        self.azimuth_radio_button.setToolTip(
            _translate("MainWindow", "Азимуты (Ctrl+2)")
        )
        self.azimuth_radio_button.setText(_translate("MainWindow", "АЗТ"))
        self.rumb_radio_button.setToolTip(
            _translate("MainWindow", "Румбы (Ctrl+3)")
        )
        self.rumb_radio_button.setText(_translate("MainWindow", "РМБ"))
        self.left_angle_radio_button.setToolTip(
            _translate("MainWindow", "Левые внутренние углы (Ctrl+4)")
        )
        self.left_angle_radio_button.setText(_translate("MainWindow", "ЛВУ"))
        self.right_angle_radio_button.setToolTip(
            _translate("MainWindow", "Правые внутернние углы (Ctrl + 5)")
        )
        self.right_angle_radio_button.setText(_translate("MainWindow", "ПВУ"))
        self.handTool_button.setToolTip(
            _translate("MainWindow", "Навигация по карте (Ctrl+H)")
        )
        self.manageLayers_button.setToolTip(
            _translate("MainWindow", "Настроить видимость слоев (Ctrl+L)")
        )
        self.generateReport_Button.setToolTip(
            _translate("MainWindow", "Сформировать отчет")
        )
        self.buildLesoseka_Button.setToolTip(
            _translate("MainWindow", "Построить лесосеку (Ctrl+B)")
        )
        self.editAttributes_button.setToolTip(
            _translate("MainWindow", "Редактировать атрибуты")
        )
        self.deleteLesoseka_Button.setToolTip(
            _translate("MainWindow", "Удалить лесосеку")
        )
        self.saveLesoseka_Button.setToolTip(
            _translate("MainWindow", "Сохранить лесосеку")
        )
        self.saveData_pushButton.setToolTip(
            _translate(
                "MainWindow", "Сохранить данные отвода в файл (Ctrl + S)"
            )
        )
        self.loadData_pushButton.setToolTip(
            _translate("MainWindow", "Загрузить данные из файла (Ctrl + O)")
        )
        self.magneticDeclination_pushButton.setToolTip(
            _translate(
                "MainWindow",
                "Магнитное склонение по данным всемирной магнитной модели сервиса NOAA\n"
                " Satellite and Information Service центра National Geophysical Data Center",
            )
        )
        self.menu_3.setTitle(_translate("MainWindow", "Данные отвода"))
        self.menu_info.setTitle(_translate("MainWindow", "Справка"))
        self.action.setText(_translate("MainWindow", "Сохранить"))
        self.action_2.setText(_translate("MainWindow", "Загрузить"))
        self.otvodSettingsAction.setText(_translate("MainWindow", "Параметры"))
        self.saveData_action.setText(
            _translate("MainWindow", "Сохранить (Ctrl+S)")
        )
        self.loadData_action.setText(
            _translate("MainWindow", "Загрузить (Ctrl+O)")
        )
