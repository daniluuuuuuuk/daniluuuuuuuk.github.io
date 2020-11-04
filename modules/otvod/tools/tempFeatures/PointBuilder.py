from qgis.core import QgsProject, QgsMarkerSymbol, QgsPalLayerSettings, QgsTextFormat, QgsVectorLayer
from qgis.core import QgsTextBufferSettings, QgsVectorLayerSimpleLabeling, QgsFeature, QgsGeometry
from PyQt5.QtGui import QFont, QColor

class PointBuilder():

    def __init__(self, pointsDict, canvas):
        self.pointsDict = pointsDict
        self.canvas = canvas
        self.projectInstance = QgsProject.instance()
        self.symbol = self.setLayerSymbol()

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

    def showOnCanvas(self, key, point, pointType):
        fet = QgsFeature()
        fet.initAttributes(2)
        attributes = [key, str(pointType)]
        fet.setAttributes(attributes)
        try:
            fet.setGeometry(QgsGeometry.fromPointXY(point))
            return fet
        except Exception as e:
            print(e)

    def makeFeature(self):
        self.deleteTempLayerIfExists()

        uri = "point?crs=epsg:32635&field=id:integer&field=type:string"
        vl = QgsVectorLayer(uri, "Пикеты", "memory")

        vl.renderer().setSymbol(self.symbol)
        self.setLayerLabelling(vl)

        dataProvider = vl.dataProvider()

        features = []
        i = 0
        for key in self.pointsDict:
            i += 1
            point = self.pointsDict[key][0]
            pointType = self.pointsDict[key][1]
            features.append(self.showOnCanvas(i, point, pointType))

        vl.startEditing()
        dataProvider.addFeatures(features)
        vl.commitChanges()

        self.projectInstance.addMapLayer(vl)

        layers = self.canvas.layers()
        layers.insert(0, vl)
        self.canvas.setLayers(layers)
        self.canvas.refresh()

    def deleteTempLayerIfExists(self):
        try:
            layer = self.projectInstance.mapLayersByName("Пикеты")[0]
            self.projectInstance.removeMapLayers([layer.id()])
            self.canvas.refresh()
        except:
            pass
