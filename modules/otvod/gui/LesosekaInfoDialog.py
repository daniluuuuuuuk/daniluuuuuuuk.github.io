from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtCore import QDateTime, QDate, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5 import QtCore
from .lesosekaInfo import Ui_Dialog as uiLesosekaInfo
from ..tools.threading.ForestObjectWorker import Worker as ForestObjWorker
from ..tools.threading.ForestObjectLoader import ForestObjectLoader
from ..tools.threading.RestatementWorker import Worker as RestatementWorker
from ..tools.threading.RestatementLoader import RestatementLoader
from ..tools.threading.CuttingTypeWorker import Worker as CuttingTypeWorker
from ..tools.threading.CuttingTypeLoader import CuttingTypeLoader
from ....tools import config

class LesosekaInfo(QDialog):

    def __init__(self, editMode):
        super(LesosekaInfo, self).__init__()
        self.ui = uiLesosekaInfo()
        self.ui.setupUi(self)
        self.forestObjectCode = None
        self.guidItems = None

        self.gplho, self.leshoz, self.lesnich = self.getEnterpriseConfig()

        if not editMode:
            self.ui.gplho.currentTextChanged.connect(self.gplhoChanged)
            self.ui.leshos.currentTextChanged.connect(self.leshozChanged)
            self.ui.lesnich.currentTextChanged.connect(self.lesnichChanged)
            self.ui.restatement_comboBox.currentTextChanged.connect(self.restatementChanged)

        self.setUseTypes()

    def setUseTypes(self):
        self.ui.useType.currentTextChanged.connect(self.useTypeChanged)
        useTypes = ['Рубки главного пользования', 'Рубки промежуточного пользования', 'Прочие рубки']
        self.ui.useType.addItems(useTypes)

    def useTypeChanged(self):
        if self.ui.useType.currentText() == '':
            return

        def workerFinished(result):
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()
            self.comboboxClear(self.ui.cuttingType)
            self.clearComboboxIndex(self.ui.cuttingType)
            self.ui.cuttingType.addItems(result)

        thread = QtCore.QThread()
        worker = CuttingTypeWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        worker.useType = self.ui.useType.currentIndex() + 1
        thread.started.connect(worker.run)
        thread.start()

    def getEnterpriseConfig(self):
        cf = config.Configurer('enterprise')
        settings = cf.readConfigs()
        return [settings.get('gplho', ''),
            settings.get('leshoz', ''),
            settings.get('lesnich', '')]

    def restatementChanged(self):

        if self.ui.restatement_comboBox.currentText() == "":
            return

        def workerFinished(result):

            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()
            populateData(result)

        def populateData(data):
            self.ui.gplho.blockSignals(True)
            self.ui.leshos.blockSignals(True)
            self.ui.lesnich.blockSignals(True)

            self.comboboxClear(self.ui.gplho, self.ui.leshos, self.ui.lesnich)
            self.clearComboboxIndex(self.ui.gplho, self.ui.leshos, self.ui.lesnich)

            self.ui.gplho.addItem(data.get('ГПЛХО')[0])
            self.ui.leshos.addItem(data.get('Лесхоз')[0])
            self.ui.lesnich.addItem(data.get('Лесничество')[0])
            self.ui.num_kv.setText(str(data.get('Квартал')))
            self.ui.num_vds.setText(str(data.get('Выдел')))
            self.ui.num.setText(str(data.get('Номер')))
            self.guid = data.get('uid')
            self.ui.date.setDate(QDate.fromString(data.get('Дата'), 'dd.MM.yyyy'))

            self.forestObjectCode = data.get('Код')

            self.ui.gplho.blockSignals(False)
            self.ui.leshos.blockSignals(False)
            self.ui.lesnich.blockSignals(False)
            

        thread = QtCore.QThread()
        worker = RestatementWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        worker.guid = self.guidItems[self.ui.restatement_comboBox.currentText()]
        thread.started.connect(worker.run)
        thread.start()

    def getLesnichNumber(self):
        if self.forestObjectCode is None:
            return 0
        else:
            return int(str(self.forestObjectCode)[-2:])

    def getLeshozNumber(self):
        if self.forestObjectCode is None:
            return 0
        else:
            return int(str(self.forestObjectCode)[5:8])

    def comboboxClear(self, *args):
        for arg in args:
            arg.clear()

    def clearComboboxIndex(self, *args):
        for arg in args:
            arg.setCurrentIndex(-1)

    def gplhoChanged(self):

        if self.ui.gplho.currentText() == "":
            return

        def workerFinished(result):

            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()

            self.comboboxClear(self.ui.leshos, self.ui.lesnich)
            self.clearComboboxIndex(self.ui.leshos, self.ui.lesnich)
            self.ui.leshos.addItem("")
            self.ui.leshos.addItems(result[1].values())

            if self.leshoz:
                index = self.ui.leshos.findText(self.leshoz)
                if index >= 0:
                    self.ui.leshos.setCurrentIndex(index)

        thread = QtCore.QThread()
        worker = ForestObjWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        worker.gplho = self.ui.gplho.currentText()
        worker.leshoz = None
        thread.started.connect(worker.run)
        thread.start()

    def leshozChanged(self):

        if self.ui.leshos.currentText() == "":
            return        

        def workerFinished(result):
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()

            self.comboboxClear(self.ui.lesnich)
            self.clearComboboxIndex(self.ui.lesnich)

            self.ui.lesnich.addItems(result[2].values())

            if self.lesnich:
                index = self.ui.lesnich.findText(self.lesnich)
                if index >= 0:
                    self.ui.lesnich.setCurrentIndex(index)

        thread = QtCore.QThread()
        worker = ForestObjWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        worker.gplho = self.ui.gplho.currentText()
        worker.leshoz = self.ui.leshos.currentText()
        thread.started.connect(worker.run)
        thread.start()

    def lesnichChanged(self):

        if self.ui.lesnich.currentText() == "":
            return

        def getKey(dict, val): 
            for key, value in dict.items(): 
                if val == value: 
                    return key 

        def workerFinished(result):

            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()

            self.forestObjectCode = getKey(result[2], self.ui.lesnich.currentText())

        thread = QtCore.QThread()
        worker = ForestObjWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        worker.gplho = self.ui.gplho.currentText()
        worker.leshoz = self.ui.leshos.currentText()
        thread.started.connect(worker.run)
        thread.start()

    def setUpValues(self):

        def workerFinished(result):

            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()

            self.ui.gplho.addItem("")
            self.ui.gplho.addItems(result[0].values())

            if self.gplho:
                index = self.ui.gplho.findText(self.gplho)
                if index >= 0:
                    self.ui.gplho.setCurrentIndex(index)

            self.ui.restatement_comboBox.addItem("")
            items = []
            self.guidItems = {}
            for rst in result[3]:
                items.append(str(rst[1]) + ' кв. ' + str(rst[2]) + ' выд. ' + str(rst[3]) + ' № ' + str(rst[4]))
                self.guidItems[items[-1]] = rst[0]
            self.ui.restatement_comboBox.addItems(items)

        thread = QtCore.QThread()
        worker = ForestObjWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        thread.started.connect(worker.run)
        thread.start()

        self.ui.date.setDateTime(QDateTime.currentDateTime())

    def populateValues(self, attributes):
        self.ui.gplho.addItem(str(attributes.get('vedomstvo_text')))
        self.ui.leshos.addItem(str(attributes.get('leshos_text')))
        self.ui.lesnich.addItem(str(attributes.get('lesnich_text')))
        self.ui.num_kv.setText(str(attributes.get('num_kv')))
        self.ui.num_vds.setText(str(attributes.get('num_vds')))
        self.ui.num.setText(str(attributes.get('num')))
        self.ui.fio.setText(str(attributes.get('fio')))
        self.ui.date.setDate(QDate.fromString(attributes.get('date'), 'dd.MM.yyyy'))
        self.ui.info.setText(str(attributes.get('info')))

        self.ui.useType.addItem(str(attributes.get('useType')))
        self.ui.cuttingType.addItem(str(attributes.get('cuttingType')))

        self.ui.gplho.setEnabled(False)
        self.ui.leshos.setEnabled(False)
        self.ui.lesnich.setEnabled(False)
        self.ui.useType.setEnabled(False)
        self.ui.cuttingType.setEnabled(False)