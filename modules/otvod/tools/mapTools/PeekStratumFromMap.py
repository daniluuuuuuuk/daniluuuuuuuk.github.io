from qgis.gui import QgsMapToolEmitPoint, QgsMapTool
from PyQt5.QtCore import pyqtSignal, QObject
from qgis.core import QgsProject
from ...tools import GeoOperations
from qgis.core import QgsRectangle


class PeekStratumFromMap(QgsMapToolEmitPoint, QObject):

    signal = pyqtSignal(object)

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, e):
        layers = QgsProject.instance().mapLayersByName('Выдела')
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
        self.signal.emit(list(layer.getSelectedFeatures())[0])
        layer.removeSelection()

    def deactivate(self):
        pass
