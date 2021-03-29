from ..modules.otvod.tools.tempFeatures.PointBuilder import PointBuilder
from ..modules.otvod.tools.tempFeatures.BindingPointBuilder import BindingPointBuilder
from ..modules.otvod.tools.CoordinateConverter import CoordinateConverter as Converter
from ..modules.otvod.tools.CoordinateFormatConverter import CoordinateFormatConverter as FormatConverter
from ..modules.otvod.LayoutManager import LayoutManager
from ..modules.otvod.tools import GeoOperations
from qgis.utils import iface
from qgis.core import QgsProject, edit, QgsGeometry, QgsCoordinateReferenceSystem
from qgis.core import QgsFillSymbol, QgsVectorLayer, QgsFeature
from PyQt5.QtCore import QVariant
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox, QComboBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QButtonGroup)

class AreaDataPrintContainer:

    def __init__(self, data, points, feature, areaData):
        super().__init__()
        self.bindingPoint = data[1]
        self.uid = data[0]
        self.magneticInclination = data[2]
        self.points = points[0]
        self.feature = feature
        self.areaData = areaData
        self.canvas = iface.mapCanvas()
        self.projectInstance = QgsProject.instance()
        self.columnNames = None
        self.tableList = None

    def makeTableFormat(self, points):
        coordTableList = []
        for key in points:
            point = points[key][0]
            pointWGS = GeoOperations.convertToWgs(point)
            coordX = pointWGS.x()
            coordY = pointWGS.y()
            coordTableList.append([str(key) + "-" + str(key + 1), str(coordY), str(coordX), points[key][1]])
        return coordTableList

    def buildPointsLayer(self):
        bpb = BindingPointBuilder(self.bindingPoint, self.canvas)
        bpb.makeFeature()
        pb = PointBuilder(self.points, self.canvas)
        pb.makeFeature()

    def buildAreaLayer(self):
        self.buildTempLayer('Привязка', 'Линия привязки')
        self.buildTempLayer('Лесосека', 'Лесосеки')

    def deleteTempLayerIfExists(self, layerName):
        layer = self.projectInstance.mapLayersByName(
                layerName)
        if layer:
            self.projectInstance.removeMapLayers([layer[0].id()])
    
    def printLayout(self):
        layout = LayoutManager(self.canvas, QgsProject.instance(), self.uid, int(self.areaData['scale']))
        layout.generate([self.columnNames] + self.tableList)

    def prepareTableForLayout(self):
        tableList = self.makeTableFormat(self.points)
        cvt = Converter(tableList, None, None, self.magneticInclination)
        needFormatConvert = False if self.areaData['format'] == 'Десятичный' else True
        if self.areaData['type'] == 'Координаты':
            self.tableList = tableList
            self.columnNames = ["№", "X, °", "Y, °", "GPS", "Тип"]
            if needFormatConvert:
                ftCvt = FormatConverter(tableList, 0, 1)
                self.tableList = crd = ftCvt.convertToDMS()
                self.columnNames = ["№", "X, °", "X, ′", "X, ″", "Y, °", "Y, ′", "Y, ″", "Тип"]
        elif self.areaData['type'] == 'Азимуты':
            self.tableList = self.convert2az(tableList, cvt, needFormatConvert)
        elif self.areaData['type'] == 'Румбы':
            self.tableList = self.convert2rmb(tableList, cvt, needFormatConvert)
        elif self.areaData['type'] == 'Левые углы':
            self.tableList = self.convert2lft(tableList, cvt, needFormatConvert)
        elif self.areaData['type'] == 'Правые углы':
            self.tableList = self.convert2rgt(tableList, cvt, needFormatConvert)

    def convert2az(self, tableList, cvt, needFormatConvert):
        azth = cvt.convertDDCoord2Azimuth(self.bindingPoint, self.points)
        self.columnNames = ["№", "Угол, °", "Длина линии, м", "Тип"]
        if needFormatConvert:
            ftCvt = FormatConverter(azth, 1, 1)
            azth = ftCvt.convertToDMS()
            self.columnNames = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Тип"]
        return azth

    def convert2rmb(self, tableList, cvt, needFormatConvert):
        rmbs = cvt.convertDDCoord2Rumb(self.bindingPoint, self.points)
        self.columnNames = ["№", "Угол, °", "Длина линии, м", "Румб", "Тип"]
        if needFormatConvert:
            ftCvt = FormatConverter(rmbs, 2, 1)
            rmbs = ftCvt.convertToDMS()
            self.columnNames = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Румб", "Тип"]
        return rmbs

    def convert2lft(self, tableList, cvt, needFormatConvert):
        lft = cvt.convertCoord2Angle(self.bindingPoint, self.points, 3, 0)
        self.columnNames = ["№", "Угол, °", "Длина линии, м", "Тип"]
        if needFormatConvert:
            ftCvt = FormatConverter(lft, 3, 1)
            lft = ftCvt.convertToDMS()        
            self.columnNames = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Тип"]
        return lft

    def convert2rgt(self, tableList, cvt, needFormatConvert):
        rgt = cvt.convertCoord2Angle(self.bindingPoint, self.points, 4, 0)
        self.columnNames = ["№", "Угол, °", "Длина линии, м", "Тип"]
        if needFormatConvert:
            ftCvt = FormatConverter(rgt, 4, 1)
            rgt = ftCvt.convertToDMS()
            self.columnNames = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Тип"]
        return rgt

    def buildTempLayer(self, layerName, sourceLayer):
        self.deleteTempLayerIfExists(layerName)
        if layerName == 'Привязка':
            uri = "linestring?crs=epsg:32635"
            layer = QgsVectorLayer(uri, layerName, "memory")
        if layerName == 'Лесосека':
            uri = "polygon?crs=epsg:32635"
            layer = QgsVectorLayer(uri, layerName, "memory")
            layer.renderer().setSymbol(QgsFillSymbol.createSimple(
            {'color': '255,0,0,100', 'color_border': '0,0,0,255', 'style': 'dense7'}))

        layer.setCrs(QgsCoordinateReferenceSystem(32635))
        self.projectInstance.addMapLayer(layer)

        layers = self.canvas.layers()
        layers.insert(0, layer)

        self.canvas.setLayers(layers)
        self.canvas.refresh()

        self.copyOnLayer(sourceLayer, layerName)

        if self.canvas.isCachingEnabled():
            layer.triggerRepaint()
        else:
            self.canvas.refresh()

    def copyOnLayer(self, sourceLYRName, destLYRName):
        sourceLYR = self.projectInstance.mapLayersByName(sourceLYRName)[0]
        destLYR = self.projectInstance.mapLayersByName(destLYRName)[0]

        feature = list(sourceLYR.getFeatures("uid = '{}'".format(self.uid)))
        if not feature:
            return

        destLYR.startEditing()
        data_provider = destLYR.dataProvider()
        data_provider.addFeatures([feature[0]])
        destLYR.commitChanges()
        iface.messageBar().clearWidgets()

class AreaCoordinatesTypeDialog(QDialog):

    def __init__(self, parent=None):
        super(AreaCoordinatesTypeDialog, self).__init__(parent)
        self.setWindowTitle("Выбор формата данных лесосеки")
        self.coordTypeGroup = QButtonGroup(self)
        self.coordFormatGroup = QButtonGroup(self)
        self.scaleCombobox = None
        self.setupUi()
        self.adjustSize()

    def getPredefinedScales(self):
        return  ['500', '1000', '2500', '5000', '10000', '25000', '50000', '100000']

    def setupUi(self):
        self.resize(311, 509)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        # self.buttonBox.setGeometry(QtCore.QRect(140, 460, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.createCoordTypeGroup())
        self.layout.addWidget(self.createCoordFormatGroup())
        self.layout.addWidget(self.createScaleWidget())
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def createScaleWidget(self):
        groupBox = QGroupBox('Масштаб')
        vbox = QVBoxLayout()
        combo = QComboBox()
        combo.addItems(self.getPredefinedScales())
        combo.setCurrentText('10000')
        vbox.addWidget(combo)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        self.scaleCombobox = combo
        return groupBox

    def createCoordFormatGroup(self):
        groupBox = QGroupBox("Формат данных")
        formatRadio1 = QRadioButton("Десятичный")
        formatRadio2 = QRadioButton("Градусы/минуты/секунды")

        formatRadio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(formatRadio1)
        vbox.addWidget(formatRadio2)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        self.coordFormatGroup.addButton(formatRadio1)
        self.coordFormatGroup.addButton(formatRadio2)
        
        return groupBox

    def createCoordTypeGroup(self):
        groupBox = QGroupBox("Тип данных")
        typeRadio1 = QRadioButton("Координаты")
        typeRadio2 = QRadioButton("Азимуты")
        typeRadio3 = QRadioButton("Румбы")
        typeRadio4 = QRadioButton("Левые углы")
        typeRadio5 = QRadioButton("Правые углы")

        typeRadio1.setChecked(True)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(typeRadio1)
        vbox2.addWidget(typeRadio2)
        vbox2.addWidget(typeRadio3)
        vbox2.addWidget(typeRadio4)
        vbox2.addWidget(typeRadio5)
        vbox2.addStretch(1)
        groupBox.setLayout(vbox2)

        self.coordTypeGroup.addButton(typeRadio1)
        self.coordTypeGroup.addButton(typeRadio2)
        self.coordTypeGroup.addButton(typeRadio3)
        self.coordTypeGroup.addButton(typeRadio4)
        self.coordTypeGroup.addButton(typeRadio5)

        return groupBox
