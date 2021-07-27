from qgis.core import QgsPointXY, QgsProject, edit
from qgis.core import QgsCoordinateReferenceSystem, QgsMarkerSymbol, QgsVectorLayer, QgsFeature, QgsGeometry
from qgis.core import QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings, QgsVectorLayerSimpleLabeling
from PyQt5.QtGui import QFont, QColor

class BindingPointBuilder(QgsPointXY):
    """Реализует нанесение точки привязки
    """
    def __init__(self, point, canvas):
        QgsPointXY.__init__(self, point)
        self.canvas = canvas
        self.projectInstance = QgsProject.instance()
        self.symbol = self.setLayerSymbol()

    def showOnCanvas(self):
        pass

    def setLayerSymbol(self):
        symbol = QgsMarkerSymbol.createSimple(
            {'name': 'circle', 'color': '0,0,0,0', 'outline_color': 'red'})
        return symbol

    def setLayerLabelling(self, layer):
        layer_settings = QgsPalLayerSettings()
        text_format = QgsTextFormat()

        text_format.setFont(QFont("Arial", 12))
        text_format.setSize(10)

        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(0.10)
        buffer_settings.setColor(QColor("black"))

        text_format.setBuffer(buffer_settings)
        layer_settings.setFormat(text_format)

        layer_settings.fieldName = "id"
        layer_settings.placement = 4

        layer_settings.enabled = True

        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        layer.setLabelsEnabled(True)
        layer.setLabeling(layer_settings)
        layer.triggerRepaint()

    def makeFeature(self):

        self.deleteTempLayerIfExists()

        uri = "point?crs=epsg:32635&field=id:integer"

        vl = QgsVectorLayer(uri, "Точка привязки", "memory")
        vl.setCrs(QgsCoordinateReferenceSystem(32635))
        vl.renderer().setSymbol(self.symbol)

        dataProvider = vl.dataProvider()
        vl.startEditing()

        fet = QgsFeature()
        fet.initAttributes(2)
        fet.setGeometry(QgsGeometry.fromPointXY(self))
        fet.setAttribute(0, 0)

        vl.commitChanges()

        dataProvider.addFeatures([fet])
        self.projectInstance.addMapLayer(vl)

        layers = self.canvas.layers()
        layers.insert(0, vl)

        self.setLayerLabelling(vl)

        self.canvas.setLayers(layers)
        self.canvas.refresh()

    def deleteTempLayerIfExists(self):
        try:
            layer = self.projectInstance.mapLayersByName("Точка привязки")[0]
            self.projectInstance.removeMapLayers([layer.id()])
        except:
            # print("Такого слоя нет")
            pass
