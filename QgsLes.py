from PyQt5 import QtWidgets
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
    QToolBar,
    QDialog,
    QLabel,
    QVBoxLayout,
    QPushButton,
)
from . import Filter, util, Settings, PostgisDB
from qgis.core import QgsProject
from .modules.otvod.OtvodController import OtvodController
from .modules.otvod.tools.mapTools.RectangleMapTool import RectangleMapTool
from .modules.otvod.tools.mapTools import PeekStratumFromMap as peeker

# from .tools import CuttingAreaPeeker as peeker
from qgis.gui import QgsMapToolZoom
from qgis.core import Qgis, QgsApplication
from .modules.trees_accounting.src.trees_accounting import TaMainWindow
from .tools.ProjectInitializer import QgsProjectInitializer
from .tools.TaxationLoader import Worker as taxWorker
from .tools import config, AreaController, AreaFilter
from .tools.ThematicController import (
    ThematicController,
    ChooseThematicMapDialog,
)

from .gui.taxationDescription import (
    TaxationDescription as TaxationDescriptionDialog,
)
from .gui.exportImportCuttingAreasDialog import ExportImportCuttingAreaWindow
from qgis.PyQt.QtCore import Qt
from .tools.thermal_anomaly.ThermalAnomalyDialog import ThermalAnomalyDialog


class DatabaseConnectionVerifier:
    def __init__(self, iface):
        super().__init__()
        self.iface = iface

    def verifyConfig(self):
        if not self.configValid():
            Settings.SettingsController()
        if not PostgisDB.PostGisDB().setConnection():
            return False
        return True

    def configValid(self):
        self.cf = config.Configurer("dbconnection")
        btsettings = self.cf.readConfigs()
        user = btsettings.get("user")
        password = btsettings.get("password")
        host = btsettings.get("host")
        port = btsettings.get("port")
        database = btsettings.get("database")
        if not user or not password or not host or not port or not database:
            return False
        return True

    def initGui(self):
        pass

    def unload(self):
        del self


class QgsLes:
    """Класс добавляет кнопки модуля на панели инструментов. 
    Содержит обработчики кликов, инициализирует фильтр (поиск)
    по лесничеству, кварталу, выделу.
    """
    def __init__(self, iface, runnable):
        self.iface = iface
        self.runnable = runnable
        self.canvas = self.iface.mapCanvas()
        QgsProject.instance().legendLayersAdded.connect(self.ifVydLayerReady)
        QgsProject.instance().cleared.connect(self.removeFilterButton)
        self.filter = None
        self.dockWidget = None
        QgsApplication.messageLog().messageReceived.connect(
            self.write_log_message
        )

    def removeFilterButton(self):
        try:
            if self.qgsLesToolbar:
                for action in self.qgsLesToolbar.actions():
                    if not action.text():
                        self.qgsLesToolbar.removeAction(action)
        except:
            # issue: при закрытии кугиса тулбар удаляется первее анлодинга проекта -> кугис крашится
            pass

    def write_log_message(self, message, tag, level):
        with open(util.resolvePath("tmp/qgis.log"), "a") as logfile:
            logfile.write(
                "{tag}({level}): {message}".format(
                    tag=tag, level=level, message=message
                )
            )

    def ifVydLayerReady(self, layer):
        if layer[0].name() == "Выдела" and self.runnable:
            self.initFilter()

    def initFilter(self):
        def checkNumLhzConfig():
            def writeConfigs(cf):
                lr = QgsProject.instance().mapLayersByName("Выдела")[0]
                try:
                    feature = lr.getFeature(1)
                    location = settings.get("location")
                    num_lhz = str(int(feature["num_lhz"]))
                    gplho = settings.get("gplho")
                    leshoz = settings.get("leshoz")
                    lesnich = settings.get("lesnich")
                    lhType = settings.get("type")
                    lhCode = str(feature["code_lh"])
                    settingsDict = {
                        "location": location,
                        "num_lhz": num_lhz,
                        "type": lhType,
                        "gplho": gplho,
                        "leshoz": leshoz,
                        "lesnich": lesnich,
                        "code_lh": lhCode,
                    }
                    cf = config.Configurer("enterprise", settingsDict)
                    cf.writeConfigs()
                except Exception as e:
                    print(e)

            cf = config.Configurer("enterprise")
            settings = cf.readConfigs()
            # numLhz = settings.get('num_lhz')
            # if not numLhz:
            writeConfigs(cf)

        checkNumLhzConfig()

        self.filter = Filter.FilterWidget()
        self.filterAction = self.filter.getFilterWidget()
        self.qgsLesToolbar.addWidget(self.filterAction)
        self.filterButtonAction = QAction(
            QIcon(util.resolvePath("res\\icon3.png")),
            "Поиск",
            self.iface.mainWindow(),
        )
        self.filterAction.setDefaultAction(self.filterButtonAction)
        self.ctrl = Filter.FilterWidgetController(self.filter, self.iface)

    def initGui(self):

        self.qgsLesToolbar = self.iface.mainWindow().findChild(
            QToolBar, "QGIS Отвод лесосек"
        )

        if not self.qgsLesToolbar:
            self.qgsLesToolbar = self.iface.addToolBar("QGIS Отвод лесосек")
            self.qgsLesToolbar.setObjectName("QGIS Отвод лесосек")

        if not self.runnable:
            # mes = self.iface.messageBar().createMessage(
            #     "Ошибка модуля отвода",
            #     "Отсутствует подключение к базе данных. Модуль отключен",
            # )
            widget = self.iface.messageBar().createMessage(
                "Ошибка модуля отвода",
                "Отсутствует подключение к базе данных. Модуль отключен",
            )
            button = QPushButton(widget)
            button.setText("Настроить")
            button.pressed.connect(lambda: Settings.SettingsController())
            widget.layout().addWidget(button)
            self.iface.messageBar().pushWidget(
                widget, level=Qgis.Critical, duration=45
            )
            self.pluginIsActive = False
            return

        self.otvodAction = QAction(
            QIcon(util.resolvePath("res\\icon2.png")),
            "Отвод участка",
            self.iface.mainWindow(),
        )
        self.otvodAction.triggered.connect(self.otvodButtonClicked)

        self.controlAreaAction = QAction(
            QIcon(util.resolvePath("res\\icon5.png")),
            "Управление лесосекой",
            self.iface.mainWindow(),
        )
        self.controlAreaAction.triggered.connect(self.controlAreaClicked)

        self.thematicAction = QAction(
            QIcon(util.resolvePath("res\\icon-7.png")),
            "Тематические карты",
            self.iface.mainWindow(),
        )
        self.thematicAction.triggered.connect(self.thematicClicked)

        self.taxationAction = QAction(
            QIcon(util.resolvePath("res\\info.png")),
            "Информация о выделе",
            self.iface.mainWindow(),
        )
        self.taxationAction.triggered.connect(self.taxationButtonClicked)

        self.countAction = QAction(
            QIcon(util.resolvePath("res\\icon.png")),
            "Перечет",
            self.iface.mainWindow(),
        )
        self.countAction.triggered.connect(self.countButtonClicked)

        self.filterAreaAction = QAction(
            QIcon(util.resolvePath("res\\icon6.png")),
            "Панель инструментов",
            self.iface.mainWindow(),
        )
        self.filterAreaAction.setCheckable(True)
        self.filterAreaAction.triggered.connect(self.filterAreaButtonClicked)

        self.settingsAction = QAction(
            QIcon(util.resolvePath("res\\settings.png")),
            "Настройки",
            self.iface.mainWindow(),
        )

        self.settingsAction.triggered.connect(
            lambda: Settings.SettingsController()
        )

        self.exportImportAction = QAction(
            QIcon(util.resolvePath("res\\export_import.png")),
            "Экспорт/Импорт лесосек",
            self.iface.mainWindow(),
        )

        self.exportImportAction.triggered.connect(
            self.exportImportCuttingAreaClicked
        )

        self.initProjectAction = QAction(
            QIcon(util.resolvePath("res\\download.png")),
            "Инициализировать проект",
            self.iface.mainWindow(),
        )
        self.initProjectAction.triggered.connect(self.initProjectClicked)

        self.thermalAnomalyAction = QAction(
            QIcon(util.resolvePath("res\\fire.png")),
            "Поиск тепловых аномалий",
            self.iface.mainWindow(),
        )
        self.thermalAnomalyAction.triggered.connect(self.thermalAnomalyClicked)

        self.qgsLesToolbar.addAction(self.taxationAction)
        self.qgsLesToolbar.addAction(self.otvodAction)
        self.qgsLesToolbar.addAction(self.countAction)
        self.qgsLesToolbar.addAction(self.controlAreaAction)
        self.qgsLesToolbar.addAction(self.thematicAction)
        self.qgsLesToolbar.addAction(self.filterAreaAction)
        self.qgsLesToolbar.addAction(self.settingsAction)
        self.qgsLesToolbar.addAction(self.initProjectAction)
        self.qgsLesToolbar.addAction(self.exportImportAction)
        self.qgsLesToolbar.addAction(self.thermalAnomalyAction)

        if QgsProject.instance().mapLayersByName("Выдела"):
            self.initFilter()
    
    def thermalAnomalyClicked(self):
        self.dlg = ThermalAnomalyDialog(self.iface)
        self.dlg.show()

    def filterAreaButtonClicked(self, checked):
        if not QgsProject.instance().mapLayersByName("Лесосеки"):
            QtWidgets.QMessageBox.warning(
                None, "Ошибка", "Отсутствует слой лесосек."
            )
            return
        if not checked and self.dockWidget:
            self.iface.removeDockWidget(self.dockWidget)
        else:
            self.dockWidget = AreaFilter.AreaFilterDockWidget(
                self.filterAreaAction
            )
            self.filgetAreaCtrlr = AreaFilter.AreaFilterController(
                self.dockWidget
            )
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget)

    def thematicClicked(self):
        def rerenderStyle():
            thMap = self.dialog.thematicCombobox.currentText()
            thMapCtrlr = ThematicController(self.dialog, thMap)

        self.dialog = ChooseThematicMapDialog()
        self.dialog.thematicCombobox.currentIndexChanged.connect(rerenderStyle)
        self.dialog.exec()
        # if self.dialog.exec() == QDialog.Applied:
        #     thMap = self.dialog.thematicCombobox.currentText()
        #     thMapCtrlr = ThematicController(thMap)

    def controlAreaClicked(self):
        def getResult(feature):
            if feature:
                # zoomTool = QgsMapToolZoom(self.canvas, False)
                # self.canvas.setMapTool(zoomTool)
                self.ctrlr = AreaController.AreaController(feature)
            else:
                QtWidgets.QMessageBox.warning(
                    None, "Ошибка", "Не выбрана лесосека."
                )

        self.showInfoMessage("А теперь нажмите на лесосеку")
        self.pkr = peeker.PeekStratumFromMap(self.canvas, "Лесосеки")
        self.canvas.setMapTool(self.pkr)
        self.pkr.signal.connect(getResult)

    def showInfoMessage(self, text):
        self.iface.messageBar().pushMessage(
            "", text, level=Qgis.Info, duration=3
        )

    def initProjectClicked(self):
        self.initializer = QgsProjectInitializer(
            self.iface, self.qgsLesToolbar
        )

    def unload(self):
        del self.qgsLesToolbar
        if self.dockWidget:
            del self.dockWidget

    def taxationButtonClicked(self):
        def getResult(feature):
            def showTaxationDetails(details):
                tdd = TaxationDescriptionDialog(tax_data=details)
                tdd.exec()

            if feature:
                txwrker = taxWorker(feature)
                txwrker.finished.connect(showTaxationDetails)
                txwrker.run()

            # zoomTool = QgsMapToolZoom(self.canvas, False)
            # self.canvas.setMapTool(zoomTool)

        self.showInfoMessage("Укажите выдел")
        self.pkr = peeker.PeekStratumFromMap(self.canvas, "Выдела")
        self.canvas.setMapTool(self.pkr)
        self.pkr.signal.connect(getResult)

    def otvodButtonClicked(self):
        def getMapRect(rct):
            layer_list = QgsProject.instance().layerTreeRoot().children()
            layers = [
                lyr.layer()
                for lyr in layer_list
                if lyr.name() == "Кварталы"
                or lyr.name() == "Выдела"
                or lyr.name() == "Населенные пункты"
                or lyr.name() == "Гидрография площадная"
            ]
            self.oc = OtvodController(layers, rct)
            self.rmt.reset()
            try:
                self.canvas.setMapTool(currentMapTool)
            except:
                self.canvas.unsetMapTool(self.rmt)

        self.canvas = self.iface.mapCanvas()

        try:
            currentMapTool = self.canvas.mapTool()
        except:
            pass
        self.showInfoMessage("Выделите область на карте")
        self.rmt = RectangleMapTool(self.canvas)
        self.rmt.signal.connect(getMapRect)
        self.canvas.setMapTool(self.rmt)

    def countButtonClicked(self):
        def getResult(feature):
            if feature:
                uid = feature["uid"]
                self.rst = TaMainWindow(uid)
                self.rst.show()
            else:
                QtWidgets.QMessageBox.warning(
                    None, "Внимание", "Не выбрана лесосека."
                )

            zoomTool = QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(zoomTool)

        self.showInfoMessage("А теперь нажмите на лесосеку")
        self.pkr = peeker.PeekStratumFromMap(self.canvas, "Лесосеки")
        self.canvas.setMapTool(self.pkr)
        self.pkr.signal.connect(getResult)

    def exportImportCuttingAreaClicked(self):
        def getSelectedUids():
            lr = QgsProject.instance().mapLayersByName("Лесосеки")[0]
            return [feature["uid"] for feature in lr.selectedFeatures()]

        export_import_cutting_area_window = ExportImportCuttingAreaWindow(
            selected_cutting_areas=getSelectedUids()
        )
        export_import_cutting_area_window.exec()
