from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QToolButton, QMenu, QWidgetAction, QWidget, QMessageBox
from .gui import filterActionWidget
from qgis.core import QgsProject
from . import util
from .ForestObject import ForestObject, ForestEnterprise, Forestry, Quarter, Stratum
from abc import ABCMeta, abstractmethod
import re

class FilterWidget(QWidget):
  def __init__(self, parent = None):
    QWidget.__init__(self, parent=parent)

    self.ui = filterActionWidget.Ui_Form()
    self.ui.setupUi(self)

  def getFilterWidget(self):
    self.filterButton = QToolButton()
    self.filterButton.setMenu(QMenu())
    self.filterButton.setPopupMode(QToolButton.MenuButtonPopup)
    self.qwa = QWidgetAction(None)
    self.qwa.setDefaultWidget(self)
    m = self.filterButton.menu()
    m.addAction(self.qwa)
    return self.filterButton

class FilterWidgetController:

  def __init__(self, view, iface):

    def setEnterpriseName(result):
      if result:
        self.enterprise.name = result[0][0]
        self.view.ui.leshoz_combobox_3.setCurrentText(self.enterprise.name)
        self.view.ui.leshoz_combobox_3.lineEdit().setCursorPosition(0)
        self.view.ui.lch_combobox_3.addItems(self.loadForestries(result[1:]))
      else:
        QMessageBox.information(None, 'Ошибка', "Лесхоз не найден. Проверьте файл конфигурации. Фильтр отключен")


    self.view = view
    self.iface = iface
    self.project = QgsProject.instance()
    
    self.fo = ForestObject()

    self.enterprise = ForestEnterprise()
    self.forestry = Forestry()    
    self.quarter = Quarter()
    self.stratum = Stratum()

    self.enterprise.nameLoaded.connect(setEnterpriseName)

    self.initWidgetData()

    self.view.ui.lch_combobox_3.currentTextChanged.connect(self.changeForestry)
    self.view.ui.kv_combobox_3.currentTextChanged.connect(self.changeQuarter)
    self.view.ui.vd_combobox_3.currentTextChanged.connect(self.changeStratum)

    self.view.ui.zoomTo_PushButton_3.clicked.connect(self.search)
    self.view.ui.clearFilter_pushButton_3.clicked.connect(self.clear)

  def loadForestries(self, result):
    forestries = []
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
    self.stratum.number = self.view.ui.vd_combobox_3.currentText()

  def search(self):
    if self.forestry.number == "" :
      QMessageBox.information(None, 'Ошибка', "Введите значение лесничества")
    elif self.forestry.number != "" and self.quarter.number == "":
      util.zoomToForestry(self.forestry.number, self.project, self.iface)
    elif self.quarter.number != "" and self.stratum.number == "":
      util.zoomToQuarter(self.forestry.number, self.quarter.number, self.project, self.iface)
    else:
      util.zoomToStratum(self.forestry.number, self.quarter.number, self.stratum.number, self.project, self.iface)

  def comboboxClear(self, *args):
    for arg in args:
      arg.clear()

  def clearComboboxIndex(self, *args):
    for arg in args:
      arg.setCurrentIndex(-1)

  def clear(self):
    self.clearComboboxIndex(self.view.ui.lch_combobox_3, self.view.ui.kv_combobox_3, self.view.ui.vd_combobox_3)
    self.comboboxClear(self.view.ui.kv_combobox_3, self.view.ui.vd_combobox_3)