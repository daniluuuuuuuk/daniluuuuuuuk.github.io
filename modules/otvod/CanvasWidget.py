from . import CuttingArea
from .UIButtonController import ButtonController
from .tools import GeoOperations
from .tools.Serializer import DbSerializer
from .tools.mapTools.AzimuthMapTool import AzimuthMapTool
from .tools.mapTools.BuildFromMapPointsTool import BuildFromMapPointsTool
from .tools.mapTools.BuildFromMapTool import BuildFromMapTool
from .tools.mapTools.PeekPointFromMap import PeekPointFromMap
from .tools.mapTools.PeekStratumFromMap import PeekStratumFromMap
from .tools.tempFeatures.AnchorPointBuilder import AnchorPointBuilder
from .tools.tempFeatures.CuttingAreaBuilder import CuttingAreaBuilder
from .tools.tempFeatures.PointBuilder import PointBuilder
from .tools.VydelAreaCalculator import VydelAreaCalculator
from .gui.LesosekaInfoDialog import LesosekaInfo
from qgis.PyQt.QtWidgets import QMessageBox, QDialog
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsPointXY
from PyQt5.QtGui import QColor
from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsMapToolPan
from qgis.PyQt.QtCore import QObject
from .LayerManager import LayerManager


class CanvasWidget(QgsMapCanvas):
    def __init__(self, otvodMainWindow, layers, rct, table):

        self.predefinedScales = [
            500,
            1000,
            2500,
            5000,
            10000,
            25000,
            50000,
            100000,
        ]

        super(CanvasWidget, self).__init__()
        QObject.__init__(self)
        self.omw = otvodMainWindow
        self.layers = layers
        self.table = table
        self.rct = rct
        self.canvas = self.setupDefaultCanvas()
        self.canvas.scaleChanged.connect(self.onScaleChanged)
        self.initScalesBox()
        self.cuttingArea = None
        self.btnControl = ButtonController(self.getButtons())
        self.btnControl.lockLesosekaButtons()
        self.panTool = QgsMapToolPan(self.canvas)
        self.editedUid = None

        """Возвращает кнопки управления лесосекой
        """

    def getButtons(self):
        return [
            self.omw.buildLesoseka_Button,
            self.omw.editAttributes_button,
            self.omw.saveLesoseka_Button,
            self.omw.deleteLesoseka_Button,
            self.omw.generateReport_Button,
        ]

        """Инициализирует список масштабов
        """

    def initScalesBox(self):
        box = self.omw.canvas_scale_combo
        for x in self.predefinedScales:
            box.addItem(str(x))
        if self.canvas:
            box.currentTextChanged.connect(
                lambda x: self.canvas.zoomScale(int(x))
            )

        """При изменении масштаба производится его округление до предопределенных значений
        """

    def onScaleChanged(self):
        self.canvas.scaleChanged.disconnect(self.onScaleChanged)
        scale = self.canvas.scale()
        targetScale = min(
            self.predefinedScales, key=lambda x: abs(int(x) - scale)
        )
        self.canvas.zoomScale(targetScale)
        self.omw.canvas_scale_combo.setCurrentText(str(targetScale))
        self.canvas.scaleChanged.connect(self.onScaleChanged)

        """Настройка канваса
        """

    def setupDefaultCanvas(self):
        canvas = QgsMapCanvas(self.omw.canvasWidget)
        canvas.setCanvasColor(QColor(255, 255, 255, 255))
        canvas.enableAntiAliasing(True)
        canvas.setFixedWidth(371)
        canvas.setFixedHeight(341)

        canvas.setLayers(self.layers)

        crs = QgsCoordinateReferenceSystem("EPSG:32635")
        canvas.setDestinationCrs(crs)
        mapSettings = canvas.mapSettings()
        canvas.setExtent(self.rct)

        canvas.refresh()
        return canvas

        """Возвращает текущий канвас
        """

    def getCanvas(self):
        return self.canvas

        """Инструмент определения азимута и расстояния
        """

    def findAzimuth(self, btn, btnState):
        def getResult(result):
            magnAz = self.validatedAzimuth(
                float(round(result[0], 1))
                - self.table.getMagneticInclination()
            )
            self.omw.outputLabel.setText(
                "Аз. истин.: "
                + str(round(result[0], 1))
                + "°, магн.: "
                + str(round(magnAz, 1))
                + "°. Расст.: "
                + str(round(result[1], 1))
                + "м."
            )

        if btnState == True:
            self.amt = AzimuthMapTool(
                self.canvas, self.table.getMagneticInclination()
            )
            self.canvas.setMapTool(self.amt)
            self.amt.signal.connect(getResult)
        elif btnState == False:
            self.amt.deactivate()
            self.canvas.setMapTool(self.panTool)

    def validatedAzimuth(self, azimuth):
        if azimuth > 360:
            return azimuth - 360
        elif azimuth < 0:
            return 360 - abs(azimuth)
        else:
            return azimuth

        """Инструмент выноса лесосеки из канваса
        """

    def build_from_map(self, btn, btnState, btnGroup):
        def getResult(result):
            point = GeoOperations.convertToWgs(result[0][0])
            self.omw.y_coord_LineEdit.setText(str(point.x()))
            self.omw.x_coord_LineEdit.setText(str(point.y()))
            self.table.appendTableFromMap(result[1:])
            # if btn.objectName() == "lesoseka_from_map_button":
            #     self.buildLesosekaFromMap()
            btn.toggle()

        if btnState == True:
            self.omw.coord_radio_button.toggle()
            self.table.deleteRows()
            if btn.objectName() == "lesoseka_from_map_points_button":
                self.bfm = BuildFromMapPointsTool(
                    self.canvas, self.table.getMagneticInclination()
                )
            elif btn.objectName() == "lesoseka_from_map_button":
                self.bfm = BuildFromMapTool(
                    self.canvas, self.table.getMagneticInclination()
                )
            self.canvas.setMapTool(self.bfm)
            self.bfm.signal.connect(getResult)

        elif btnState == False:
            try:
                self.bfm.deactivate()
            except:
                print("Ошибка деактивации OtvodModule")
            zoomTool = QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(zoomTool)
            for button in btnGroup:
                button.setEnabled(True)

    def isAreaValid(self, layer):
        def getId(f):
            return f["id"]

        features = sorted(layer.getFeatures(), key=getId)
        lesosekaPointsCounter = 0
        for x in features:
            if x.attributes()[1] == "Лесосека":
                lesosekaPointsCounter += 1
                if lesosekaPointsCounter == 3:
                    return True
        return False

        """Строит лесосеку
        """

    def buildLesosekaFromMap(self):
        try:
            layer = QgsProject.instance().mapLayersByName("Пикеты")[0]
        except Exception as e:
            QMessageBox.information(
                None, "Ошибка модуля QGISLes", "Отсутствуют угловые точки"
            )
            return

        layerVd = QgsProject.instance().mapLayersByName("Выдела")[0]
        layerVd.removeSelection()

        try:
            n = float(self.omw.x_coord_LineEdit.text())
            e = float(self.omw.y_coord_LineEdit.text())
            bindingPoint = GeoOperations.convertToZone35(QgsPointXY(e, n))
        except Exception as e:
            QMessageBox.information(
                None, "Ошибка модуля QGISLes", "Некорректная точка привязки"
            )
            return

        if not self.isAreaValid(layer):
            QMessageBox.information(
                None,
                "Ошибка модуля QGISLes",
                "Для построения лесосеки необходимо минимум 3 узла",
            )
            return

        self.cuttingArea = CuttingArea.CuttingArea(
            self.canvas,
            bindingPoint,
            layer,
            None,
            self.btnControl,
            self.editedUid,
        )
        self.canvas.setMapTool(self.panTool)
        cuttingArea = self.cuttingArea.build()
        if not cuttingArea:
            return

        switch = self.omw.switchLayout.itemAt(0).widget()
        if switch.isChecked():
            switch.setChecked(False)

        # self.tableWrapper.convertCoordFormat(self.coordType)
        self.omw.coord_radio_button.setChecked(True)
        self.table.makeTableFromCuttingArea(bindingPoint, cuttingArea)
        # self.table.deleteLastTemperatePoint()
        self.showAreaByVydel()
        # self.omw.inclinationSlider.setValue(0)

    def showAreaByVydel(self):
        calc = VydelAreaCalculator()
        layer = calc.calculateAreaByVydel()
        manager = LayerManager(self.canvas)
        manager.addLayer("Результат обрезки")

        """Получение точки из окна карты и занесение ее координат XY в таблицу
        """

    def peekPointFromMap(self, btn, btnState):
        def getResult(point):
            point = GeoOperations.convertToWgs(point)
            self.omw.y_coord_LineEdit.setText(str(round(point.x(), 10)))
            self.omw.x_coord_LineEdit.setText(str(round(point.y(), 10)))

            if btnState == True:
                btn.setChecked(False)
                self.ppfm.deactivate()
                self.canvas.setMapTool(self.panTool)

        if btnState == True:
            self.ppfm = PeekPointFromMap(self.canvas)
            self.canvas.setMapTool(self.ppfm)
            self.ppfm.signal.connect(getResult)

        elif btnState == False:
            self.canvas.setMapTool(self.panTool)

    def peekVydelFromMap(self, btn, btnState):
        def getSelectedFeature(selectedFeature):
            def getAreaPoints(areaData, areaPoints):
                self.editedUid = areaData[0]
                self.omw.coord_radio_button.setChecked(True)
                switch = self.omw.switchLayout.itemAt(0).widget()
                if switch.isChecked():
                    switch.setChecked(False)
                point = GeoOperations.convertToWgs(areaData[1])
                self.omw.y_coord_LineEdit.setText(str(round(point.x(), 10)))
                self.omw.x_coord_LineEdit.setText(str(round(point.y(), 10)))
                self.omw.inclinationSlider.setValue(float(areaData[2] * 10))
                self.table.makeTableFromCuttingArea(areaData[1], areaPoints[0])

            if not selectedFeature:
                return
            try:
                serializer = DbSerializer(selectedFeature["uid"])
                serializer.signal.connect(getAreaPoints)
                serializer.loadFromDb()
            finally:
                if btnState == True:
                    btn.setChecked(False)
                    self.ppfm.deactivate()
                    self.canvas.setMapTool(self.panTool)

        if btnState == True:
            self.ppfm = PeekStratumFromMap(self.canvas, "Лесосеки")
            self.canvas.setMapTool(self.ppfm)
            self.ppfm.signal.connect(getSelectedFeature)

        elif btnState == False:
            self.canvas.setMapTool(self.panTool)

    def showPointOnCanvas(self, pointDict):
        try:
            self.pb = PointBuilder(pointDict, self.canvas)
            if pointDict:
                self.pb.makeFeature()
            elif not pointDict:
                self.pb.deleteTempLayerIfExists()
                del self.pb
        except Exception as e:
            print(e)
