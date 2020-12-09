from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QToolButton, QMenu, QWidgetAction, QWidget, QMessageBox
from .gui import filterActionWidget
from . import util
from . import ForestObject
from abc import ABCMeta, abstractmethod
import re

class ForestObjectObserver:
    @abstractmethod
    def forestObjectChanged(self):
        pass

class FilterWidget(QWidget):

  def __init__(self, iface, project, parent = None):
    QWidget.__init__(self, parent=parent)

    self.iface = iface
    self.project = project

    self.ui = filterActionWidget.Ui_Form()
    self.ui.setupUi(self)

    self.fo = ForestObject.ForestObject()

    self.ctrl = FilterWidgetController(self, self.fo, self.iface, self.project)

    self.initFilter()

  def getFilterWidget(self):
    self.filterButton = QToolButton()
    self.filterButton.setMenu(QMenu())
    self.filterButton.setPopupMode(QToolButton.MenuButtonPopup)
    self.projCombo = FilterWidget(self.iface, self.project)
    self.qwa = QWidgetAction(None)
    self.qwa.setDefaultWidget(self.projCombo)
    m = self.filterButton.menu()
    m.addAction(self.qwa)
    return self.filterButton

  def initFilter(self):
    self.fo.forestry = ForestObject.Forestry(self.fo.forestEnterprise.number)
    self.ui.leshoz_combobox_3.setCurrentText(self.fo.forestEnterprise.name)
    self.ui.lch_combobox_3.addItems(self.fo.forestry.getAllForestries())
    self.ui.lch_combobox_3.setCurrentIndex(-1)

class FilterWidgetController:
  def __init__(self, view, fo, iface, project):
    self.fo = fo
    self.view = view
    self.iface = iface
    self.project = project

    self.forestry = ForestObject.Forestry(self.fo.forestEnterprise.number)
    self.quarter = ForestObject.Quarter()
    self.stratum = ForestObject.Stratum()

    self.view.ui.lch_combobox_3.currentTextChanged.connect(self.changeForestry)
    self.view.ui.kv_combobox_3.currentTextChanged.connect(self.changeQuarter)
    self.view.ui.vd_combobox_3.currentTextChanged.connect(self.changeStratum)

    self.view.ui.zoomTo_PushButton_3.clicked.connect(self.search)
    self.view.ui.clearFilter_pushButton_3.clicked.connect(self.clear)

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
    print(self.forestry.number, 'forestry')
    print(self.quarter.number, 'quarter')
    print(self.stratum.number, 'stratum')
    if self.forestry.number == "" :
      QMessageBox.information(None, 'Ошибка', "Введите значение лесничества")
    elif self.forestry.number != "" and self.quarter.number == "":
      util.zoomToForestry(self.forestry.number, self.project, self.iface)
    elif self.quarter.number != "" and self.stratum.number == "":
      util.zoomToQuarter(self.forestry.number, self.quarter.number, self.project, self.iface)
    else:
      print('zoom to stratum')
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