from qgis.PyQt.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QApplication, QSizePolicy, QFileDialog, QTableWidgetItem, QWidget, QButtonGroup
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import QSize, QFile, QIODevice, QByteArray, QDataStream, Qt, QDateTime, pyqtSignal, QObject
from qgis.core import QgsPointXY, QgsRectangle, QgsCoordinateReferenceSystem, QgsProject, QgsMapLayer, QgsGeometry, QgsApplication
from .gui.otvodMainWindow import Ui_MainWindow as otvodMainWindow
from .gui.otvodSettings import Ui_Dialog as uiOtvodSettingDialog
from .gui.lesosekaInfo import Ui_Dialog as uiLesosekaInfo
from .DataTable import TableType, CoordType
from .DataTable import DataTableWrapper
from PyQt5.QtGui import QColor, QIcon
from PyQt5 import QtCore
from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsRubberBand
from datetime import datetime
from ...tools import config
from .tools import MapTools, GeoOperations
import json
from functools import partial
from . import TempFeatures, CuttingArea, Report
from qgis.utils import iface
import os
from .tools.threading import ForestObjectLoader
from .tools.threading.ForestObjectWorker import Worker as ForestObjWorker
from .UIButtonController import ButtonController
from .ui.SwitchButton import Switch

class MainWindow(QMainWindow, otvodMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        otvodMainWindow.__init__(self)
        self.setupUi(self)

    def closeEvent(self, event):
        try:
            layer = QgsProject.instance().mapLayersByName("Точка привязки")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Точка привязки")
        try:
            layer = QgsProject.instance().mapLayersByName("Лесосека временный слой")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Точка привязки")
        try:
            layer = QgsProject.instance().mapLayersByName("Опорные точки")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Опорные точки")
        try:
            layer = QgsProject.instance().mapLayersByName("Выдел лесосеки")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Выдел лесосеки")
        try:
            layer = QgsProject.instance().mapLayersByName("Пикеты")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Пикеты")
        try:
            layer = QgsProject.instance().mapLayersByName("Привязка временный слой")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Привязка временный слой")
        iface.mapCanvas().refresh()
        self.deleteLater()

class OtvodController:
    def __init__(self, layerList, rct):
        self.layers = layerList
        self.rct = rct

        self.omw = MainWindow()

        self.tableType = 0
        self.coordType = 0
        self.magneticInclination = 0.0

        self.bindingPoint = QgsPointXY(0, 0)
        self.cuttingArea = None
        self.tableWrapper = self.loadDataTable()

        self.omw.peekFromMap_PushButton.setIcon(QIcon(self.resolve('icons\\pick_from_map_icon.png')))
        self.omw.peekFromGPSPushButton.setIcon(QIcon(self.resolve('icons\\pick_from_gps_icon.png')))
        self.omw.addRangeFinderNode_button.setIcon(QIcon(self.resolve('icons\\range_finder_icon.png')))
        self.omw.azimuthTool_pushButton.setIcon(QIcon(self.resolve('icons\\azimuth_icon.png')))
        self.omw.buildLesoseka_Button.setIcon(QIcon(self.resolve('icons\\build.png')))
        self.omw.editAttributes_button.setIcon(QIcon(self.resolve('icons\\pencil.png')))        
        self.omw.saveLesoseka_Button.setIcon(QIcon(self.resolve('icons\\save.png')))
        self.omw.deleteLesoseka_Button.setIcon(QIcon(self.resolve('icons\\delete.png')))
        self.omw.generateReport_Button.setIcon(QIcon(self.resolve('icons\\report.png')))
        self.omw.peekVydelFromMap_pushButton.setIcon(QIcon(self.resolve('icons\\pin.png')))
        self.omw.lesoseka_from_map_button.setIcon(QIcon(self.resolve('icons\\lesoseka_from_map.png')))
        self.omw.importCoordinates.setIcon(QIcon(self.resolve('icons\\internet.png')))

        self.omw.otvodSettingsAction.triggered.connect(lambda: self.otvodMenuSettings())
        self.omw.saveData_action.triggered.connect(lambda: self.saveDataToFile())
        self.omw.loadData_action.triggered.connect(lambda: self.loadDataFromFile())

        self.canvasWidget = canvasWidget(self.omw, self.layers, self.rct, self.tableWrapper)

        self.omw.azimuthTool_pushButton.toggled.connect(partial(self.canvasWidget.findAzimuth, self.omw.azimuthTool_pushButton))
        self.omw.lesoseka_from_map_button.clicked.connect(partial(self.build_from_map_clicked, self.omw.lesoseka_from_map_button))
        self.omw.lesoseka_from_map_button.toggled.connect(partial(self.build_from_map_toggled, self.omw.lesoseka_from_map_button))

        self.omw.editAttributes_button.clicked.connect(self.editAreaAttributes)

        self.omw.peekFromMap_PushButton.toggled.connect(partial(self.canvasWidget.peekPointFromMap, self.omw.peekFromMap_PushButton))
        self.omw.peekVydelFromMap_pushButton.toggled.connect(partial(self.canvasWidget.peekVydelFromMap, self.omw.peekVydelFromMap_pushButton))

        self.tableWrapper.tableModel.signal.connect(self.canvasWidget.showPointOnCanvas)

        self.omw.peekFromGPSPushButton.clicked.connect(self.getGPSCoords)
        self.omw.generateReport_Button.clicked.connect(self.generateReport)

        # self.omw.buildLesoseka_Button.clicked.connect(self.buildTempCuttingArea)
        self.omw.buildLesoseka_Button.clicked.connect(self.canvasWidget.buildLesosekaFromMap)        
        self.omw.saveLesoseka_Button.clicked.connect(self.saveCuttingArea)
        self.omw.deleteLesoseka_Button.clicked.connect(self.deleteCuttingArea)

        self.omw.rotate_left.clicked.connect(partial(self.rotateCuttingArea, self.omw.rotate_left))
        self.omw.rotate_right.clicked.connect(partial(self.rotateCuttingArea, self.omw.rotate_right))

        self.omw.x_coord_LineEdit.textChanged.connect(self.bindingPointCoordChanged)
        self.omw.y_coord_LineEdit.textChanged.connect(self.bindingPointCoordChanged)

        self.radio_group = self.setup_radio_buttons()
        self.radio_group.buttonClicked.connect(self.radio_clicked)
        self.radio_group.buttonToggled.connect(self.radio_clicked)
        self.omw.coord_radio_button.toggle()

        self.canvas = self.canvasWidget.getCanvas()
        self.omw.show()
        self.switch = self.initSwitchButton()

    def initSwitchButton(self):
        # s3 = Switch(thumb_radius=6, track_radius=8)
        s4 = Switch(thumb_radius=6, track_radius=8)
        s4.toggled.connect(partial(self.switchClicked, s4))
        self.omw.switchLayout.addWidget(s4)
        return s4

    def switchClicked(self, switch):
        if switch.isChecked():
            self.coordType = 1
        else:
            self.coordType = 0
        self.tableWrapper.convertCoordFormat(self.coordType)
        # print(self.coordType)
        # btn = self.radio_group.button(self.tableType)
        # btn.animateClick()
        # # self.radio_clicked(btn)

    def getLesosekaFromTempLayer(self):
        try:
            layer = QgsProject.instance().mapLayersByName("Лесосека временный слой")[0]
            features = []
            for feature in layer.getFeatures():
                features.append(feature)
            return features[0]
        except Exception as e:
            QMessageBox.information(None, "Ошибка модуля QGis", "Лесосека не построена\nОшибка: " + str(e))

    def editAreaAttributes(self):
        lesoseka = self.getLesosekaFromTempLayer()
        items = []
        # print(lesoseka.attributes())
        for x in lesoseka.fields():
            items.append({x.name() : lesoseka[x.name()]})
            # print(lesoseka[x.name()])
        dictAttr = {}
        sw = LesosekaInfo()
        ui = sw.ui
        # sw.setUpValues()
        sw.populateValues(items)
        dialogResult = sw.exec()
        if dialogResult == QDialog.Accepted:
            # self.btnControl.unlockSaveDeleteButtons()
            dictAttr["num_lch"] = 0
            dictAttr["num_kv"] = 0
            dictAttr["num_vd"] = 0
            dictAttr["area"] = 0
            dictAttr["leshos"] = sw.lhNumber
            dictAttr["num"] = ui.num.text()
            dictAttr["useType"] = ""
            dictAttr["cuttingType"] = ""
            dictAttr["plot"] = ""         
            dictAttr["fio"] = ui.fio.text()
            dictAttr["date"] = ui.date.text()
            dictAttr["info"] = ui.info.toPlainText()
            dictAttr["num_vds"] = ui.num_vds.text()
            dictAttr["leshos_text"] = ui.leshos.currentText()
            dictAttr["lesnich_text"] = ui.lesnich.currentText()
        else:
            return

    def disableRadioGroup(self, bl):
        for button in self.radio_group.buttons():
            button.setEnabled(bl)

    def build_from_map_clicked(self, btn, btnState):
        self.disableRadioGroup(False)
        # self.coordType = 0
        self.switch.setChecked(False)
        self.canvasWidget.build_from_map(btn, btnState, self.radio_group.buttons())

    def build_from_map_toggled(self, btn, btnState):
        if btnState == True:
            self.disableRadioGroup(False)
            self.deleteCuttingArea()
        else:
            self.canvasWidget.build_from_map(btn, btnState, self.radio_group.buttons())

    def setup_radio_buttons(self):
        radio_group=QButtonGroup() # Number group
        radio_group.addButton(self.omw.coord_radio_button)
        radio_group.addButton(self.omw.azimuth_radio_button)
        radio_group.addButton(self.omw.rumb_radio_button)
        radio_group.addButton(self.omw.angle_radio_button)
        i = 0
        for btn in radio_group.buttons():
            radio_group.setId(btn, i)
            i += 1
        return radio_group
        
    def radio_clicked(self, button):
        # if button.text() != "Координаты" and self.omw.lesoseka_from_map_button.isChecked():
        #     for btn in self.radio_group.buttons():
        #         if self.tableType == self.radio_group.id(btn):
        #             btn.setChecked(True)
        #             QMessageBox.information(None, 'Ошибка', 'Закончите построение лесосеки')
        #     return
        if self.tableType == self.radio_group.id(button):
            pass
        elif self.tableWrapper.tableModel.ensureTableCellsNotEmpty():
            buttonId = self.radio_group.id(button)
            currentTableType = self.tableType
            self.tableType = buttonId
            # self.coordType = 0
            self.tableWrapper.convertCells(currentTableType, buttonId, self.tableType, self.coordType, float(self.magneticInclination), self.bindingPoint)
        else:
            for btn in self.radio_group.buttons():
                if self.tableType == self.radio_group.id(btn):
                    btn.setChecked(True)
                    QMessageBox.information(None, 'Ошибка', 'Заполните недостающие данные в таблице или очистите таблицу')
        
    def resolve(self, name, basepath=None):
        if not basepath:
            basepath = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(basepath, name)

    def bindingPointCoordChanged(self):
        e = n = 0
        try:
            n = float(self.omw.x_coord_LineEdit.text())
            e = float(self.omw.y_coord_LineEdit.text())
        except:
            print("Ошибка при чтении строк координат", n, e)
        if 50.0 <= n <= 57. and 20. <= e <= 33.:
            self.bindingPoint = GeoOperations.convertToZone35(QgsPointXY(e, n))
            bp = TempFeatures.BindingPointBuilder(self.bindingPoint, self.canvas)
            bp.makeFeature()
            self.tableWrapper.tableModel.setBindingPointXY(self.bindingPoint)
            self.tableWrapper.tableModel.refreshData()

    def getGPSCoords(self):
        gpsCoords = GeoOperations.getCoordFromGPS()
        if gpsCoords:
            self.omw.x_coord_LineEdit.setText(str(round(gpsCoords[0]), 10))
            self.omw.y_coord_LineEdit.setText(str(round(gpsCoords[1]), 10))

    def loadDataTable(self):
        datatable = DataTableWrapper(self.omw.tableWidget, int(self.tableType), int(self.coordType), 0, self.bindingPoint)
        datatable.deleteRows()
        self.omw.addNode_button.clicked.connect(datatable.addRow)
        self.omw.deleteNode_button.clicked.connect(datatable.deleteRow)
        self.omw.clearNodes_button.clicked.connect(datatable.deleteRows)
        self.omw.move_node_up_button.clicked.connect(datatable.move_row_up)
        self.omw.move_node_down_button.clicked.connect(datatable.move_row_down)
        # self.omw.add_line_node_button.clicked.connect(datatable.add_line_node)
        # self.omw.add_lesoseka_node_button.clicked.connect(datatable.add_lesoseka_node)
        return datatable

    def parseConfig(self):
        cf = config.Configurer('otvod')
        moduleSettings = cf.readConfigs()
        return([moduleSettings.get('tabletype', 'No data'), moduleSettings.get('coordtype', 'No data')])

    def otvodMenuSettings(self):
        self.sw = OtvodSettingsWindow()
        self.ui = self.sw.ui
        self.ui.tabletype_comboBox.setCurrentIndex(int(self.tableType))
        self.ui.coordtype_comboBox.setCurrentIndex(int(self.coordType))
        self.ui.magnIncl_lineEdit.setText(str(self.magneticInclination))
        dialogResult = self.sw.exec()
        if dialogResult == QDialog.Accepted:
            tableType = int(self.sw.tabletypes.get(self.ui.tabletype_comboBox.currentText()))
            coordType = int(self.sw.coordtypes.get(self.ui.coordtype_comboBox.currentText()))
            magneticInclination = self.ui.magnIncl_lineEdit.text()
            if self.tableType == tableType and self.coordType == coordType and self.magneticInclination == magneticInclination:
                return 0
            else:
                self.tableType = tableType
                self.coordType = coordType
                self.magneticInclination = magneticInclination
                if self.magneticInclination == "":
                    self.magneticInclination = 0
                self.tableWrapper.deleteRows()
                self.tableWrapper.tableModel.setParams(self.tableType, self.coordType, float(self.magneticInclination), self.bindingPoint)

    def saveDataToFile(self):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H.%M")
        filename = QFileDialog.getSaveFileName(None, 'Сохранить файл отвода', "Данные отвода от " + dt_string, "Файлы отвода (*.json)")[0]
        if not filename:
            return
        else:
            with open(filename, "w", encoding='utf8') as write_file:
                json.dump(self.tableWrapper, write_file, default=self.tableWrapper.encodeJSON, ensure_ascii=False, indent=4)

    def loadDataFromFile(self):
        table = self.tableWrapper.tableModel
        filename = QFileDialog.getOpenFileName(None, 'Открыть файл отвода', '', "Файлы отвода (*.json)")[0]
        if not filename:
            return
        else:
            with open(filename, "r", encoding='utf8') as read_file:
                data = json.load(read_file)
        if data:
            for p in data:
                for key, value in p.items():
                    if key == "Table":
                        self.tableType = data[0]['Table']['table_type']
                        btn = self.radio_group.button(self.tableType)
                        btn.setChecked(True)
                        self.coordType = data[0]['Table']['coord_type']
                        self.magneticInclination = data[0]['Table']['magnetic_inclination']
                        point35 = QgsPointXY(float(data[0]['Table']['BindingPointX']), float(data[0]['Table']['BindingPointY']))
                        point = GeoOperations.convertToWgs(point35)
                        self.omw.y_coord_LineEdit.setText(str(point.x()))
                        self.omw.x_coord_LineEdit.setText(str(point.y()))
                        self.canvas.setCenter(point35)
                        self.tableWrapper.deleteRows()
                        self.tableWrapper.tableModel.setParams(self.tableType, self.coordType, self.magneticInclination, self.bindingPoint)
                        continue
                    else:
                        # print("Здесь что-то не так: может создаваться лишняя строка (трудновоспроизводимый баг)")
                        self.tableWrapper.addRow()                        
                        i = 0                        
                        for k, v in value.items():
                            if table.horizontalHeaderItem(i).text() == "Румб" or table.horizontalHeaderItem(i).text() == "Тип":
                                comboboxCellWidget = table.cellWidget(int(key), int(i))
                                index = comboboxCellWidget.findText(str(v), Qt.MatchFixedString)
                                if index >= 0:
                                    comboboxCellWidget.setCurrentIndex(index)                                
                            item = QTableWidgetItem()
                            item.setText(str(v))
                            table.setItem(int(key), int(i), item)
                            i = i + 1

    # def buildTempCuttingArea(self):
    #     wgsBingdingPoint = GeoOperations.convertToWgs(self.bindingPoint)

    #     if int(wgsBingdingPoint.y()) not in range(50, 57) or int(wgsBingdingPoint.x()) not in range(20, 33):
    #         QMessageBox.information(None, "Ошибка модуля QGISLes", "Некорректная точка привязки")
    #     try:
    #         layer = QgsProject.instance().mapLayersByName("Пикеты")[0]
    #     except Exception as e:
    #         print(e)
    #         QMessageBox.information(None, "Ошибка модуля QGISLes", "Отсутствуют угловые точки")
    #         return
    #     else:
    #         def getResult(feature):
    #             # self.omw.outputLabel.setText("Внесите информацию о лесосеке")
    #             layerVd = QgsProject.instance().mapLayersByName("Выдела")[0]
    #             layerVd.removeSelection()

    #             dictAttr = {}

    #             sw = LesosekaInfo()
    #             gui = sw.gui
    #             gui.date.setDateTime(QDateTime.currentDateTime())
    #             dialogResult = sw.exec()
    #             if dialogResult == QDialog.Accepted:
    #                 dictAttr["num"] = gui.num.text()
    #                 # dictAttr["useType"] = gui.useType.text()
    #                 # dictAttr["cuttingType"] = gui.cuttingType.text()
    #                 # dictAttr["plot"] = gui.plot.text()
    #                 dictAttr["fio"] = gui.fio.text()
    #                 dictAttr["date"] = gui.date.text()
    #                 dictAttr["info"] = gui.info.toPlainText()
    #             else:
    #                 return
                                    
    #             self.cuttingArea = CuttingArea.CuttingArea(self.canvas, self.bindingPoint, layer, feature, dictAttr)
    #             zoomTool=QgsMapToolZoom(self.canvas, False)
    #             self.canvas.setMapTool(zoomTool)
    #             cuttingArea = self.cuttingArea.build()
    #             # расчет невязки
    #             # points = cuttingArea.geometry().asPolygon()[0][-2:]
    #             # az = GeoOperations.calculateAzimuth(points[0], points[1])
    #             # dist = GeoOperations.calculateDistance(points[0], points[1])

    #             # self.omw.outputLabel.setText("Невязка: {}°, {} м".format(str(round(float(az), 1)), str(round(float(dist), 1))))

    #             # print("Периметр", str(cuttingArea.geometry().length()))

    #         self.ppfm = MapTools.PeekStratumFromMap(self.canvas)
    #         self.canvas.setMapTool(self.ppfm)
    #         self.ppfm.signal.connect(getResult)
            
    #     self.omw.outputLabel.setText("Укажите выдел на карте")

    def saveCuttingArea(self):
        # print(self.cuttingArea)
        if self.cuttingArea == None:
            self.cuttingArea = self.canvasWidget.cuttingArea
        if self.cuttingArea == None:
            QMessageBox.information(None, "Ошибка модуля QGISLes", "Отсутствует лесосека. Постройте лесосеку, после чего будет возможность ее сохранить")
        else:
            self.cuttingArea.save()
            self.canvasWidget.btnControl.unlockReportBotton()
            self.omw.outputLabel.setText("Лесосека сохранена")

    def rotateCuttingArea(self, btn):
        try:
            rotate_value = float(self.omw.rotate_inclination.text())
            if (btn.text() == '<'):
                self.magneticInclination -= rotate_value
            elif(btn.text()) == ">":
                self.magneticInclination += rotate_value
        except:
            QMessageBox.information(None, "Ошибка модуля QGISLes", "Некорректное значение в поле магнитного склонения")
        self.tableWrapper.tableModel.setMagneticInclination(self.magneticInclination)
        self.tableWrapper.tableModel.refreshData()


    def deleteCuttingArea(self):
        try:
            layer = QgsProject.instance().mapLayersByName("Точка привязки")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Точка привязки")
        try:
            layer = QgsProject.instance().mapLayersByName("Лесосека временный слой")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Точка привязки")
        try:
            layer = QgsProject.instance().mapLayersByName("Опорные точки")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Опорные точки")
        try:
            layer = QgsProject.instance().mapLayersByName("Привязка временный слой")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Привязка временный слой")
        try:
            layer = QgsProject.instance().mapLayersByName("Пикеты")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Пикеты")
        self.omw.outputLabel.setText("Лесосека удалена")          
        self.canvasWidget.btnControl.lockLesosekaButtons()
        self.tableWrapper.deleteRows()
        self.omw.y_coord_LineEdit.clear()
        self.omw.x_coord_LineEdit.clear()     
        self.canvas.refresh()
        iface.mapCanvas().refresh()

    def generateReport(self):
        try:
            QgsProject.instance().mapLayersByName("Привязка временный слой")[0],
        except:
            layers = [
                QgsProject.instance().mapLayersByName("Точка привязки")[0], 
                QgsProject.instance().mapLayersByName("Выдела")[0], 
                # QgsProject.instance().mapLayersByName("Гидрография площадная")[0], 
                # QgsProject.instance().mapLayersByName("Дороги")[0], 
                QgsProject.instance().mapLayersByName("Кварталы")[0], 
                QgsProject.instance().mapLayersByName("Населенные пункты")[0], 
                QgsProject.instance().mapLayersByName("Лесосека временный слой")[0],
                # QgsProject.instance().mapLayersByName("Гидрография линейная")[0],            
                # QgsProject.instance().mapLayersByName("Привязка временный слой")[0],
                QgsProject.instance().mapLayersByName("Пикеты")[0]
                ]
        else:
            layers = [
                QgsProject.instance().mapLayersByName("Точка привязки")[0], 
                QgsProject.instance().mapLayersByName("Выдела")[0], 
                # QgsProject.instance().mapLayersByName("Гидрография площадная")[0], 
                # QgsProject.instance().mapLayersByName("Дороги")[0], 
                QgsProject.instance().mapLayersByName("Кварталы")[0], 
                QgsProject.instance().mapLayersByName("Населенные пункты")[0], 
                QgsProject.instance().mapLayersByName("Лесосека временный слой")[0],
                # QgsProject.instance().mapLayersByName("Гидрография линейная")[0],            
                QgsProject.instance().mapLayersByName("Привязка временный слой")[0],
                QgsProject.instance().mapLayersByName("Пикеты")[0]
                ]

        report = Report.Report(self.tableWrapper.tableModel, self.canvas, layers)
        path = report.generate()
        self.omw.outputLabel.setText("<a href=file:///{}>Открыть отчет</a>".format(os.path.realpath(path)))
        self.omw.outputLabel.setOpenExternalLinks(True)


class OtvodSettingsWindow(QDialog):
    def __init__(self, *args, **kwargs):
        super(OtvodSettingsWindow, self).__init__()
        self.ui = uiOtvodSettingDialog()
        self.ui.setupUi(self)
        self.tabletypes = {'Координаты': 0,
                           'Азимуты': 1,
                           'Румбы': 2}
        self.coordtypes = {'Десятичный': 0,
                           'Градусы/Минуты/Секунды': 1}
        self.ui.tabletype_comboBox.addItems([key for key, value in self.tabletypes.items()])
        self.ui.coordtype_comboBox.addItems([key for key, value in self.coordtypes.items()])


class LesosekaInfo(QDialog):

    def __init__(self, *args, **kwargs):
        super(LesosekaInfo, self).__init__()
        self.ui = uiLesosekaInfo()
        self.ui.setupUi(self)
        self.lhNumber = None

    def setUpValues(self):

        def workerFinished(result):
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()
            self.ui.leshos.addItem(result[0][0])
            self.ui.lesnich.addItems(result[1])
            self.lhNumber = result[2]
            # self.gui.num_lch.setText(result[0][1][0])

        worker = ForestObjWorker()

        thread = QtCore.QThread()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        thread.started.connect(worker.run)
        thread.start()

        self.ui.date.setDateTime(QDateTime.currentDateTime())

    def populateValues(self, items):
        self.ui.num.setText()
        dictAttr["num_lch"] = 0
        dictAttr["num_kv"] = 0
        dictAttr["num_vd"] = 0
        dictAttr["area"] = 0
        dictAttr["leshos"] = sw.lhNumber
        dictAttr["num"] = ui.num.text()
        dictAttr["useType"] = ""
        dictAttr["cuttingType"] = ""
        dictAttr["plot"] = ""         
        dictAttr["fio"] = ui.fio.text()
        dictAttr["date"] = ui.date.text()
        dictAttr["info"] = ui.info.toPlainText()
        dictAttr["num_vds"] = ui.num_vds.text()
        dictAttr["leshos_text"] = ui.leshos.currentText()
        dictAttr["lesnich_text"] = ui.lesnich.currentText()        
        # print(items, "<=======")


class canvasWidget(QgsMapCanvas):

    def __init__(self, otvodMainWindow, layers, rct, table):

        self.predefinedScales = [500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]

        super(canvasWidget, self).__init__()
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

    # def lockLesosekaButtons(self):
    #     self.btnControl.lockLesosekaButtons()
    
    def getButtons(self):
        return [
            self.omw.buildLesoseka_Button,
            self.omw.editAttributes_button,
            self.omw.saveLesoseka_Button,
            self.omw.deleteLesoseka_Button,
            self.omw.generateReport_Button,
        ]

    def initScalesBox(self):
        box = self.omw.canvas_scale_combo
        for x in self.predefinedScales:
            box.addItem(str(x))
        if self.canvas:
            box.currentTextChanged.connect(lambda x: self.canvas.zoomScale(int(x)))

    def onScaleChanged(self):
        self.canvas.scaleChanged.disconnect(self.onScaleChanged)
        scale = self.canvas.scale()
        targetScale = min(self.predefinedScales, key=lambda x: abs(int(x) - scale))
        self.canvas.zoomScale(targetScale)
        self.omw.canvas_scale_combo.setCurrentText(str(targetScale))
        self.canvas.scaleChanged.connect(self.onScaleChanged)

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

        crs=QgsCoordinateReferenceSystem('EPSG:32635')
        canvas.setDestinationCrs(crs)
        mapSettings = canvas.mapSettings()
        canvas.setExtent(self.rct)
        # canvas.zoomScale(10000)

        canvas.refresh()
        return canvas

    def getCanvas(self):
        return self.canvas

    def findAzimuth(self, btn, btnState):
        
        def getResult(result):
            self.omw.outputLabel.setText("Аз.: " + str(round(result[0], 1)) + "°. " + "Раст.: " + str(round(result[1], 2)) + " м.")

        if btnState == True:
            self.amt = MapTools.AzimuthMapTool(self.canvas)
            self.canvas.setMapTool(self.amt)
            self.amt.signal.connect(getResult)
        elif btnState == False:
            self.amt.deactivate()
            zoomTool=QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(zoomTool)

    def build_from_map(self, btn, btnState, btnGroup):
        
        def getResult(result):
            point =  GeoOperations.convertToWgs(result[0][0])
            self.omw.y_coord_LineEdit.setText(str(round(point.x(), 10)))
            self.omw.x_coord_LineEdit.setText(str(round(point.y(), 10)))
            # self.omw.coord_radio_button.clicked.emit()
            self.table.appendTableFromMap(result[1:])
            self.buildLesosekaFromMap()
            btn.toggle()

        if btnState == True:
            self.omw.coord_radio_button.toggle()
            self.table.deleteRows()
            self.bfm = MapTools.BuildFromMapTool(self.canvas)
            self.canvas.setMapTool(self.bfm)
            self.bfm.signal.connect(getResult)

        elif btnState == False:
            try:
                self.bfm.deactivate()
            except:
                print("Ошибка деактивации OtvodModule строка 502")
            zoomTool=QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(zoomTool)
            for button in btnGroup:
                button.setEnabled(True)
        

    def buildLesosekaFromMap(self):

        try:
            layer = QgsProject.instance().mapLayersByName("Пикеты")[0]
        except Exception as e:
            print(e)
            QMessageBox.information(None, "Ошибка модуля QGISLes", "Отсутствуют угловые точки")
            return

        # layer = QgsProject.instance().mapLayersByName("Пикеты")[0]

        layerVd = QgsProject.instance().mapLayersByName("Выдела")[0]
        layerVd.removeSelection()

        dictAttr = {}

        sw = LesosekaInfo()
        ui = sw.ui
        sw.setUpValues()
        dialogResult = sw.exec()
        if dialogResult == QDialog.Accepted:
            self.btnControl.unlockSaveDeleteButtons()
            dictAttr["num_lch"] = 0
            dictAttr["num_kv"] = 0
            dictAttr["num_vd"] = 0
            dictAttr["area"] = 0
            dictAttr["leshos"] = sw.lhNumber
            dictAttr["num"] = ui.num.text()
            dictAttr["useType"] = ""
            dictAttr["cuttingType"] = ""
            dictAttr["plot"] = ""         
            dictAttr["fio"] = ui.fio.text()
            dictAttr["date"] = ui.date.text()
            dictAttr["info"] = ui.info.toPlainText()
            dictAttr["num_vds"] = ui.num_vds.text()
            dictAttr["leshos_text"] = ui.leshos.currentText()
            dictAttr["lesnich_text"] = ui.lesnich.currentText()
        else:
            return
        n = float(self.omw.x_coord_LineEdit.text())
        e = float(self.omw.y_coord_LineEdit.text())
        bindingPoint = GeoOperations.convertToZone35(QgsPointXY(e, n))
        self.cuttingArea = CuttingArea.CuttingArea(self.canvas, bindingPoint, layer, None, dictAttr)
        zoomTool=QgsMapToolZoom(self.canvas, False)
        self.canvas.setMapTool(zoomTool)
        cuttingArea = self.cuttingArea.build()

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
                zoomTool=QgsMapToolZoom(self.canvas, False)
                self.canvas.setMapTool(zoomTool)
        
        if btnState == True:
            self.ppfm = MapTools.PeekPointFromMap(self.canvas)
            self.canvas.setMapTool(self.ppfm)
            self.ppfm.signal.connect(getResult)

        elif btnState == False:
            zoomTool=QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(zoomTool)
            
    def peekVydelFromMap(self, btn, btnState):

        def getResult(selectedFeature):
            self.bap = TempFeatures.AnchorPointBuilder(self.canvas, selectedFeature)
            self.bap.makeFeature()

            self.bcp = TempFeatures.CuttingAreaBuilder(self.canvas, selectedFeature)
            self.bcp.makeFeature()

            if btnState == True:
                btn.setChecked(False)
                self.ppfm.deactivate()
                zoomTool=QgsMapToolZoom(self.canvas, False)
                self.canvas.setMapTool(zoomTool)
        
        if btnState == True:
            self.ppfm = MapTools.PeekStratumFromMap(self.canvas)
            self.canvas.setMapTool(self.ppfm)
            self.ppfm.signal.connect(getResult)

        elif btnState == False:
            zoomTool=QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(zoomTool)

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