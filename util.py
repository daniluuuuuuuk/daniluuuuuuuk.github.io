import os
from enum import Enum

def resolvePath(name, basepath=None):
  if not basepath:
    basepath = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(basepath, name)

def clearAllSelections(iface):
  mc = iface.mapCanvas()

  for layer in mc.layers():
      if layer.type() == layer.VectorLayer:
          layer.removeSelection()

  mc.refresh()

def setLayer(name, iface, QgsProject):
  layer = QgsProject.mapLayersByName(name)[0]
  iface.mapCanvas().setCurrentLayer(layer)
  iface.setActiveLayer(layer)

def zoomToForestry(number, QgsProject, iface):
  clearAllSelections(iface)
  setLayer('Кварталы', iface, QgsProject)
  currentLayer = iface.mapCanvas().currentLayer()
  expr = "\"num_lch\"='{}'".format(number)
  currentLayer.selectByExpression(expr)
  iface.mapCanvas().zoomToSelected()

def zoomToQuarter(forestry, quarter, QgsProject, iface):
  clearAllSelections(iface)
  setLayer('Кварталы', iface, QgsProject)
  currentLayer = iface.mapCanvas().currentLayer()
  expr = "\"num_lch\" = '{}' AND \"num_kv\" = '{}'".format(forestry, quarter)
  currentLayer.selectByExpression(expr)
  iface.mapCanvas().zoomToSelected()

def zoomToStratum(forestry, quarter, stratum, QgsProject, iface):
  clearAllSelections(iface)
  setLayer('Выдела', iface, QgsProject)
  currentLayer = iface.mapCanvas().currentLayer()
  fieldId = str((int(forestry) * 10000000) + (int(quarter) * 100) + int(stratum))
  expr = "\"fieldid\"='{}'".format(fieldId)
  currentLayer.selectByExpression(expr)
  iface.mapCanvas().zoomToSelected()

class TableType(Enum):
    AZIMUTH = 0
    COORDINATE = 1
    RUMB = 2

class CoordType(Enum):
    DECIMAL = 0
    DMS = 1