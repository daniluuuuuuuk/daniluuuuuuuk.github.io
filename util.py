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
  layer = QgsProject.instance().mapLayersByName("Кварталы")[0]
  iface.setActiveLayer(layer)
  expr = "\"num_lch\"='{}'".format(number)
  layer.selectByExpression(expr)
  iface.mapCanvas().zoomToSelected()

def zoomToQuarter(forestry, quarter, QgsProject, iface):
  clearAllSelections(iface)
  layer = QgsProject.instance().mapLayersByName("Кварталы")[0]
  iface.setActiveLayer(layer)
  expr = "\"num_lch\" = '{}' AND \"num_kv\" = '{}'".format(forestry, quarter)
  layer.selectByExpression(expr)
  iface.mapCanvas().zoomToSelected()

def zoomToStratum(forestry, quarter, stratum, QgsProject, iface):
  clearAllSelections(iface)
  layer = QgsProject.instance().mapLayersByName("Выдела")[0]
  iface.setActiveLayer(layer)
  expr = "\"num_lch\" = '{}' AND \"num_kv\" = '{}' AND \"num_vd\" = '{}'".format(forestry, quarter, stratum)
  layer.selectByExpression(expr)
  iface.mapCanvas().zoomToSelected()

class TableType(Enum):
    AZIMUTH = 0
    COORDINATE = 1
    RUMB = 2

class CoordType(Enum):
    DECIMAL = 0
    DMS = 1