from . import config
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QMessageBox, QDialog
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsDataSourceUri, QgsTask, QgsMessageLog, Qgis
from qgis.PyQt.QtXml import QDomDocument


class QgsProjectInitializer:

    def __init__(self, iface):
        super().__init__()
        if self.clearCurrentProject() == False:
            return
        self.iface = iface
        self.setCrs()
        self.settings = None
        self.layerDbNames = {'hidroline': 'Гидрография линейная', 'hidropoly': 'Гидрография площадная', 'compartments': 'Кварталы',
                             'area': 'Лесосеки', 'settlements': 'Населенные пункты', 'area_line': 'Линия привязки', 'roads': 'Дороги', 'subcompartments': 'Выдела',
                             'forestry_borders': 'Границы лесничеств'}
        self.layerStyleNames = {'hidroline': 'Hidroline', 'hidropoly': 'Hidropoly', 'compartments': 'Kvartaly',
                             'area': 'Lesoseki', 'settlements': 'Nas punkt', 'area_line': 'Privyazka', 'roads': 'Dorogi', 'subcompartments': 'Vydela',
                             'forestry_borders': 'Granitsy lesnich'}
        try:
            self.cf = config.Configurer('dbconnection')
            self.settings = self.cf.readConfigs()
        except Exception as e:
            QMessageBox.information(
                None, 'Ошибка', "Проверьте подключение к базе данных" + e)
        if self.settings != None:
            self.loadLayersFromDb()

    def taskFinished(self):
        print("task finished")

    def clearCurrentProject(self):
        reply = QMessageBox.question(QDialog(), 'Инициализация проекта',
                                     'Слои текущего проекта будут удалены. Продолжить?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for lyr in QgsProject.instance().mapLayers().values():
                QgsProject.instance().removeMapLayers([lyr.id()])
        else:
            return False

    def setCrs(self):
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(32635))

    def loadLayersFromDb(self):
        self.loadTask = LoadLayersFromDbTask(self.settings, self.layerDbNames, self.layerStyleNames, self.iface)
        QgsApplication.taskManager().addTask(self.loadTask)


class LoadLayersFromDbTask(QgsTask):

    def __init__(self, settings, layerDbNames, layerStyleNames, iface):
        super().__init__("Layers from db", QgsTask.CanCancel)
        self.iface = iface
        self.settings = settings
        self.layerDbNames = layerDbNames
        self.layerStyleNames = layerStyleNames
        self.layers = []

    def run(self):
        QgsMessageLog.logMessage('Started task')
        user = self.settings.get('user')
        password = self.settings.get('password')
        host = self.settings.get('host')
        port = self.settings.get('port')
        database = self.settings.get('database')

        uri = QgsDataSourceUri()
        uri.setConnection(host, port, database, user, password)

        for tablename in self.layerDbNames:
            geom = 'geom'
            uri.setDataSource("public", tablename, geom)
            vlayer = QgsVectorLayer(
                uri.uri(False), self.layerDbNames[tablename], "postgres")
            self.layers.append(vlayer)
        return True

    def setLayerStyle(self, vlayer, tablename):
        styles = vlayer.listStylesInDatabase()
        styledoc = QDomDocument()
        styleIndex = styles[2].index(self.layerStyleNames[tablename])
        styleTuple = vlayer.getStyleFromDatabase(str(styles[1][styleIndex]))
        styleqml = styleTuple[0]
        styledoc.setContent(styleqml)
        vlayer.importNamedStyle(styledoc)
        self.iface.layerTreeView().refreshLayerSymbology(vlayer.id())

    def finished(self, result):
        if result:
            for layer in self.layers:
                QgsProject.instance().addMapLayer(layer)
                tableName = [k for k,v in self.layerDbNames.items() if v == layer.name()]
                self.setLayerStyle(layer, tableName[0])
        else:
            pass
