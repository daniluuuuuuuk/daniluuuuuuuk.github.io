from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QMessageBox, QDialog
from .gui.LesosekaInfoDialog import LesosekaInfo
from qgis.PyQt.QtWidgets import QDialog

class CuttingAreaAttributesEditor:

    def __init__(self, cuttingArea):
        self.cuttingArea = cuttingArea

    def getLesosekaFromTempLayer(self):
        try:
            layer = QgsProject.instance().mapLayersByName(
                "Лесосека временный слой")[0]
            features = []
            for feature in layer.getFeatures():
                features.append(feature)
            return features[0]
        except Exception as e:
            QMessageBox.information(
                None, "Ошибка модуля QGis", "Лесосека не построена\nОшибка: " + str(e))

    def editAreaAttributes(self):
        lesoseka = self.getLesosekaFromTempLayer()

        items = {}
        for x in lesoseka.fields():
            items.update({x.name(): lesoseka[x.name()]})

        dictAttr = {}
        sw = LesosekaInfo(True)
        ui = sw.ui
        # sw.setUpValues()
        sw.populateValues(items)
        dialogResult = sw.exec()
        if dialogResult == QDialog.Accepted:
            # self.btnControl.unlockSaveDeleteButtons()
            # dictAttr["num_lch"] = 0
            dictAttr["num_kv"] = ui.num_kv.text()
            # dictAttr["num_vd"] = 0
            dictAttr["area"] = ui.area.text()
            # dictAttr["leshos"] = sw.lhNumber
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
            self.refreshAttributes(dictAttr)
        else:
            return

    def refreshAttributes(self, attributesDict):

        layer = QgsProject.instance().mapLayersByName(
            "Лесосека временный слой")[0]

        layer.startEditing()
        features = layer.getFeatures()
        for feature in features:
            feature['num_kv'] = attributesDict.get('num_kv')
            # feature['leshos'] = attributesDict.get('leshos')
            feature['area'] = attributesDict.get('area')
            feature['num'] = attributesDict.get('num')
            feature['fio'] = attributesDict.get('fio')
            feature['date'] = attributesDict.get('date')
            feature['info'] = attributesDict.get('info')
            feature['num_vds'] = attributesDict.get('num_vds')
            feature['leshos_text'] = attributesDict.get('leshos_text')
            feature['lesnich_text'] = attributesDict.get('lesnich_text')
            feature['vedomstvo_text'] = attributesDict.get('vedomstvo_text')
            feature['useType'] = attributesDict.get('useType')
            feature['cuttingType'] = attributesDict.get('cuttingType')            
            layer.updateFeature(feature)
        layer.commitChanges()