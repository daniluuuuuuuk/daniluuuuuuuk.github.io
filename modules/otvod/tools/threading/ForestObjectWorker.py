from qgis.core import *
from .ForestObjectLoader import ForestObjectLoader
from PyQt5 import QtCore, QtGui
import traceback
import time


class Worker(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.gplho = None
        self.leshoz = None
        self.loader = ForestObjectLoader('Load Forest object')

    def run(self):
        ret = None
        try:
            self.loader.run(self.gplho, self.leshoz)
            self.loader.waitForFinished()
            ret = [self.loader.allGplho, self.loader.allLeshozy, self.loader.allLesnichestva, self.loader.allRestatements, self.loader.lhTypesAndNames]

        except Exception as e:
            raise e
            # self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)
