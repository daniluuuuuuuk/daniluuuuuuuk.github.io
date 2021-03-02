from qgis.PyQt.QtWidgets import QMainWindow, QShortcut
from .gui.otvodMainWindow import Ui_MainWindow as otvodMainWindow
from qgis.core import QgsProject
from qgis.utils import iface
from PyQt5.QtGui import QKeySequence
from functools import partial


class MainWindow(QMainWindow, otvodMainWindow):
    def __init__(self, controller):
        QMainWindow.__init__(self)
        otvodMainWindow.__init__(self)
        self.controller = controller
        self.setupUi(self)
        self.initHotKeys()

    def initHotKeys(self):
        self.loadDataFromFile = QShortcut(self)
        self.loadDataFromFile.setKey(QKeySequence("Ctrl+O"))
        self.loadDataFromFile.activated.connect(
            lambda: self.controller.loadDataFromFile()
        )

        self.saveDataToFile = QShortcut(self)
        self.saveDataToFile.setKey(QKeySequence("Ctrl+S"))
        self.saveDataToFile.activated.connect(
            lambda: self.controller.saveDataToFile()
        )

        self.handTool = QShortcut(self)
        self.handTool.setKey(QKeySequence("Ctrl+H"))
        self.handTool.activated.connect(lambda: self.handTool_button.click())

        self.peekFromMap = QShortcut(self)
        self.peekFromMap.setKey(QKeySequence("Ctrl+Q"))
        self.peekFromMap.activated.connect(
            lambda: self.peekFromMap_PushButton.click()
        )

        self.manageLayers = QShortcut(self)
        self.manageLayers.setKey(QKeySequence("Ctrl+L"))
        self.manageLayers.activated.connect(
            lambda: self.manageLayers_button.click()
        )

        self.azimuthTool = QShortcut(self)
        self.azimuthTool.setKey(QKeySequence("Ctrl+A"))
        self.azimuthTool.activated.connect(
            lambda: self.azimuthTool_pushButton.click()
        )

        self.fromMap = QShortcut(self)
        self.fromMap.setKey(QKeySequence("Ctrl+W"))
        self.fromMap.activated.connect(
            lambda: self.lesoseka_from_map_button.click()
        )

        self.fromMapPoints = QShortcut(self)
        self.fromMapPoints.setKey(QKeySequence("Ctrl+E"))
        self.fromMapPoints.activated.connect(
            lambda: self.lesoseka_from_map_points_button.click()
        )

        self.peekVydelFromMap = QShortcut(self)
        self.peekVydelFromMap.setKey(QKeySequence("Ctrl+D"))
        self.peekVydelFromMap.activated.connect(
            lambda: self.peekVydelFromMap_pushButton.click()
        )

        self.buildLesoseka = QShortcut(self)
        self.buildLesoseka.setKey(QKeySequence("Ctrl+B"))
        self.buildLesoseka.activated.connect(
            lambda: self.buildLesoseka_Button.click()
        )

        self.coord = QShortcut(self)
        self.coord.setKey(QKeySequence("Ctrl+1"))
        self.coord.activated.connect(lambda: self.coord_radio_button.click())

        self.azimuth = QShortcut(self)
        self.azimuth.setKey(QKeySequence("Ctrl+2"))
        self.azimuth.activated.connect(
            lambda: self.azimuth_radio_button.click()
        )

        self.rumb = QShortcut(self)
        self.rumb.setKey(QKeySequence("Ctrl+3"))
        self.rumb.activated.connect(lambda: self.rumb_radio_button.click())

        self.leftAngle = QShortcut(self)
        self.leftAngle.setKey(QKeySequence("Ctrl+4"))
        self.leftAngle.activated.connect(
            lambda: self.left_angle_radio_button.click()
        )

        self.rightAngle = QShortcut(self)
        self.rightAngle.setKey(QKeySequence("Ctrl+5"))
        self.rightAngle.activated.connect(
            lambda: self.right_angle_radio_button.click()
        )

        self.reverseSwitchKey = QShortcut(self)
        self.reverseSwitchKey.setKey(QKeySequence("Ctrl+Shift+R"))
        self.reverseSwitchKey.activated.connect(self.reverseSwitch)

        self.incrementInclinationOne = QShortcut(self)
        self.incrementInclinationOne.setKey(QKeySequence("Ctrl+Up"))
        self.incrementInclinationOne.activated.connect(
            partial(self.incrementInclination, 1)
        )

        self.decrementInclinationOne = QShortcut(self)
        self.decrementInclinationOne.setKey(QKeySequence("Ctrl+Down"))
        self.decrementInclinationOne.activated.connect(
            partial(self.decrementInclination, 1)
        )

        self.incrementInclinationMax = QShortcut(self)
        self.incrementInclinationMax.setKey(QKeySequence("Ctrl+Shift+Up"))
        self.incrementInclinationMax.activated.connect(
            partial(self.incrementInclination, 10)
        )

        self.decrementInclinationMax = QShortcut(self)
        self.decrementInclinationMax.setKey(QKeySequence("Ctrl+Shift+Down"))
        self.decrementInclinationMax.activated.connect(
            partial(self.decrementInclination, 10)
        )

        self.addNode = QShortcut(self)
        self.addNode.setKey(QKeySequence("Ctrl++"))
        self.addNode.activated.connect(lambda: self.addNode_button.click())

        self.deleteNode = QShortcut(self)
        self.deleteNode.setKey(QKeySequence("Ctrl+-"))
        self.deleteNode.activated.connect(
            lambda: self.deleteNode_button.click()
        )

    def incrementInclination(self, value):
        if self.controller.tableType == 0:
            return
        currentInclination = self.inclinationSlider.value()
        self.inclinationSlider.setValue(currentInclination + value)

    def decrementInclination(self, value):
        if self.controller.tableType == 0:
            return
        currentInclination = self.inclinationSlider.value()
        self.inclinationSlider.setValue(currentInclination - value)

    def reverseSwitch(self):
        switch = self.switchLayout.itemAt(0).widget()
        if switch.isChecked():
            switch.setChecked(False)
        else:
            switch.setChecked(True)

    def closeEvent(self, event):

        layerNamesToDelete = [
            "Точка привязки",
            "Лесосека временный слой",
            "Опорные точки",
            "Привязка временный слой",
            "Пикеты",
            "Результат обрезки",
            "Выдел лесосеки",
        ]

        for name in layerNamesToDelete:
            layer = QgsProject.instance().mapLayersByName(name)
            if layer:
                QgsProject.instance().removeMapLayers([layer[0].id()])

        iface.mapCanvas().refresh()
        self.deleteLater()
