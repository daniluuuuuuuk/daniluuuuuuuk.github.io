from qgis.core import QgsPointXY, QgsProject
from qgis.core import QgsCoordinateReferenceSystem, QgsMarkerSymbol, QgsFeature, QgsVectorLayer, QgsGeometry

class AnchorPointBuilder():

    def __init__(self, canvas, feature):
        self.canvas = canvas
        self.feature = feature
        self.projectInstance = QgsProject.instance()
        self.symbol = self.setLayerSymbol()

    def setLayerSymbol(self):
        symbol = QgsMarkerSymbol.createSimple(
            {'name': 'circle', 'color': '0,0,0,0', 'outline_color': '0,0,0,255'})
        return symbol

    def getCoordinatesArray(self):
        geom = self.feature.geometry()
        coordinatesString = str(geom.asWkt())
        pointCoordinates = coordinatesString.replace(
            "MultiPolygon ", "").replace(")))", "").replace("(((", "")
        return pointCoordinates

    def getCoordinatesList(self):
        string = self.getCoordinatesArray()
        listCoords = string.split(", ")
        listXY = []
        for x in listCoords:
            y = x.split(" ")
            listXY.append(y)
        return listXY

    def getCoordinatesXYList(self):
        pointsXY = []
        listCoords = self.getCoordinatesList()
        for pair in listCoords:
            point = QgsPointXY(float(pair[0]), float(pair[1]))
            pointsXY.append(point)
        return pointsXY

    def makeFeature(self):

        self.deleteTempLayerIfExists()

        uri = "point?crs=epsg:32635&field=id:integer"

        vl = QgsVectorLayer(uri, "Опорные точки", "memory")
        vl.setCrs(QgsCoordinateReferenceSystem(32635))
        dataProvider = vl.dataProvider()
        vl.renderer().setSymbol(self.symbol)

        feat = QgsFeature()
        feat.initAttributes(7)
        # feat.setAttribute(6, self.uidForFeature)

        points = self.getCoordinatesXYList()
        for p in points:
            # point = QgsGeometry.fromPointXY(p)
            feat.setGeometry(QgsGeometry.fromPointXY(p))
            (res, outFeats) = vl.dataProvider().addFeatures([feat])
        if self.canvas.isCachingEnabled():
            vl.triggerRepaint()
        else:
            self.canvas.refresh()

        self.projectInstance.addMapLayer(vl)

        layers = self.canvas.layers()
        layers.insert(0, vl)
        self.canvas.setLayers(layers)

    def deleteTempLayerIfExists(self):
        try:
            layer = self.projectInstance.mapLayersByName("Опорные точки")[0]
            self.projectInstance.removeMapLayers([layer.id()])
        except:
            # print("Такого слоя нет")
            pass