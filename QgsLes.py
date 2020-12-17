from PyQt5 import QtWidgets
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar
from . import Filter, util, Settings, PostgisDB
from qgis.core import QgsProject
from .modules.otvod.OtvodController import OtvodController
from .modules.otvod.tools.mapTools.RectangleMapTool import RectangleMapTool
from .tools import CuttingAreaPeeker as peeker
from qgis.gui import QgsMapToolZoom
from qgis.core import Qgis
from .modules.trees_accounting.src.restatements import Restatement
from .modules.trees_accounting.src.areas_list import AreasList
from .tools.ProjectInitializer import QgsProjectInitializer
from .tools.TaxationLoader import Worker as taxWorker
from .tools import config

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
        self.cf = config.Configurer('dbconnection')
        btsettings = self.cf.readConfigs()
        user = btsettings.get('user')
        password = btsettings.get('password')
        host = btsettings.get('host')
        port = btsettings.get('port')
        database = btsettings.get('database')
        if not user or not password or not host or not port or not database:
            return False
        return True

    def initGui(self):
        pass

    def unload(self):
        del self

class QgsLes:
    def __init__(self, iface, runnable):
        self.iface = iface
        self.runnable = runnable
        self.canvas = self.iface.mapCanvas()
        QgsProject.instance().legendLayersAdded.connect(self.ifKvLayerReady)
        self.filter = None

    def ifKvLayerReady(self, layer):
        if layer[0].name() == 'Кварталы' and self.filter == None and self.runnable:
            self.initFilter()

    def initFilter(self):
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
            self.iface.messageBar().pushMessage("Ошибка модуля отвода", "Отсутствует подключение к базе данных. Модуль отключен", level=Qgis.Critical, duration=15)
            self.pluginIsActive = False
            return

        self.otvodAction = QAction(
            QIcon(util.resolvePath("res\\icon2.png")),
            "Отвод участка",
            self.iface.mainWindow(),
        )
        self.otvodAction.triggered.connect(self.otvodButtonClicked)

        self.taxationAction = QAction(
            QIcon(util.resolvePath("res\\info.png")),
            "Информация о выделе",
            self.iface.mainWindow(),
        )
        self.taxationAction.triggered.connect(self.taxationButtonClicked)        

        self.countAction = QAction(
            QIcon(util.resolvePath("res\\icon.png")), "Перечет", self.iface.mainWindow()
        )
        self.countAction.triggered.connect(self.countButtonClicked)

        self.settingsAction = QAction(
            QIcon(util.resolvePath("res\\settings.png")),
            "Настройки",
            self.iface.mainWindow(),
        )

        self.settingsAction.triggered.connect(lambda: Settings.SettingsController())

        self.initProjectAction = QAction(
            QIcon(util.resolvePath("res\\download.png")),
            "Инициализировать проект",
            self.iface.mainWindow(),
        )
        self.initProjectAction.triggered.connect(self.initProjectClicked)
        
        self.qgsLesToolbar.addAction(self.taxationAction)
        self.qgsLesToolbar.addAction(self.otvodAction)
        self.qgsLesToolbar.addAction(self.countAction)
        self.qgsLesToolbar.addAction(self.settingsAction)
        self.qgsLesToolbar.addAction(self.initProjectAction)

        if QgsProject.instance().mapLayersByName('Выдела'):
            self.initFilter()

    def initProjectClicked(self):
        self.initializer = QgsProjectInitializer(self.iface)

    def unload(self):
        del self.qgsLesToolbar

    def taxationButtonClicked(self):
        def getResult(feature):

            if feature:
                txwrker = taxWorker(feature)
                txwrker.run()

            zoomTool = QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(zoomTool)            

        self.pkr = peeker.PeekStratumFromMap(self.canvas, 'Выдела')
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

        self.rmt = RectangleMapTool(self.canvas)
        self.rmt.signal.connect(getMapRect)
        self.canvas.setMapTool(self.rmt)

    def countButtonClicked(self):
        def getResult(feature):
            if feature:
                uid = feature["uid"]
                self.rst = Restatement(uid)
                self.rst.show()

            if not feature:
                response_window_message = QtWidgets.QMessageBox.warning(
                    None,
                    "Внимание",
                    "Не выбрана пробная площадь.\n"
                    "Вы хотите создать запись пробной площади без картографической составляющей?",
                    buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                )
                if response_window_message == 16384:  # если нажали Yes
                    # Вызываю окно первоначальных характеристик
                    self.rst = AreasList()
                    self.rst.show()

                if response_window_message == 65536:  # Если нажали No
                    pass

            zoomTool = QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(zoomTool)

        self.pkr = peeker.PeekStratumFromMap(self.canvas, 'Лесосеки')
        self.canvas.setMapTool(self.pkr)
        self.pkr.signal.connect(getResult)
