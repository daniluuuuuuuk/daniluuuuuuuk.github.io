from .gui.canvasLayerManagerWidget import Ui_Dialog as layerWidget
from qgis.PyQt.QtWidgets import QDialog, QCheckBox, QSizePolicy
from qgis.core import QgsProject


class LayerManager:
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.widget = layerWidget()
        self.dialog = QDialog()
        self.checkBoxes = []

    def changeLayers(self, checkBoxes):
        names = [
            checkbox.text() for checkbox in checkBoxes if checkbox.isChecked()
        ]
        self.setupCanvasLayers(names)

    def addLayer(self, layer):
        currentCanvasLayers = self.getCanvasLayerNames()
        currentCanvasLayers.append(layer)
        self.setupCanvasLayers(currentCanvasLayers)

    def removeLayer(self, layer):
        currentCanvasLayers = self.getCanvasLayerNames()
        currentCanvasLayers.remove(layer)
        self.setupCanvasLayers(currentCanvasLayers)

    def getCanvasLayerNames(self):
        return [x.name() for x in self.canvas.layers()]

    def getProjectLayerNames(self):
        return [
            x.name() for x in QgsProject.instance().layerTreeRoot().children()
        ]

    def setupCanvasLayers(self, layerNames):
        layer_list = QgsProject.instance().layerTreeRoot().children()
        layers = [
            lyr.layer() for lyr in layer_list if lyr.name() in layerNames
        ]
        self.canvas.setLayers(layers)

    def setupCheckBoxes(self):
        for lr in self.getProjectLayerNames():
            cb = QCheckBox(lr)
            cb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            if lr in self.getCanvasLayerNames():
                cb.setChecked(True)
            self.widget.verticalLayout.addWidget(cb)
            self.checkBoxes.append(cb)

    def initWidget(self):
        self.widget.setupUi(self.dialog)
        self.setupCheckBoxes()
        if self.dialog.exec() == QDialog.Accepted:
            return True
        return False
