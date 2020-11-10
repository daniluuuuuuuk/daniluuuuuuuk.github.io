from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtCore import QDateTime, QDate, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5 import QtCore
from .lesosekaInfo import Ui_Dialog as uiLesosekaInfo
from ..tools.threading.ForestObjectWorker import Worker as ForestObjWorker
from ..tools.threading.ForestObjectLoader import ForestObjectLoader
from functools import partial


class LesosekaInfo(QDialog):

    def __init__(self, editMode):
        super(LesosekaInfo, self).__init__()
        self.ui = uiLesosekaInfo()
        self.ui.setupUi(self)
        # self.setupValidation()
        self.forestObjectCode = None
        
        if not editMode:
            self.ui.gplho.currentTextChanged.connect(self.gplhoChanged)
            self.ui.leshos.currentTextChanged.connect(self.leshozChanged)
            self.ui.lesnich.currentTextChanged.connect(self.lesnichChanged)

    # def setupValidation(self):
    #     reg_ex = QRegExp("[a-z-A-Z_]+")
    #     num_kv_validator = QRegExpValidator(reg_ex, self.ui.num_kv)
    #     self.ui.num_kv.setValidator(num_kv_validator)

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

            self.ui.leshos.addItems(result[1].values())

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
            print("prishel result")

            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()

            self.comboboxClear(self.ui.lesnich)
            self.clearComboboxIndex(self.ui.lesnich)

            self.ui.lesnich.addItems(result[2].values())

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

        thread = QtCore.QThread()
        worker = ForestObjWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        thread.started.connect(worker.run)
        thread.start()

        self.ui.date.setDateTime(QDateTime.currentDateTime())

    def populateValues(self, attributes):
        self.ui.gplho.addItem(str(attributes.get('gplho_text')))
        self.ui.leshos.addItem(str(attributes.get('leshos_text')))
        self.ui.lesnich.addItem(str(attributes.get('lesnich_text')))
        self.ui.num_kv.setText(str(attributes.get('num_kv')))
        self.ui.num_vds.setText(str(attributes.get('num_vds')))
        self.ui.num.setText(str(attributes.get('num')))
        self.ui.fio.setText(str(attributes.get('fio')))
        self.ui.date.setDate(QDate.fromString(attributes.get('date'), 'dd.MM.yyyy'))
        self.ui.info.setText(str(attributes.get('info')))

        self.ui.gplho.setEnabled(False)
        self.ui.leshos.setEnabled(False)
        self.ui.lesnich.setEnabled(False)