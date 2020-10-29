from qgis.core import QgsPointXY, QgsFeature, QgsVectorLayer, QgsGeometry, QgsProject, QgsDistanceArea, QgsUnitTypes
from qgis.core import QgsCoordinateReferenceSystem, QgsMarkerSymbol, QgsFillSymbol, QgsPalLayerSettings, QgsTextFormat
from qgis.core import QgsTextBufferSettings, QgsVectorLayerSimpleLabeling, QgsVectorDataProvider, QgsCoordinateTransformContext
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import QVariant


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


class CuttingAreaTemp():

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


class CuttingAreaBuilder():

    def __init__(self, canvas, feature):
        self.canvas = canvas
        self.feature = feature
        self.projectInstance = QgsProject.instance()
        self.symbol = self.setLayerSymbol()

    def setLayerSymbol(self):
        symbol = QgsFillSymbol.createSimple(
            {'color': '0,0,0,0', 'color_border': '0,0,0,255', 'style': 'dense7'})
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
