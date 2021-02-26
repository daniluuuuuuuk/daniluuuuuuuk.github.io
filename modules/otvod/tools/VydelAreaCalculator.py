import processing
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QFont, QColor
from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem, QgsProject, QgsFillSymbol
from qgis.core import QgsProcessing, QgsDistanceArea, QgsCoordinateTransformContext, edit
from qgis.core import QgsVectorLayerSimpleLabeling, QgsTextFormat, QgsTextBufferSettings
from qgis.core import QgsTextBufferSettings, QgsUnitTypes, QgsField, QgsPalLayerSettings
from qgis.PyQt.QtWidgets import QToolButton, QMenu, QWidgetAction, QWidget, QMessageBox

class VydelAreaCalculator:

    def __init__(self):
        self.project = QgsProject.instance()
        self.inpath = self.project.mapLayersByName("Выдела")[0]
        self.layer = self.project.mapLayersByName("Лесосека временный слой")[0]

    def getCuttedLayer(self, inputLayer, outputLayer):
        self.deleteResultLayerIfExists()
        return processing.run("native:clip", {'INPUT': inputLayer, \
        'OVERLAY': outputLayer, 'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT})['OUTPUT']

    def deleteResultLayerIfExists(self):
        if self.project.mapLayersByName("Результат обрезки"):
            vl = self.project.mapLayersByName("Результат обрезки")[0]
            self.project.removeMapLayers([vl.id()])

    def setupAreaCalculationObject(self):
        da = QgsDistanceArea()
        da.setEllipsoid("WGS84")
        trctxt = QgsCoordinateTransformContext()
        da.setSourceCrs(QgsCoordinateReferenceSystem(32635), trctxt)
        return da

    def getLayers(self):
        pass

    def addAreaAttribute(self, newLayer, name):
            with edit(newLayer):
                x = newLayer.dataProvider().addAttributes([QgsField(name, QVariant.String)])
                newLayer.updateFields()
                # newLayer.commitChanges()

    def calculateAreaByVydel(self):
        try:
            newLayer = self.getCuttedLayer(self.inpath, self.layer)

            self.project.addMapLayer(newLayer)

            da = self.setupAreaCalculationObject()

            self.addAreaAttribute(newLayer, "area_calc")

            self.updateAreaAttribute(newLayer, da)

            newLayer.renderer().setSymbol(self.setLayerSymbol())
            self.setLayerLabelling(newLayer)

        except Exception as e:
            QMessageBox.information(None, 'Ошибка', "Ошибка при расчете площади по выделам.\n" + str(e))
    
    def updateAreaAttribute(self, newLayer, da):
        with edit(newLayer):
            for feat in newLayer.getFeatures():
                multiPart = feat.geometry().isMultipart()
                if not multiPart:
                    pol = feat.geometry().asPolygon()
                    area = da.measurePolygon(pol[0])
                    areaRounded = round(da.convertAreaMeasurement(
                        area, QgsUnitTypes.AreaHectares), 1)
                    #СЮДА ТОЖЕ ВКЛЮЧИТЬ УДАЛЕНИЕ ЕСЛИ ПЛОЩАДЬ МЕНЬШЕ 0.1
                else:
                    pol = feat.geometry().asMultiPolygon()
                    for geom in pol:
                        area = da.measurePolygon(geom[0])
                        areaRounded = round(da.convertAreaMeasurement(
                            area, QgsUnitTypes.AreaHectares), 1)
                        areaRoundedPrec = round(da.convertAreaMeasurement(
                            area, QgsUnitTypes.AreaHectares), 4)
                        if areaRoundedPrec < 0.0001:
                            newLayer.deleteFeature(feat.id())
                        elif areaRounded < 0.1:
                            feat["area_calc"] = '<0.1'
                        else:
                            feat["area_calc"] = areaRounded
                        newLayer.updateFeature(feat)

    def setLayerSymbol(self):
        symbol = QgsFillSymbol.createSimple(
            {'color': '255,0,0,0', 'color_border': '0,0,0,0'})
        return symbol

    def setLayerLabelling(self, layer):
        layer_settings = QgsPalLayerSettings()
        layer_settings.isExpression = True
        text_format = QgsTextFormat()

        text_format.setFont(QFont("Arial", 8))
        text_format.setSize(8)

        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(False)
        buffer_settings.setSize(0.10)
        buffer_settings.setColor(QColor("white"))

        text_format.setBuffer(buffer_settings)
        layer_settings.setFormat(text_format)

        layer_settings.fieldName = "concat(area_calc, ' га', '\n', ' (', num_vd, ')')"
        layer_settings.placement = 1

        layer_settings.enabled = True
        layer_settings.displayAll = True

        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        layer.setLabelsEnabled(True)
        layer.setLabeling(layer_settings)
        layer.triggerRepaint()

