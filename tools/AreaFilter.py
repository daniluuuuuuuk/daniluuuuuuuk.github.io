from PyQt5.QtWidgets import QDockWidget
from qgis.PyQt.QtGui import QIcon
from ..gui.filterAreaWidget import Ui_Tools
from qgis.core import QgsProject, QgsFeatureRequest
from PyQt5 import QtCore
from .. import PostgisDB, util
from qgis.core import Qgis, QgsTask, QgsMessageLog
from qgis.utils import iface
from functools import partial


MESSAGE_CATEGORY = 'Поиск атрибутов'

class AreaFilterController:

    def __init__(self, widget):
        self.widget = widget
        self._ids = []
        self._currentId = 0
        self.widget.ui.filter_pushButton.clicked.connect(self.filterAreas)
        self.widget.ui.clear_pushButton.clicked.connect(self.clearWidgetData)
        self.layer = QgsProject.instance().mapLayersByName("Лесосеки")[0]
        # self.layer.removeSelection()
        self.setupButtonSignals()
        self.setupControlButtons(False)
        self.initValues()
        self.deselectAllLayers()

    @property
    def ids(self):
        return self._ids

    @ids.setter
    def ids(self, value):
        self._ids = value
        self.setupControlButtons(True) if len(value) > 1 else self.setupControlButtons(False)

    @property
    def currentId(self):
        return self._currentId

    @currentId.setter
    def currentId(self, value):
        self._currentId = value
        if value == len(self.ids):
            self.widget.ui.next_pushButton.setEnabled(False)
        elif value == 0:
            self.widget.ui.prev_pushButton.setEnabled(False)
        else:
            self.setupControlButtons(True)

    def deselectAllLayers(self):
        for a in iface.attributesToolBar().actions(): 
            if a.objectName() == 'mActionDeselectAll':
                a.trigger()

    def setupButtonSignals(self):
        self.widget.ui.prev_pushButton.clicked.connect(partial(self.zoomToIndex, -1))
        self.widget.ui.next_pushButton.clicked.connect(partial(self.zoomToIndex, 1))

        self.widget.ui.lesnich_comboBox.currentTextChanged.connect(self.filterAreas)
        self.widget.ui.num_kv_comboBox.currentTextChanged.connect(self.filterAreas)
        self.widget.ui.num_vd_comboBox.currentTextChanged.connect(self.filterAreas)
        self.widget.ui.num_comboBox.currentTextChanged.connect(self.filterAreas)
        self.widget.ui.useType_comboBox.currentTextChanged.connect(self.filterAreas)
        self.widget.ui.cuttingType_comboBox.currentTextChanged.connect(self.filterAreas)
        self.widget.ui.fio_comboBox.currentTextChanged.connect(self.filterAreas)

        self.widget.ui.info.textChanged.connect(self.filterAreas)
        self.widget.ui.date_lineEdit.textChanged.connect(self.filterAreas)
        self.widget.ui.area_min.textChanged.connect(self.filterAreas)
        self.widget.ui.area_max.textChanged.connect(self.filterAreas)

    def zoomToIndex(self, side):
        if not self.ids:
            return
        self.currentId += side
        # issue лишний клик предыдущий
        if self.currentId == 0:
            self.currentId = 0
            return
        iface.mapCanvas().setCurrentLayer(self.layer)
        self.layer.removeSelection()
        self.layer.selectByIds([self.ids[self.currentId - 1]])
        iface.mapCanvas().zoomToSelected()
        self.showAreaInfo()

    def showAreaInfo(self):
        feature = self.layer.selectedFeatures()[0]
        attributesAsText = self.prepareAttributes(feature)
        self.widget.ui.areaInfo_textEdit.setText(attributesAsText)

    def prepareAttributes(self, feature):
        attributesAsText = 'Лесничество: ' + str(feature['lesnich_text']) + '\n' \
        + 'Квартал: ' + str(feature['num_kv']) + '\n' \
        + 'Выдел(а): ' + str(feature['num_vds']) + '\n' \
        + 'Площадь: ' + str(feature['area']) + '\n' \
        + 'Номер: ' + str(feature['num']) + '\n' \
        + 'Вид пользования: ' + str(feature['useType']) + '\n' \
        + 'Вид рубки: ' + str(feature['cuttingTyp']) + '\n' \
        + 'Дата: ' + str(feature['date']) + '\n' \
        + 'Исполнитель: ' + str(feature['fio']) + '\n' \
        + 'Дополнительно: ' + str(feature['info'])
        return attributesAsText

    def setupControlButtons(self, status):
        self.widget.ui.prev_pushButton.setEnabled(status)
        self.widget.ui.next_pushButton.setEnabled(status)
        self.widget.ui.export_pushButton.setEnabled(status)
    
    def initValues(self):

        def workerFinished(result):
            self.worker.deleteLater()
            self.thread.quit()
            self.thread.wait()
            self.thread.deleteLater()
            print(result)
            self.appendWidget(result)

        self.thread = QtCore.QThread(iface.mainWindow())
        self.worker = Worker(self.layer)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(workerFinished)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def appendWidget(self, data):   
        self.widget.ui.lesnich_comboBox.addItems(str(i) for i in data['lesnich_text'])
        self.widget.ui.num_kv_comboBox.addItems(str(i) for i in data['num_kv'])
        self.widget.ui.num_vd_comboBox.addItems(str(i) for i in data['num_vds'])
        self.widget.ui.num_comboBox.addItems(str(i) for i in data['num'])
        self.widget.ui.useType_comboBox.addItems(str(i) for i in data['usetype'])
        self.widget.ui.cuttingType_comboBox.addItems(str(i) for i in data['cuttingtyp'])
        self.widget.ui.fio_comboBox.addItems(str(i) for i in data['fio'])
        self.negateComboboxes()

    def negateComboboxes(self):
        self.widget.ui.lesnich_comboBox.setCurrentIndex(-1)
        self.widget.ui.num_kv_comboBox.setCurrentIndex(-1)
        self.widget.ui.num_vd_comboBox.setCurrentIndex(-1)
        self.widget.ui.num_comboBox.setCurrentIndex(-1)
        self.widget.ui.useType_comboBox.setCurrentIndex(-1)
        self.widget.ui.cuttingType_comboBox.setCurrentIndex(-1)
        self.widget.ui.fio_comboBox.setCurrentIndex(-1)

    def filterAreas(self):
        self.ids = []
        self.currentId = 0                
        iface.mapCanvas().setCurrentLayer(self.layer)
        self.widget.ui.areaInfo_textEdit.clear()
        self.widget.ui.areaCounter_lineEdit.clear()
        self.layer.removeSelection()
        expression = self.constructExpression()
        request = QgsFeatureRequest().setFilterExpression(expression)
        features = self.layer.getFeatures(request)
        self.ids = [s.id() for s in features]
        self.layer.selectByIds(self.ids)
        iface.mapCanvas().zoomToSelected()
        self.widget.ui.areaCounter_lineEdit.setText(str(len(self.ids)))
        if len(self.ids) == 1:
            self.showAreaInfo()

    def clearWidgetData(self):
        self.negateComboboxes()
        self.clearLines()
        self.layer.removeSelection()
        self.ids = []
        self.currentId = 0

    def clearLines(self):
        self.widget.ui.areaCounter_lineEdit.clear()
        self.widget.ui.areaInfo_textEdit.clear()
        self.widget.ui.area_min.clear()
        self.widget.ui.area_max.clear()
        self.widget.ui.date_lineEdit.clear()
        self.widget.ui.info.clear()
        
    def constructExpression(self):
        expression = ''
        if self.widget.ui.lesnich_comboBox.currentText():
            expression += " \"lesnich_text\" = '{}' ".format(self.widget.ui.lesnich_comboBox.currentText())
        if self.widget.ui.num_kv_comboBox.currentText():
            query = " \"num_kv\" = '{}' ".format(self.widget.ui.num_kv_comboBox.currentText())
            expression += ' and ' + query if expression else expression + query
        if self.widget.ui.num_vd_comboBox.currentText():
            text = self.widget.ui.num_vd_comboBox.currentText()
            query = " \"num_vds\" = '%{}%' or \"num_vds\" = '{}' ".format(text, text)
            expression += ' and ' + query if expression else expression + query
        if self.widget.ui.num_comboBox.currentText():
            query = " \"num\" = '{}' ".format(self.widget.ui.num_comboBox.currentText())
            expression += ' and ' + query if expression else expression + query
        if self.widget.ui.useType_comboBox.currentText():
            query = " \"usetype\" = '{}' ".format(self.widget.ui.useType_comboBox.currentText())
            expression += ' and ' + query if expression else expression + query
        if self.widget.ui.cuttingType_comboBox.currentText():
            query = " \"cuttingtyp\" = '{}' ".format(self.widget.ui.cuttingType_comboBox.currentText())
            expression += ' and ' + query if expression else expression + query
        if self.widget.ui.fio_comboBox.currentText():
            query = " \"fio\" = '{}' ".format(self.widget.ui.fio_comboBox.currentText())
            expression += ' and ' + query if expression else expression + query            
        if self.widget.ui.area_min.text():
            query = " \"area\" >= '{}' ".format(self.widget.ui.area_min.text())
            expression += ' and ' + query if expression else expression + query
        if self.widget.ui.area_max.text():
            query = " \"area\" <= '{}' ".format(self.widget.ui.area_max.text())
            expression += ' and ' + query if expression else expression + query
        if self.widget.ui.date_lineEdit.text():
            query = " \"date\" like '%{}%' ".format(self.widget.ui.date_lineEdit.text())
            expression += ' and ' + query if expression else expression + query
        if self.widget.ui.info.text():
            query = " \"info\" like '%{}%' ".format(self.widget.ui.info.text())
            expression += ' and ' + query if expression else expression + query
        return expression

class AreaFilterDockWidget(QDockWidget):
    def __init__(self):
        QDockWidget.__init__(self)
        self.ui = Ui_Tools()
        self.ui.setupUi(self)
        self.ui.tabWidget.setTabIcon(0, QIcon(util.resolvePath("res\\icon-.png")))

class Worker(QtCore.QObject):

    def __init__(self, layer):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.layer = layer
        self.searcher = UniqueValuesTask('Find unique attributes')

    def run(self):
        ret = None
        try:
            self.searcher.run(self.layer)
            self.searcher.waitForFinished()
            ret = self.searcher.result

        except Exception as e:
            raise e
            # self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)

class UniqueValuesTask(QgsTask):

    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)
        self.result = {}
        self.exception = None

    def findUniqueAttributes(self, layer):
        attributesUnique = ['lesnich_text', 'num_kv', 'num_vds',
        'num', 'usetype', 'cuttingtyp', 'fio']
        for attr in attributesUnique:
            idx = layer.fields().indexOf(attr)
            values = layer.uniqueValues(idx)
            if '' in values:
                values.remove('')
            self.result[attr] = values

    def run(self, layer):
        QgsMessageLog.logMessage('\nStarted task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.findUniqueAttributes(layer)
        return True

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage(
                'Task "{name}" completed\n'
                .format(
                    name=self.description()),
                MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without exception '
                    '(probably the task was manually canceled by the '
                    'user)'.format(
                        name=self.description()),
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.description(), exception=self.exception),
                    MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was cancelled'.format(name=self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()