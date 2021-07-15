from .gui.canvasLayerManagerWidget import Ui_Dialog as layerWidget
from qgis.PyQt.QtWidgets import QDialog, QCheckBox, QSizePolicy, QButtonGroup
from qgis.PyQt.QtWidgets import QRadioButton, QVBoxLayout, QDialogButtonBox, QMessageBox
from qgis.core import QgsProject, QgsWkbTypes, QgsFeatureRequest, QgsMapLayer, QgsField
from qgis.core import edit
from .tools import GeoOperations as geop
from PyQt5.QtCore import QVariant

INT_FIELD_NAME = 'pnum'

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
        layer_list = QgsProject.instance().mapLayers().values()
        layers = [
            lyr for lyr in layer_list if lyr.name() in layerNames
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
        self.layerName = None
        self.layer = None
        self.fieldName = None

    def getProjectLayerNames(self):
        return [
            x.name() for x in QgsProject.instance().mapLayers().values() 
            if x.type() == QgsMapLayer.VectorLayer 
            and x.geometryType() == QgsWkbTypes.PointGeometry
            ]

    def radioClicked(self, btn):
        self.layerName = btn.name
        self.layer = QgsProject.instance().mapLayersByName(btn.name)[0]

    def fieldNameRadioClicked(self, btn):
        self.fieldName = btn.name

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

        espg = self.layer.crs().authid()

        self.setFieldName()

        if not self.fieldName:
            return

        self.createIntegerField(self.layer, self.fieldName)
        self.copyStringToIntegerData(self.layer, self.fieldName)

        features = self.sortFeaturesByField(self.layer)
        return self.getPointsList(features, espg)

    def copyStringToIntegerData(self, layer, fieldName):
        features = layer.getFeatures()
        layer.updateFields()
        idx = layer.fields().indexFromName(INT_FIELD_NAME)
        with edit(layer):
            for feat in features:
                try:
                    feat.setAttribute(idx, int(feat[fieldName]))
                    layer.updateFeature(feat)
                except:
                    QMessageBox.warning(
                        None, "Ошибка", "Некорректное значение номера точки"
                    )
                    return

    def createIntegerField(self, layer, fieldName):
        idx = layer.fields().indexFromName(INT_FIELD_NAME)
        if idx != -1:
            with edit(layer):        
                provider = layer.dataProvider()
                provider.deleteAttributes([idx])
                layer.updateFields()
        with edit(layer):        
            provider = layer.dataProvider()
            provider.addAttributes([QgsField(INT_FIELD_NAME,  QVariant.Int)])
            layer.updateFields()

    def setFieldName(self):
        self.fieldNameDialog = QDialog()
        self.widget.setupUi(self.fieldNameDialog)
        self.fieldNameGroup = QButtonGroup()

        for name in self.layer.fields().names():
            radiobutton = QRadioButton(name)
            radiobutton.name = name
            radiobutton.setChecked(False)
            self.fieldNameGroup.addButton(radiobutton)
            self.widget.verticalLayout.addWidget(radiobutton)

        self.fieldNameGroup.buttonClicked.connect(self.fieldNameRadioClicked)
        self.fieldNameDialog.setWindowTitle('Выберите поле с номерами точек')        
        self.fieldNameDialog.exec()

    def getPointsList(self, features, espg):
        if espg == 'EPSG:32635':
            return [
                [pt.geometry().asPoint(), 'Лесосека'] for pt in features
            ]
        elif espg == 'EPSG:4326':
            return [
                [geop.convertToZone35(pt.geometry().asPoint()), 'Лесосека'] for pt in features
            ]
        else:
            QMessageBox.warning(
                None, "Ошибка", "Импорт слоя в данной системе координат не поддерживается"
            )
            return []

    def sortFeaturesByField(self, layer):
        request = QgsFeatureRequest()

        clause = QgsFeatureRequest.OrderByClause(INT_FIELD_NAME, ascending=True)
        orderby = QgsFeatureRequest.OrderBy([clause])
        request.setOrderBy(orderby)

        features = layer.getFeatures(request)

        return features

    def initWidget(self):
        self.widget.setupUi(self.dialog)
        self.setupRadioButtons()
        self.dialog.setWindowTitle('Выберите слой с точками лесосеки')        
        if self.dialog.exec() == QDialog.Accepted:
            return True
        return False