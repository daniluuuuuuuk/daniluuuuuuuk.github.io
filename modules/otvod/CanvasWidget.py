from .UIButtonController import ButtonController
from .tools import GeoOperations
from .tools.mapTools.AzimuthMapTool import AzimuthMapTool
from .tools.mapTools.BuildFromMapPointsTool import BuildFromMapPointsTool
from .tools.mapTools.BuildFromMapTool import BuildFromMapTool
from .tools.mapTools.PeekPointFromMap import PeekPointFromMap
from .tools.mapTools.PeekStratumFromMap import PeekStratumFromMap
# from .LesosekaInfoDialog import LesosekaInfo
from .gui.LesosekaInfoDialog import LesosekaInfo
from . import CuttingArea, TempFeatures
from qgis.PyQt.QtWidgets import QMessageBox, QDialog
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsPointXY
from PyQt5.QtGui import QColor
from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsMapToolPan
from qgis.PyQt.QtCore import QObject


class CanvasWidget(QgsMapCanvas):

    def __init__(self, otvodMainWindow, layers, rct, table):

        self.predefinedScales = [500, 1000, 2500,
                                 5000, 10000, 25000, 50000, 100000]

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
                lambda x: self.canvas.zoomScale(int(x)))

        """При изменении масштаба производится его округление до предопределенных значений
        """

    def onScaleChanged(self):
        self.canvas.scaleChanged.disconnect(self.onScaleChanged)
        scale = self.canvas.scale()
        targetScale = min(self.predefinedScales,
                          key=lambda x: abs(int(x) - scale))
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
        # lp = QgsProject.instance().mapLayersByName("Линия привязки")[0]
        # lss = QgsProject.instance().mapLayersByName("Лесосеки")[0]

        # self.layers.insert(0, lp)
        # self.layers.insert(0, lss)

        canvas.setLayers(self.layers)

        crs = QgsCoordinateReferenceSystem('EPSG:32635')
        canvas.setDestinationCrs(crs)
        mapSettings = canvas.mapSettings()
        canvas.setExtent(self.rct)
        # canvas.zoomScale(10000)

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
            self.omw.outputLabel.setText(
                "Аз.: " + str(round(result[0], 1)) + "°. " + "Раст.: " + str(round(result[1], 2)) + " м.")

        if btnState == True:
            self.amt = AzimuthMapTool(self.canvas)
            self.canvas.setMapTool(self.amt)
            self.amt.signal.connect(getResult)
        elif btnState == False:
            self.amt.deactivate()
            # zoomTool = QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(self.panTool)

        """Инструмент выноса лесосеки из канваса
        """

    def build_from_map(self, btn, btnState, btnGroup):

        def getResult(result):
            point = GeoOperations.convertToWgs(result[0][0])
            self.omw.y_coord_LineEdit.setText(str(point.x()))
            self.omw.x_coord_LineEdit.setText(str(point.y()))
            # self.omw.coord_radio_button.clicked.emit()
            self.table.appendTableFromMap(result[1:])
            if btn.objectName() == "lesoseka_from_map_button":
                self.buildLesosekaFromMap()
            btn.toggle()

        if btnState == True:
            self.omw.coord_radio_button.toggle()
            self.table.deleteRows()
            if btn.objectName() == "lesoseka_from_map_points_button":
                self.bfm = BuildFromMapPointsTool(self.canvas)
            elif btn.objectName() == "lesoseka_from_map_button":
                self.bfm = BuildFromMapTool(self.canvas)
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

        """Строит лесосеку
        """

    def buildLesosekaFromMap(self):

        try:
            layer = QgsProject.instance().mapLayersByName("Пикеты")[0]
        except Exception as e:
            QMessageBox.information(
                None, "Ошибка модуля QGISLes", "Отсутствуют угловые точки")
            return

        layerVd = QgsProject.instance().mapLayersByName("Выдела")[0]
        layerVd.removeSelection()

        # dictAttr = {}

        # sw = LesosekaInfo()
        # ui = sw.ui
        # sw.setUpValues()
        # dialogResult = sw.exec()
        # if dialogResult == QDialog.Accepted:
        #     self.btnControl.unlockSaveDeleteButtons()
        #     dictAttr["num_lch"] = 0
        #     dictAttr["num_kv"] = 0
        #     dictAttr["num_vd"] = 0
        #     dictAttr["area"] = 0
        #     dictAttr["leshos"] = sw.lhNumber
        #     dictAttr["num"] = ui.num.text()
        #     dictAttr["useType"] = ""
        #     dictAttr["cuttingType"] = ""
        #     dictAttr["plot"] = ""
        #     dictAttr["fio"] = ui.fio.text()
        #     dictAttr["date"] = ui.date.text()
        #     dictAttr["info"] = ui.info.toPlainText()
        #     dictAttr["num_vds"] = ui.num_vds.text()
        #     dictAttr["leshos_text"] = ui.leshos.currentText()
        #     dictAttr["lesnich_text"] = ui.lesnich.currentText()
        # else:
        #     return
        n = float(self.omw.x_coord_LineEdit.text())
        e = float(self.omw.y_coord_LineEdit.text())
        bindingPoint = GeoOperations.convertToZone35(QgsPointXY(e, n))
        # self.cuttingArea = CuttingArea.CuttingArea(
        #     self.canvas, bindingPoint, layer, None, dictAttr)
        self.cuttingArea = CuttingArea.CuttingArea(
            self.canvas, bindingPoint, layer, None, self.btnControl)            
        # zoomTool = QgsMapToolZoom(self.canvas, False)
        self.canvas.setMapTool(self.panTool)
        cuttingArea = self.cuttingArea.build()
        # print("""""""""""""""""""""""""""""""""""""", cuttingArea)
        # self.showPointOnCanvas(cuttingArea)
        # x = self.refreshPolygonPoints(cuttingArea)
        # self.showPointOnCanvas(x)
        # print("cuttinarea =>", cuttingArea)
        # print("cuttinarea =>", cuttingArea.geometry().asPolygon())
        # print(type(cuttingArea.geometry().asPolygon()))

    # def refreshPolygonPoints(self, area):

    #     def assignNumbersToPoints(points):
    #         pointsWithNumbers = []
    #         i = 0
    #         for point in points:
    #             pointsWithNumbers.append([i, points[i]])
    #             i += 1
    #         return pointsWithNumbers

    #     points = area.geometry().asPolygon()
    #     return assignNumbersToPoints(points)

        """Получение точки из окна карты и занесение ее координат XY в таблицу
        """

    def peekPointFromMap(self, btn, btnState):

        def getResult(point):
            # print("Пришла точка привязки", point)
            point = GeoOperations.convertToWgs(point)
            self.omw.y_coord_LineEdit.setText(str(round(point.x(), 10)))
            self.omw.x_coord_LineEdit.setText(str(round(point.y(), 10)))

            # if self.table.getRowsCount() > 0:
            #     self.buildLesosekaFromMap()

            if btnState == True:
                btn.setChecked(False)
                self.ppfm.deactivate()
                # zoomTool = QgsMapToolZoom(self.canvas, False)
                self.canvas.setMapTool(self.panTool)

        if btnState == True:
            self.ppfm = PeekPointFromMap(self.canvas)
            self.canvas.setMapTool(self.ppfm)
            self.ppfm.signal.connect(getResult)

        elif btnState == False:
            # zoomTool = QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(self.panTool)

        """Инструмент выбора выдела на карте и построение его опорных точек
        """

    def peekVydelFromMap(self, btn, btnState):

        def getResult(selectedFeature):
            self.bap = TempFeatures.AnchorPointBuilder(
                self.canvas, selectedFeature)
            self.bap.makeFeature()

            self.bcp = TempFeatures.CuttingAreaBuilder(
                self.canvas, selectedFeature)
            self.bcp.makeFeature()

            if btnState == True:
                btn.setChecked(False)
                self.ppfm.deactivate()
                # zoomTool = QgsMapToolZoom(self.canvas, False)
                self.canvas.setMapTool(self.panTool)

        if btnState == True:
            self.ppfm = PeekStratumFromMap(self.canvas)
            self.canvas.setMapTool(self.ppfm)
            self.ppfm.signal.connect(getResult)

        elif btnState == False:
            # zoomTool = QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(self.panTool)

    def showPointOnCanvas(self, pointDict):
        # print("Пришла точка", pointDict)
        try:
            self.pb = TempFeatures.PointBuilder(pointDict, self.canvas)
            if pointDict:
                # self.pb = TempFeatures.PointBuilder(pointDict, self.canvas)
                self.pb.makeFeature()
            elif not pointDict:
                self.pb.deleteTempLayerIfExists()
                del self.pb
        except Exception as e:
            print(e)
