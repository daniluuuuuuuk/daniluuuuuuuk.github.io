# from qgis.PyQt.QtGui import QIcon
# from qgis.PyQt.QtWidgets import QAction, QToolBar, QDialog, QMessageBox
# from .gui import filterActionWidget, settingsDialog
# from . import Filter, util, res, Settings, PostgisDB
# from qgis.core import QgsProject
# from .tools import module_errors as er
# from .modules.otvod.OtvodModule import OtvodController
# from .modules.otvod.tools.MapTools import RectangleMapTool
# from .tools import CuttingAreaPeeker as peeker
# from qgis.gui import QgsMapToolZoom

import sys
import traceback
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QDialog, QMessageBox
from .gui import filterActionWidget, settingsDialog
from . import Filter, util, res, Settings, PostgisDB
from qgis.core import QgsProject
from .tools import module_errors as er
from .modules.otvod.OtvodController import OtvodController
from .modules.otvod.tools.mapTools.RectangleMapTool import RectangleMapTool
from .tools import CuttingAreaPeeker as peeker
from qgis.gui import QgsMapToolZoom
from qgis.core import QgsMessageLog, Qgis
from .modules.trial_area.restatements import Restatement


class QgsLes:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

    def initGui(self):

        self.qgsLesToolbar = self.iface.mainWindow().findChild(
            QToolBar, "QGIS Отвод лесосек"
        )
        if not self.qgsLesToolbar:
            self.qgsLesToolbar = self.iface.addToolBar("QGIS Отвод лесосек")
            self.qgsLesToolbar.setObjectName("QGIS Отвод лесосек")

        self.otvodAction = QAction(
            QIcon(util.resolvePath("res\\icon2.png")),
            "Отвод участка",
            self.iface.mainWindow(),
        )
        self.otvodAction.triggered.connect(self.otvodButtonClicked)

        # self.mdolAction = QAction(
        #     QIcon(util.resolvePath("res\\icon4.png")),
        #     "Материально-денежная оценка",
        #     self.iface.mainWindow(),
        # )
        # self.mdolAction.triggered.connect(self.mdolButtonClicked)

        self.countAction = QAction(
            QIcon(util.resolvePath("res\\icon.png")), "Перечет", self.iface.mainWindow()
        )
        self.countAction.triggered.connect(self.countButtonClicked)

        # if not PostgisDB.PostGisDB().setConnection():
        #     QMessageBox.information(
        #         None, er.MODULE_ERROR, er.DATABASE_CONNECTION_ERROR + er.FILTER_DISABLED
        #     )
        # else:
        #     self.fter = Filter.FilterWidget(self.iface, QgsProject.instance())
        #     self.filterAction = self.fter.getFilterWidget()
        #     self.qgsLesToolbar.addWidget(self.filterAction)
        #     self.filterButtonAction = QAction(
        #         QIcon(util.resolvePath("res\\icon3.png")),
        #         "Поиск",
        #         self.iface.mainWindow(),
        #     )
        #     self.filterAction.setDefaultAction(self.filterButtonAction)

        self.settingsAction = QAction(
            QIcon(util.resolvePath("res\\settings.png")),
            "Настройки",
            self.iface.mainWindow(),
        )

        self.settingsAction.triggered.connect(lambda: Settings.SettingsController())

        self.qgsLesToolbar.addAction(self.otvodAction)
        self.qgsLesToolbar.addAction(self.countAction)
        # self.qgsLesToolbar.addAction(self.mdolAction)
        self.qgsLesToolbar.addAction(self.settingsAction)

    def unload(self):
        del self.qgsLesToolbar

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
        # print("main podcast scale", self.canvas.scale())
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

            zoomTool = QgsMapToolZoom(self.canvas, False)
            self.canvas.setMapTool(zoomTool)

        self.pkr = peeker.PeekStratumFromMap(self.canvas)
        self.canvas.setMapTool(self.pkr)
        self.pkr.signal.connect(getResult)

    # def mdolButtonClicked(self):

    #     def getResult(feature):
    #         if feature:
    #             uid = feature['uid']
    #             self.ev = Evaluation(uid)
    #             self.ev.show()

    #         zoomTool = QgsMapToolZoom(self.canvas, False)
    #         self.canvas.setMapTool(zoomTool)

    #     self.pkr = peeker.PeekStratumFromMap(self.canvas)
    #     self.canvas.setMapTool(self.pkr)
    #     self.pkr.signal.connect(getResult)

    def filterButtonClicked(self):
        print("show filter Window")
