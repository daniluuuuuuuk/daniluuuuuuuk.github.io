from qgis.core import QgsProject, QgsGeometry, QgsCoordinateReferenceSystem
from qgis.core import QgsFillSymbol, QgsVectorLayer, QgsFeature
from PyQt5.QtCore import QVariant


class AnchorLineTemp():

    def __init__(self, canvas, point, features, feature, uid, dictAttr):

        self.uid = uid
        self.canvas = canvas
        self.feature = feature
        self.features = features
        self.point = point
        self.projectInstance = QgsProject.instance()
        self.symbol = self.setLayerSymbol()
        self.properFields = ["num_lch", "num_kv", "num_vd", "area", "leshos"]
        # self.attributes = self.feature.attributes()
        self.dictAttr = dictAttr  # атрибуты лесосеки

        self.fieldsString = self.fieldsToString(self.feature.fields())

        self.attributes = [self.uid] + self.feature.attributes()
        self.fields = self.feature.fields()
        self.attributesDictionary = {**self.attrDict(), **self.dictAttr}
        # self.feature = feature
        # self.uid = uid
        # self.point = point
        # self.canvas = canvas
        # self.features = features
        # self.dictAttr = dictAttr
        # self.projectInstance = QgsProject.instance()
        # self.symbol = self.setLayerSymbol()
        # self.attributes = self.feature.attributes()
        # self.fieldsString = self.fieldsToString(self.feature.fields())

        # self.attributes = [self.uid] + self.feature.attributes()
        # self.fields = self.feature.fields()
        # self.attributesDictionary = {**self.attrDict(), **self.dictAttr}

    # def attrDict(self):
    #     dictionary = {}
    #     dictionary["uid"] = self.uid
    #     for x in self.fields:
    #         dictionary[x.name()] = self.feature.attribute(x.name())
    #     return dictionary

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

    # def fieldsToString(self, fields):
    #     string = "&field=uid"
    #     for field in fields:
    #         qvariant = QVariant.typeToName(field.type())
    #         if qvariant == "QString":
    #             typeName = "string"
    #         else:
    #             typeName = qvariant
    #         string = string + "&field=" + str(field.name()) + ":" + typeName
    #     for key in self.dictAttr:
    #         string = string + "&field=" + str(key) + ":string"
    #     return string

    def setLayerSymbol(self):
        symbol = QgsFillSymbol.createSimple(
            {'color': '255,0,0,100', 'color_border': '0,0,0,255'})
        return symbol

    def makeFeature(self):
        self.deleteTempLayerIfExists()
        uri = "linestring?crs=epsg:32635" + self.fieldsString
        layer = QgsVectorLayer(uri, "Привязка временный слой", "memory")

        layer.setCrs(QgsCoordinateReferenceSystem(32635))
        self.projectInstance.addMapLayer(layer)

        feat = QgsFeature()
        countAttributes = len(self.attributesDictionary)
        feat.initAttributes(countAttributes)

        i = 0
        for key in self.attributesDictionary:
            feat[i] = self.attributesDictionary[key]
            i += 1

        feat.setGeometry(QgsGeometry.fromPolylineXY(
            [self.point] + self.features))

        (res, outFeats) = layer.dataProvider().addFeatures([feat])

        layers = self.canvas.layers()
        layers.insert(0, layer)
        self.canvas.setLayers(layers)
        self.canvas.refresh()

        if self.canvas.isCachingEnabled():
            layer.triggerRepaint()
        else:
            self.canvas.refresh()

    def deleteTempLayerIfExists(self):
        try:
            layer = self.projectInstance.mapLayersByName(
                "Привязка временный слой")[0]
            self.projectInstance.removeMapLayers([layer.id()])
        except:
            pass

