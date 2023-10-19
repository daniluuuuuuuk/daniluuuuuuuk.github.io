"""Классы для формирования тематических карт
Для формирования тематических карта со слоем выделов по уникальному полю identity 
добавляются в проект и связываются таблицы БД: subcompartments_taxation и subcompartments_taxation_m10
После связывания к слою выделов применяется соответствующий стиль из таблицы public.layer_styles
Доступны стили (тематические карты) раскрашенные по: породе и группе возраста, полноте, бонитету,
ТУМ, запасу, проектируемым хозмероприятиям. 
Слой лесосек раскрашивается по типу пользования.
"""

from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsProject, QgsVectorLayerJoinInfo
from qgis.core import QgsTask
from qgis.PyQt.QtWidgets import QMessageBox, QDialog, QComboBox, QVBoxLayout, QGroupBox
from qgis.PyQt.QtWidgets import QPushButton, QDialogButtonBox
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface
from . import config
from ..modules.trees_accounting.src.services.waiting_spinner_widget import (
    QtWaitingSpinner,
)

class ThematicController:

    def __init__(self, dialogWindow, thematic):
        self.thematic = thematic
        self.dialogWindow = dialogWindow

        self.spinner = QtWaitingSpinner(
            self.dialogWindow, True, True, QtCore.Qt.ApplicationModal
        )
        self.spinner.start()

        self.tableNames = ['subcompartment_characteristics', 'taxation_characteristics']

        self.layer = self.getStyledLayer()

        self.cf = config.Configurer('dbconnection')
        
        self.settings = self.cf.readConfigs()

        self.removeTaxTable()

        if self.thematic != '':
            self.loadTaxTables()
        else:
            self.setLayerStyle()
            self.spinner.stop()

    def loadTaxTables(self):

        def workerFinished(result):
            for layer in result:
                QgsProject.instance().addMapLayer(layer)

            self.continueAfterTablesLoaded(result)
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()

        thread = QtCore.QThread()
        worker = TaxTablesWorker(self.tableNames, self.settings, self.layer, self.thematic)
        worker.moveToThread(thread) 
        worker.finished.connect(workerFinished)
        thread.started.connect(worker.run)
        thread.finished.connect(lambda: self.spinner.stop())
        thread.start()

    def continueAfterTablesLoaded(self, layers):
        self.setLayerStyle()

    def getStyledLayer(self):
        if 'Лесосеки' in self.thematic:
            return QgsProject.instance().mapLayersByName("Лесосеки")[0]
        else:
            return QgsProject.instance().mapLayersByName("Выдела")[0]

    def getStyleName(self, thematic):
        stylesDbMapping = {
            '': 'Vydela',
            "Породы": "Species_map",
            "Бонитет": "Bonitet_map",
            "ТУМ": "Forest_growing_cond_types_map",
            "Запас": "Layer_stocks",
            "Полнота": "Fullness_map",
            "Проектируемые хозмероприятия": "Economic_events_map",
            "Лесосеки: виды пользования": "UseType_map",
            "Категории защитности": "Protection_categories_map",
        }
        return stylesDbMapping.get(thematic)

    def setLayerStyle(self):
        def setStyle(layer=None, style=None):
            if layer:
                layer = QgsProject.instance().mapLayersByName(layer)[0]
            else:
                layer = self.layer

            styles = layer.listStylesInDatabase()
            styledoc = QDomDocument()
            styleIndex = styles[2].index(style)
            styleTuple = layer.getStyleFromDatabase(str(styles[1][styleIndex]))
            styleqml = styleTuple[0]
            styledoc.setContent(styleqml)
            layer.importNamedStyle(styledoc)
            iface.layerTreeView().refreshLayerSymbology(layer.id())
            layer.triggerRepaint()
            self.expandLayer()

        setStyle(style=self.getStyleName(self.thematic))
        if self.thematic == '':
            setStyle('Лесосеки', 'Lesoseki')

    def expandLayer(self):
        root = QgsProject.instance().layerTreeRoot()
        node = root.findLayer(self.layer.id())
        node.setExpanded(True)

    def removeTaxTable(self):
        for table in self.tableNames:
            qinst = QgsProject.instance()
            layers = qinst.mapLayersByName(table)
            if layers:
                qinst.removeMapLayer(layers[0].id())


class TaxTablesWorker(QtCore.QObject):

    finished = QtCore.pyqtSignal(list)

    def __init__(self, names, settings, layer, thematic):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.names = names
        self.settings = settings
        self.layer = layer
        self.thematic = thematic
        self.loader = TaxTableLoader(self.names, self.settings, self.layer, self.thematic)

    def run(self):
        ret = None
        try:
            self.loader.run()
            self.loader.waitForFinished()
            ret = self.loader.tables
        except Exception as e:
            raise e

        self.finished.emit(ret)

    def kill(self):
        self.killed = True


class TaxTableLoader(QgsTask):

    def __init__(self, tableNames, settings, layer, thematic):
        super().__init__('Load tax tables', QgsTask.CanCancel)
        self.tableNames = tableNames
        self.settings = settings
        self.tables = []
        self.layer = layer
        self.thematic = thematic

    def run(self):
        self.loadTables()
        self.joinTables()

    def joinTables(self):

        def join(table):
            # print(f'type: {table}')
            # print(f'type: {table.name()}')
            if table.name() == 'taxation_characteristics':
                joinFieldName = 'subcompartment_characteristics_id'
            else:
                joinFieldName = 'id'
            targetFieldName = 'id'
            joinObject = QgsVectorLayerJoinInfo()
            joinObject.setJoinFieldName(joinFieldName)
            joinObject.setTargetFieldName(targetFieldName)
            joinObject.setJoinLayerId(table.id())
            joinObject.setUsingMemoryCache(True)
            joinObject.setJoinLayer(table)
            joinObject.joinFieldNamesSubset()
            self.layer.addJoin(joinObject)

        for table in self.tables:
            join(table)

    def loadTables(self):
        for table in self.tableNames:
            uri = QgsDataSourceUri()
            uri.setConnection(
                self.settings.get('host'),
                self.settings.get('port'),
                self.settings.get('database'),
                self.settings.get('user'),
                self.settings.get('password'),
            )
            uri.setDataSource('public', table, None)
            layer = QgsVectorLayer(uri.uri(False), table, "postgres")
            self.tables.append(layer)


class ChooseThematicMapDialog(QDialog):

    def __init__(self, parent=None):
        super(ChooseThematicMapDialog, self).__init__(parent)
        self.setWindowTitle("Выбор тематической карты")
        self.thematicCombobox = None
        self.setupUi()
        self.adjustSize()

    def setupUi(self):
        self.resize(311, 509)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Reset|
            QtWidgets.QDialogButtonBox.Cancel|
            QtWidgets.QDialogButtonBox.Ok
            )
        self.buttonBox.setObjectName("buttonBox")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.createThematicMapWidget())
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.buttonBox.clicked.connect(self.btnClicked)

    def btnClicked(self, btn):
        if self.buttonBox.buttonRole(btn) == 7:
            self.thematicCombobox.setCurrentIndex(-1)

    def createThematicMapWidget(self):
        groupBox = QGroupBox('Критерий окраски')
        vbox = QVBoxLayout()
        combo = QComboBox()
        combo.addItems([
            '', 'Породы', 'Бонитет','ТУМ',
            'Запас', 'Полнота', 'Проектируемые хозмероприятия',
            'Лесосеки: виды пользования', 'Категории защитности'
            ])
        combo.setCurrentIndex(0)
        vbox.addWidget(combo)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        self.thematicCombobox = combo
        return groupBox

    def closeEvent(self, event):
        tableNames = ['subcompartment_characteristics', 'taxation_characteristics']

        for name in tableNames:
            layer = QgsProject.instance().mapLayersByName(name)
            if layer:
                QgsProject.instance().removeMapLayers([layer[0].id()])

        self.deleteLater()