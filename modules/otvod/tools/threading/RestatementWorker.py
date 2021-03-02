from qgis.core import *
from .RestatementLoader import RestatementLoader
from PyQt5 import QtCore, QtGui
import traceback
import time


class Worker(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.guid = None
        self.loader = RestatementLoader('Load Restatement Data')

    def run(self):
        ret = None
        try:
            self.loader.run(self.guid)
            self.loader.waitForFinished()
            ret = self.loader.restatementData

        except Exception as e:
            raise e
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)
