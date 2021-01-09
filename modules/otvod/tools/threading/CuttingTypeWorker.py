from qgis.core import *
from .CuttingTypeLoader import CuttingTypeLoader
from PyQt5 import QtCore, QtGui
import traceback
import time


class Worker(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.useType = None
        self.loader = CuttingTypeLoader('Load Cutting and Use Types')

    def run(self):
        ret = None
        try:
            self.loader.run(self.useType)
            self.loader.waitForFinished()
            ret = self.loader.cuttingTypes

        except Exception as e:
            raise e
            # self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)
