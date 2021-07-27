from qgis.gui import QgsMapToolEmitPoint, QgsMapTool
from PyQt5.QtCore import pyqtSignal, QObject
from qgis.core import QgsProject
from ...tools import GeoOperations
from qgis.core import QgsRectangle
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QRadioButton, QDialogButtonBox, QDialog, QButtonGroup
from PyQt5 import QtCore
# from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox, QComboBox,
#         QMenu, QPushButton, QRadioButton, QVBoxLayout,

class PeekStratumFromMap(QgsMapToolEmitPoint, QObject):
    """Инструмента определения лесосеки с области карты
    """
    signal = pyqtSignal(object)

    def __init__(self, canvas, layerName):
        self.canvas = canvas
        self.layerName = layerName
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def canvasReleaseEvent(self, e):
        layers = QgsProject.instance().mapLayersByName(self.layerName)
        layer = layers[0]
        x = self.toMapCoordinates(e.pos()).x()
        y = self.toMapCoordinates(e.pos()).y()
        radius = 5
        rect = QgsRectangle(x - radius,
                            y - radius,
                            x + radius,
                            y + radius)
        layer.selectByRect(rect, False)
        self.canvas.setCurrentLayer(layer)
        # self.canvas.zoomToSelected()
        features = list(layer.getSelectedFeatures())
        if len(features) > 1:

            self.dialog = MultipleAreaChoiceDialog(features)
            if self.dialog.exec() == QDialog.Accepted:
                self.signal.emit(self.dialog.feature)
            
        elif len(features) == 1:
            self.signal.emit(list(layer.getSelectedFeatures())[0])
        else:
            self.signal.emit(None)
        layer.removeSelection()

    def deactivate(self):
        pass

class MultipleAreaChoiceDialog(QDialog):

    def __init__(self, features, parent=None):
        super(MultipleAreaChoiceDialog, self).__init__(parent)
        self.setWindowTitle("Выберите лесосеку")
        self.feature = None
        self.buttonGroup = QButtonGroup()
        self.features = features
        self.setupUi()
        self.adjustSize()
        self.connectButtons()

    def connectButtons(self):
        i = 0
        for btn in self.buttonGroup.buttons():
            self.buttonGroup.setId(btn, i)
            i += 1
        self.buttonGroup.buttonClicked.connect(self.radioClicked)

    def radioClicked(self, btn):
        idx = self.buttonGroup.id(btn)
        self.feature = self.features[idx]

    def setupUi(self):
        self.resize(311, 509)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.createAreaListGroup())
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def createAreaListGroup(self):
        
        def getFeatAttr(ft):
            name = '№' + ft['num'] + ' ' + 'Кв.' + ft['num_kv'] + ' выд. ' + ft['num_vds']  \
            + ' ' + ft['useType'] + ' - ' + ft['cuttingTyp'] \
            + ' - ' + ft['date'] + ' ' + ft['fio'] + ' ' + ft['info']
            return name

        groupBox = QGroupBox("Список найденных лесосек")
        radios = []
        vbox = QVBoxLayout()
        for ft in self.features:
            radio = QRadioButton(getFeatAttr(ft))
            self.buttonGroup.addButton(radio)
            vbox.addWidget(radio)
            radios.append(radio)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        self.feature = self.features[0]
        radios[0].setChecked(True)
        
        return groupBox