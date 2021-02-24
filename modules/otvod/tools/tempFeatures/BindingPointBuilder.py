from qgis.core import QgsPointXY, QgsProject
from qgis.core import QgsCoordinateReferenceSystem, QgsMarkerSymbol, QgsVectorLayer, QgsFeature, QgsGeometry

class BindingPointBuilder(QgsPointXY):

    def __init__(self, point, canvas):
        QgsPointXY.__init__(self, point)
        self.canvas = canvas
        self.projectInstance = QgsProject.instance()
        self.symbol = self.setLayerSymbol()

    def showOnCanvas(self):
        pass

    def setLayerSymbol(self):
        symbol = QgsMarkerSymbol.createSimple(
            {'name': 'circle', 'color': '255,0,0,255', 'outline_color': 'red'})
        return symbol

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

        vl.commitChanges()

        dataProvider.addFeatures([fet])
        self.projectInstance.addMapLayer(vl)

        layers = self.canvas.layers()
        layers.insert(0, vl)
        self.canvas.setLayers(layers)
        self.canvas.refresh()

    def deleteTempLayerIfExists(self):
        try:
            layer = self.projectInstance.mapLayersByName("Точка привязки")[0]
            self.projectInstance.removeMapLayers([layer.id()])
        except:
            # print("Такого слоя нет")
            pass
