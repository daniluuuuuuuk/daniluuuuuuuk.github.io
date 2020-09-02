import uuid
from .tools import MapTools
from qgis.core import QgsPointXY, QgsGeometry, QgsFeatureRequest
from qgis.core import QgsProject, QgsFeature
from . import TempFeatures

class CuttingArea:

    def __init__(self, canvas, bindingPoint, layer, feature, dictAttr):
        super().__init__()

        if feature == None:
            self.feature = self.getEmptyFeature()
        else:
            self.feature = feature
        self.canvas = canvas
        self.bindingPoint = bindingPoint
        self.layer = layer
        self.fields = self.feature.fields()
        self.dictAttr = dictAttr

        self.anchorLinePoints = []
        self.cuttingAreaPoints = []

        self.uid = str(uuid.uuid4())

    def getEmptyFeature(self):
        feature = QgsFeature()
        # feature.initAttributes(2)
        # attributes = [1, 2]
        # feature.setAttributes(attributes)
        return feature

    def build(self):

        def getId(f):
            return f['id']

        features = sorted(self.layer.getFeatures(), key=getId)
        for x in features:
            if x.attributes()[1] == "Привязка":
                # print("Привязка")
                self.anchorLinePoints.append(x.geometry().asPoint())
            elif x.attributes()[1] == "Лесосека":
                self.cuttingAreaPoints.append(x.geometry().asPoint())
                # print("Лесосека")
        if self.anchorLinePoints:
            # print("BUILD LINE")
            return self.buildLine()
        else:
            return self.buildPoly(self.bindingPoint)

    def buildLine(self):
        tempLineBuilder = TempFeatures.AnchorLineTemp(self.canvas, self.bindingPoint, self.anchorLinePoints, self.feature, self.uid, self.dictAttr)
        tempLineBuilder.makeFeature()

        tempCuttingAreaBuilder = TempFeatures.CuttingAreaTemp(self.canvas, self.anchorLinePoints[-1], self.cuttingAreaPoints, self.feature, self.uid, self.dictAttr)
        return tempCuttingAreaBuilder.makeFeature()
            
    def buildPoly(self, point):
        tempCuttingAreaBuilder = TempFeatures.CuttingAreaTemp(self.canvas, point, self.cuttingAreaPoints, self.feature, self.uid, self.dictAttr)
        return tempCuttingAreaBuilder.makeFeature()

    def save(self):
        if self.anchorLinePoints:
            self.copyOnLayer("Привязка временный слой", "Линия привязки")
            self.copyOnLayer("Лесосека временный слой", "Лесосеки")
        else:
            self.copyOnLayer("Лесосека временный слой", "Лесосеки")

    def copyOnLayer(self, sourceLYRName, destLYRName):
        # print("CopyOnLayer", sourceLYRName, destLYRName)
        sourceLYR = QgsProject.instance().mapLayersByName(sourceLYRName)[0]
        destLYR = QgsProject.instance().mapLayersByName(destLYRName)[0]

        request = QgsFeatureRequest().setFilterExpression('"uid" == %s' % (self.uid))
        # print('"uid" == %s' % (self.uid))
        request.setSubsetOfAttributes([])
        request.setFlags(QgsFeatureRequest.NoGeometry)
        for f in destLYR.getFeatures(request):
            # print("EST'")
            # print(f.id())
            destLYR.deleteFeature(f.id())

        features = []
        for feature in sourceLYR.getFeatures():
            features.append(feature)
        destLYR.startEditing()
        data_provider = destLYR.dataProvider()
        data_provider.addFeatures(features)
        destLYR.commitChanges()