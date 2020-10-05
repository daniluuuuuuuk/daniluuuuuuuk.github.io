from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsRectangle
from PyQt5.QtCore import pyqtSignal, QObject
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QMessageBox


class PeekStratumFromMap(QgsMapToolEmitPoint, QObject):

    signal = pyqtSignal(object)

    def __init__(self, canvas):
      self.canvas = canvas
      QgsMapToolEmitPoint.__init__(self, self.canvas)

    def canvasReleaseEvent(self, e):
      layers = QgsProject.instance().mapLayersByName('Лесосеки')
      layer = layers[0]
      x = self.toMapCoordinates(e.pos()).x()
      y = self.toMapCoordinates(e.pos()).y()
      radius = 5
      rect = QgsRectangle(x - radius,
                          y - radius,
                          x + radius,
                          y + radius)
      layer.selectByRect(rect, False)
      self.canvas.setCurrentLayer(layer)
      self.canvas.zoomToSelected()
      try:
        self.signal.emit(list(layer.getSelectedFeatures())[0])
      except Exception as e:
        QMessageBox.information(None, "Ошибка модуля Qgis", "Лесосека не определена. " + str(e))
        self.signal.emit(None)

      layer.removeSelection()