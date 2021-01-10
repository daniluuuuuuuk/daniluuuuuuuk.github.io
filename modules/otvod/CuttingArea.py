import uuid
from qgis.core import QgsPointXY, QgsGeometry, QgsFeatureRequest
from qgis.core import QgsProject, QgsFeature, QgsExpression
from .tools.tempFeatures.AnchorLineTemp import AnchorLineTemp
from .tools.tempFeatures.CuttingAreaTemp import CuttingAreaTemp
from . import TieUpObject
from .tools.DiscrepancyCalculator import DiscrepancyCalculator
from qgis.PyQt.QtWidgets import QDialog
from .gui.discrepancyWindow import Ui_Dialog as DiscrepancyDialog
from .gui.LesosekaInfoDialog import LesosekaInfo
from .tools import GeoOperations
from qgis.core import edit
from .tools.Serializer import DbSerializer

class CuttingArea:

    def __init__(self, canvas, bindingPoint, layer, feature, btnControl, editedUid):
        super().__init__()

        if feature == None:
            self.feature = self.getEmptyFeature()
        else:
            self.feature = feature
        self.canvas = canvas
        self.bindingPoint = bindingPoint
        self.layer = layer
        self.uid = editedUid
        self.fields = self.feature.fields()
        self.dictAttr = None

        self.isAlreadyTiedUp = None

        self.anchorLinePoints = []
        self.cuttingAreaPoints = []

        self.btnControl = btnControl
        if self.uid == None:
            self.uid = str(uuid.uuid4())
            
    def getLesosekaProperties(self):
        dictAttr = {}
        self.sw = LesosekaInfo(False)
        ui = self.sw.ui
        self.sw.setUpValues(self.layer)
        dialogResult = self.sw.exec()
        if dialogResult == QDialog.Accepted:
            self.btnControl.unlockSaveDeleteButtons()
            dictAttr["num_lch"] = self.sw.getLesnichNumber()
            dictAttr["num_kv"] = ui.num_kv.text()
            # dictAttr["num_vd"] = 0
            dictAttr["area"] = 0
            dictAttr["leshos"] = self.sw.getLeshozNumber()
            dictAttr["num"] = ui.num.text()
            dictAttr["useType"] = ui.useType.currentText()
            dictAttr["cuttingType"] = ui.cuttingType.currentText()
            # dictAttr["plot"] = ""
            dictAttr["fio"] = ui.fio.text()
            dictAttr["date"] = ui.date.text()
            dictAttr["info"] = ui.info.toPlainText()
            dictAttr["num_vds"] = ui.num_vds.text()
            dictAttr["leshos_text"] = ui.leshos.currentText()
            dictAttr["lesnich_text"] = ui.lesnich.currentText()
            dictAttr["vedomstvo_text"] = ui.gplho.currentText()
            return dictAttr
        else:
            return False

        """Получение шаблонного объекта
        """

    def getEmptyFeature(self):
        feature = QgsFeature()
        return feature

        """Построение лесосеки на основании точек
        """

    def build(self):

        def getId(f):
            return f['id']

        self.tiedUpPointList = []
        features = sorted(self.layer.getFeatures(), key=getId)
        for x in features:
            if x.attributes()[1] == "Привязка":
                self.anchorLinePoints.append(x.geometry().asPoint())
            elif x.attributes()[1] == "Лесосека":
                self.cuttingAreaPoints.append(x.geometry().asPoint())
        if (self.showDiscrepancyWindow()):
            self.dictAttr = self.getLesosekaProperties()
            if self.dictAttr == False:
                return
            if self.anchorLinePoints:
                if not self.isTiedUp(self.anchorLinePoints[-1], self.cuttingAreaPoints[-1]):
                    self.tiedUpPointList = [
                        self.anchorLinePoints[-1]] + self.cuttingAreaPoints
                    self.cuttingAreaPoints = self.tieUp(self.tiedUpPointList)
                self.buildLine()
                return self.getTiedUpPointsWithNumbers(self.anchorLinePoints, self.cuttingAreaPoints)
            else:
                if not self.isTiedUp(self.bindingPoint, self.cuttingAreaPoints[-1]):
                    self.tiedUpPointList = [
                        self.bindingPoint] + self.cuttingAreaPoints
                    self.cuttingAreaPoints = self.tieUp(self.tiedUpPointList)
                self.buildPoly(self.bindingPoint)
                return self.getTiedUpPointsWithNumbers(None, self.cuttingAreaPoints)

    def showDiscrepancyWindow(self):
        discrepancies = self.getDiscrepanciesList()

        angleDiscrepancy = GeoOperations.convertToDMS(discrepancies[0])
        maxAngleDiscrepancy = GeoOperations.convertToDMS(discrepancies[2])

        angleDiscrepancyFormatted = str(angleDiscrepancy[0]) + '° ' + str(
            round(angleDiscrepancy[1], 1)) + '′ ' + str(round(angleDiscrepancy[2], 1)) + '″'
        maxAngleDiscrepancyFormatted = str(maxAngleDiscrepancy[0]) + '° ' + str(round(
            maxAngleDiscrepancy[1], 1)) + '′ ' + str(round(maxAngleDiscrepancy[2], 1)) + '″'

        linearDiscrepancy = str(round(discrepancies[1], 1))
        maxLinearDiscrepancy = str(round(discrepancies[3], 1))

        dialog = QDialog()
        window = DiscrepancyDialog()
        window.setupUi(dialog)

        if (discrepancies[4] == True):
            window.angleDiscrepancyMeasured.setStyleSheet(
                "background-color: lightgreen")
        else:
            window.angleDiscrepancyMeasured.setStyleSheet(
                "background-color: red")
        if (discrepancies[5] == True):
            window.linearDiscrepancyMeasured.setStyleSheet(
                "background-color: lightgreen")
        else:
            window.linearDiscrepancyMeasured.setStyleSheet(
                "background-color: red")

        window.angleDiscrepancyMeasured.setText(angleDiscrepancyFormatted)
        window.linearDiscrepancyMeasured.setText(linearDiscrepancy)
        window.maxAngleDiscrepancy.setText(maxAngleDiscrepancyFormatted)
        window.maxLinearDiscrepancy.setText(maxLinearDiscrepancy)

        if (dialog.exec_() == QDialog.Accepted):
            return True
        return False

    def getDiscrepanciesList(self):
        if self.anchorLinePoints:
            pointsList = [self.anchorLinePoints[-1]] + self.cuttingAreaPoints
        else:
            pointsList = [self.bindingPoint] + self.cuttingAreaPoints
        dCalc = DiscrepancyCalculator(pointsList)
        return [dCalc.angleDiscrepancy, dCalc.linearDiscrepancy, dCalc.maxAngleDiscrepapancy, dCalc.maxLinearDiscrepancy, dCalc.isAngleDiscrepancyAcceptable(), dCalc.isLinearDiscrepancyAcceptable()]

        """Получение увязанных точек лесосеки с нумерацией в порядке
        """

    def getTiedUpPointsWithNumbers(self, anchorLinePoints, cuttingAreaTiedUpPoints):
        if not anchorLinePoints:
            i = 0
            pairNumberPoint = {}
            for point in cuttingAreaTiedUpPoints:
                pairNumberPoint[i] = [point, "Лесосека"]
                i += 1
            if not self.isAlreadyTiedUp:
                pairNumberPoint[i] = [self.bindingPoint, "Лесосека"]
        else:
            i = 0
            pairNumberPoint = {}
            for point in anchorLinePoints:
                pairNumberPoint[i] = [point, "Привязка"]
                i += 1
            for point in cuttingAreaTiedUpPoints:
                pairNumberPoint[i] = [point, "Лесосека"]
                i += 1
            if not self.isAlreadyTiedUp:
                pairNumberPoint[i] = [anchorLinePoints[-1], "Лесосека"]
        return pairNumberPoint

    def isTiedUp(self, firstPoint, lastPoint):
        if firstPoint == lastPoint:
            self.isAlreadyTiedUp = True
            return True
        else:
            self.isAlreadyTiedUp = False
            return False

        """Увязка полигона
        """

    def tieUp(self, pointList):
        tieUpPolygon = TieUpObject.Polygon(pointList)
        return tieUpPolygon.getTiedUpFeature()

        """Построение лесосеки с линией привязки
        """

    def buildLine(self):
        tempLineBuilder = AnchorLineTemp(
            self.canvas, self.bindingPoint, self.anchorLinePoints, self.uid)
        tempLineBuilder.makeFeature()

        tempCuttingAreaBuilder = CuttingAreaTemp(
            self.canvas, self.anchorLinePoints[-1], self.cuttingAreaPoints, self.feature, self.uid, self.dictAttr)
        return tempCuttingAreaBuilder.makeFeature()

        """Построение лесосеки без линии привязки
        """

    def buildPoly(self, point):
        tempCuttingAreaBuilder = CuttingAreaTemp(
            self.canvas, point, self.cuttingAreaPoints, self.feature, self.uid, self.dictAttr)
        return tempCuttingAreaBuilder.makeFeature()

        """Сохранение лесосеки
        """

    def save(self, tableData):
        if self.anchorLinePoints:
            self.copyOnLayer("Привязка временный слой", "Линия привязки")
            self.copyOnLayer("Лесосека временный слой", "Лесосеки")
        else:
            self.copyOnLayer("Лесосека временный слой", "Лесосеки")

        data = [self.uid] + tableData
        DbSerializer(data).saveToDb()


        """Копирование лесосеки с временного слоя на слой из базы данных
        """

    def copyOnLayer(self, sourceLYRName, destLYRName):
        sourceLYR = QgsProject.instance().mapLayersByName(sourceLYRName)[0]
        destLYR = QgsProject.instance().mapLayersByName(destLYRName)[0]

        features = destLYR.getFeatures("uid = '{}'".format(self.uid))
        print(self.uid)
        with edit(destLYR):
            for f in features:
                print(f.id())
                destLYR.deleteFeature(f.id())

        features = []
        for feature in sourceLYR.getFeatures():
            features.append(feature)
        destLYR.startEditing()
        data_provider = destLYR.dataProvider()
        data_provider.addFeatures(features)
        destLYR.commitChanges()
