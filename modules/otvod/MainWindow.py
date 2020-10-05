from qgis.PyQt.QtWidgets import QMainWindow
from .gui.otvodMainWindow import Ui_MainWindow as otvodMainWindow
from qgis.core import QgsProject
from qgis.utils import iface

class MainWindow(QMainWindow, otvodMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        otvodMainWindow.__init__(self)
        self.setupUi(self)

    def closeEvent(self, event):
        try:
            layer = QgsProject.instance().mapLayersByName("Точка привязки")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Точка привязки")
        try:
            layer = QgsProject.instance().mapLayersByName("Лесосека временный слой")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Точка привязки")
        try:
            layer = QgsProject.instance().mapLayersByName("Опорные точки")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Опорные точки")
        try:
            layer = QgsProject.instance().mapLayersByName("Выдел лесосеки")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Выдел лесосеки")
        try:
            layer = QgsProject.instance().mapLayersByName("Пикеты")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Пикеты")
        try:
            layer = QgsProject.instance().mapLayersByName("Привязка временный слой")[0]
            QgsProject.instance().removeMapLayers([layer.id()])
        except Exception as e:
            print(str(e) + "Ошибка при удалении слоя Привязка временный слой")
        iface.mapCanvas().refresh()
        self.deleteLater()
