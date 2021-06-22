from qgis.core import QgsProject, QgsFillSymbol, QgsVectorLayer, QgsCoordinateReferenceSystem


class CuttingAreaBuilder():

    def __init__(self, canvas, feature):
        self.canvas = canvas
        self.feature = feature
        self.projectInstance = QgsProject.instance()
        self.symbol = self.setLayerSymbol()

    def setLayerSymbol(self):
        symbol = QgsFillSymbol.createSimple(
            {'color': '0,0,0,0', 'color_border': '0,0,0,255', 'style': 'dense5', 'width_border':'0.6'})
        return symbol

    def makeFeature(self):

        self.deleteTempLayerIfExists()

        uri = "polygon?crs=epsg:32635&field=id:integer"

        vl = QgsVectorLayer(uri, "Выдел лесосеки", "memory")
        vl.setCrs(QgsCoordinateReferenceSystem(32635))
        vl.renderer().setSymbol(self.symbol)

        dataProvider = vl.dataProvider()

        vl.startEditing()
        dataProvider.addFeatures([self.feature])
        vl.commitChanges()

        self.projectInstance.addMapLayer(vl)

        layers = self.canvas.layers()
        layers.insert(0, vl)
        self.canvas.setLayers(layers)

    def deleteTempLayerIfExists(self):
        try:
            layer = self.projectInstance.mapLayersByName("Выдел лесосеки")[0]
            self.projectInstance.removeMapLayers([layer.id()])
        except:
            # print("Такого слоя нет")
            pass
