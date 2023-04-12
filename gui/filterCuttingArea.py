"""
Фильтр используется для отображения необходимых пользователю лесосек в окне "Экспорт/Импорт лесосек" по заданным параметрам.
"""

from qgis.PyQt.QtWidgets import QToolButton, QMenu, QWidgetAction, QWidget, QMessageBox
from . import filterCuttigAreaWidget
from qgis.core import QgsProject
from PyQt5 import QtCore
from ..ForestObject import ForestObject, ForestEnterprise, Forestry, Quarter, Stratum
from abc import ABCMeta, abstractmethod
import re
from qgis.utils import iface

# from .exportImportCuttingAreasDialog import ExportImportCuttingAreaWindow



class FilterWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.ui = filterCuttigAreaWidget.Ui_Form()
        self.ui.setupUi(self)

    def getFilterWidget(self):
        self.filterButton = QToolButton()
        self.filterButton.setMinimumSize(70, 20)
        self.filterButton.setStyleSheet(
            'QToolButton::menu-indicator { image: none;}'
            
        )
        
        self.filterButton.setMenu(QMenu())
        self.filterButton.setPopupMode(QToolButton.InstantPopup)
        self.qwa = QWidgetAction(None)
        self.qwa.setDefaultWidget(self)
        m = self.filterButton.menu()
        m.addAction(self.qwa)
        return self.filterButton


class FilterWidgetController:

    def __init__(self, view, current_export_window, new_export_window):
        
        def setEnterpriseName(result):
            if result:
                # self.enterprise.name = result[0][0][0]
                # self.view.ui.leshoz_combobox_3.setCurrentText(self.enterprise.name)
                self.view.ui.lch_combobox_3.lineEdit().setCursorPosition(0)
                self.view.ui.lch_combobox_3.addItems(self.loadForestries(result[1][0:]))
                # self.view.ui.lch_combobox_3.lineEdit().setCursorPosition(0)
            else:
                QMessageBox.information(None, 'Ошибка', "Лесничества не найдены. Проверьте файл конфигурации.")
        
        self.current_export_window = current_export_window
        self.new_export_window = new_export_window
        self.view = view
        
        self.fo = ForestObject()
        
        self.enterprise = ForestEnterprise()
        self.forestry = Forestry()
        self.quarter = Quarter()
        self.stratum = Stratum()
        self.cutting_area_number = 0

        self.enterprise.nameLoaded.connect(setEnterpriseName)
        self.initWidgetData()

        self.view.ui.lch_combobox_3.currentIndexChanged.connect(self.changeForestry)
        self.view.ui.kv_combobox_3.currentIndexChanged.connect(self.changeQuarter)
        self.view.ui.vd_combobox_3.currentIndexChanged.connect(self.changeStratum)
        self.view.ui.lesos_combobox_3.currentTextChanged.connect(self.changeCuttingArea)

        self.view.ui.doFilter_PushButton_3.clicked.connect(self.filter)
        self.view.ui.clearFilter_pushButton_3.clicked.connect(self.clear)

    def loadForestries(self, result):
        forestries = []
        forestries.append(str(0) +  ' ' + 'Все')
        i = 1
        for fr in result:
            forestries.append(str(i) + ' ' + fr[0])
            i += 1
        return forestries

    def initWidgetData(self):
        self.enterprise.setNameFromDb()

    def changeForestry(self):
        self.comboboxClear(self.view.ui.kv_combobox_3, self.view.ui.vd_combobox_3)
        if self.view.ui.lch_combobox_3.currentIndex() == -1 or self.view.ui.lch_combobox_3.currentText() == "":
            self.forestry.number = ""
        else:
            self.forestry.number = re.findall('\d+', str(self.view.ui.lch_combobox_3.currentText()))[0]
            self.view.ui.kv_combobox_3.addItems(self.quarter.getAllQuarters(self.forestry.number))
            self.clearComboboxIndex(self.view.ui.kv_combobox_3, self.view.ui.vd_combobox_3)

    def changeQuarter(self):
        self.comboboxClear(self.view.ui.vd_combobox_3)
        if self.view.ui.kv_combobox_3.currentIndex() == -1 or self.view.ui.kv_combobox_3.currentText() == "":
            self.quarter.number = ""
        else:
            self.quarter.number = self.view.ui.kv_combobox_3.currentText()
            self.view.ui.vd_combobox_3.addItems(self.stratum.getAllStratums(self.forestry.number, self.quarter.number))
            self.clearComboboxIndex(self.view.ui.vd_combobox_3)

    def changeStratum(self):
        self.comboboxClear(self.view.ui.lesos_combobox_3)
        if self.view.ui.vd_combobox_3.currentIndex() == -1 or self.view.ui.vd_combobox_3.currentText() == "":
            self.stratum.number = ""
        else:
            self.stratum.number = self.view.ui.vd_combobox_3.currentText()
            self.clearComboboxIndex(self.view.ui.lesos_combobox_3)

    def changeCuttingArea(self):
        self.cutting_area_number = self.view.ui.lesos_combobox_3.currentText()


    def comboboxClear(self, *args):
        for arg in args:
            arg.clear()

    def clearComboboxIndex(self, *args):
        for arg in args:
            arg.setCurrentIndex(-1)

    def clear(self):
        self.clearComboboxIndex(self.view.ui.lch_combobox_3, self.view.ui.kv_combobox_3, self.view.ui.vd_combobox_3, self.view.ui.lesos_combobox_3)
        self.comboboxClear(self.view.ui.kv_combobox_3, self.view.ui.vd_combobox_3, self.view.ui.lesos_combobox_3)
    
    def filter(self):
        def getSelectedUids():
            lr = QgsProject.instance().mapLayersByName("Лесосеки")[0]
            return [feature["uid"] for feature in lr.selectedFeatures()]
        close_window = self.current_export_window
        close_window.hide()



        export_import_cutting_area_window = self.new_export_window(
                selected_cutting_areas=getSelectedUids(),
                forestry_number=self.forestry.number,
                quarter_number=self.quarter.number,
                stratum_number=self.stratum.number,
                cutting_area_number=self.cutting_area_number
            )
        
        
        export_import_cutting_area_window.exec()
        