from qgis.core import QgsPointXY, QgsFeature, QgsVectorLayer, QgsProject, QgsDistanceArea, QgsUnitTypes, QgsGeometry
from qgis.core import QgsCoordinateReferenceSystem, QgsMarkerSymbol, QgsCoordinateTransformContext, QgsFillSymbol
from PyQt5.QtCore import QVariant

class CuttingAreaTemp():

    def __init__(self, canvas, point, features, feature, uid, dictAttr):
        self.uid = uid
        self.canvas = canvas
        self.feature = feature
        self.features = features
        self.point = point
        self.projectInstance = QgsProject.instance()
        self.symbol = self.setLayerSymbol()
        self.properFields = ["num_lch", "num_kv", "num_vds", "area", "leshos"]
        # self.attributes = self.feature.attributes()
        self.dictAttr = dictAttr  # атрибуты лесосеки

        self.fieldsString = self.fieldsToString(self.feature.fields())

        self.attributes = [self.uid] + self.feature.attributes()
        self.fields = self.feature.fields()
        self.attributesDictionary = {**self.attrDict(), **self.dictAttr}

    def attrDict(self):
        dictionary = {}
        dictionary["uid"] = self.uid
        for x in self.fields:
            if x.name() in self.properFields:
                dictionary[x.name()] = self.feature.attribute(x.name())
        return dictionary

    def fieldsToString(self, fields):
        string = "&field=uid"
        for field in fields:
            if str(field.name()) in self.properFields:
                qvariant = QVariant.typeToName(field.type())
                if qvariant == "QString":
                    typeName = "string"
                else:
                    typeName = qvariant
                string = string + "&field=" + \
                    str(field.name()) + ":" + typeName
        for key in self.dictAttr:
            string = string + "&field=" + str(key) + ":string"
        return string

    def setLayerSymbol(self):
        symbol = QgsFillSymbol.createSimple(
            {'color': '255,0,0,100', 'color_border': '0,0,0,255', 'style': 'dense7'})
        return symbol

    def makeFeature(self):

        self.deleteTempLayerIfExists()

        uri = "polygon?crs=epsg:32635" + self.fieldsString

        layer = QgsVectorLayer(uri, "Лесосека временный слой", "memory")
        layer.setCrs(QgsCoordinateReferenceSystem(32635))
        layer.renderer().setSymbol(self.symbol)
        self.projectInstance.addMapLayer(layer)

        feat = QgsFeature()

        feat.setGeometry(QgsGeometry.fromPolygonXY(
            [[self.point] + self.features]))

        da = QgsDistanceArea()
        da.setEllipsoid("WGS84")
        trctxt = QgsCoordinateTransformContext()
        da.setSourceCrs(QgsCoordinateReferenceSystem(32635), trctxt)
        tempArea = da.measurePolygon(feat.geometry().asPolygon()[0])
        area = round(da.convertAreaMeasurement(
            tempArea, QgsUnitTypes.AreaHectares), 1)

        countAttributes = len(self.attributesDictionary)
        feat.initAttributes(countAttributes)

        i = 0
        for key in self.attributesDictionary:
            if key == 'area':
                feat[i] = area
                self.attributesDictionary[key] = feat[i]
            else:
                feat[i] = self.attributesDictionary[key]
            i += 1

        (res, outFeats) = layer.dataProvider().addFeatures([feat])

        layers = self.canvas.layers()
        layers.insert(0, layer)
        self.canvas.setLayers(layers)
        self.canvas.refresh()

        if self.canvas.isCachingEnabled():
            layer.triggerRepaint()
        else:
            self.canvas.refresh()

        return feat

    def deleteTempLayerIfExists(self):
        try:
            layer = self.projectInstance.mapLayersByName(
                "Лесосека временный слой")[0]
            self.projectInstance.removeMapLayers([layer.id()])
        except:
            pass