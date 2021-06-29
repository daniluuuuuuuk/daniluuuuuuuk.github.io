from .gui.canvasLayerManagerWidget import Ui_Dialog as layerWidget
from qgis.PyQt.QtWidgets import QDialog, QCheckBox, QSizePolicy, QButtonGroup, QRadioButton
from qgis.core import QgsProject, QgsWkbTypes, QgsFeatureRequest
from .tools import GeoOperations as geop

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
            x.name() for x in QgsProject.instance().mapLayers().values()
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


class GPSLayerManager(LayerManager):

    def __init__(self, canvas):
        super().__init__(canvas)
        self.layer = None

    def getProjectLayerNames(self):
        return [
            x.name() for x in QgsProject.instance().mapLayers().values() if x.geometryType() == QgsWkbTypes.PointGeometry
            ]

    def radioClicked(self, btn):
        self.layer = btn.name

    def setupRadioButtons(self):
        self.radioGroup = QButtonGroup()
        for lr in self.getProjectLayerNames():
            radiobutton = QRadioButton(lr)
            radiobutton.name = lr
            radiobutton.setChecked(False)
            self.radioGroup.addButton(radiobutton)
            self.widget.verticalLayout.addWidget(radiobutton)
        self.radioGroup.buttonClicked.connect(self.radioClicked)

    def getPointsOfLayerAsList(self):
        lr = QgsProject.instance().mapLayersByName(self.layer)[0]
        features = self.sortFeaturesByField(lr, 'name')
        return self.getPointsList(features)

    def getPointsList(self, features):
        return [
            [geop.convertToZone35(pt.geometry().asPoint()), 'Лесосека'] for pt in features
        ]

    def sortFeaturesByField(self, layer, field):
        request = QgsFeatureRequest()

        clause = QgsFeatureRequest.OrderByClause(field, ascending=False)
        orderby = QgsFeatureRequest.OrderBy([clause])
        request.setOrderBy(orderby)

        features = layer.getFeatures(request)

        return features

    def initWidget(self):
        self.widget.setupUi(self.dialog)
        self.setupRadioButtons()
        if self.dialog.exec() == QDialog.Accepted:
            return True
        return False