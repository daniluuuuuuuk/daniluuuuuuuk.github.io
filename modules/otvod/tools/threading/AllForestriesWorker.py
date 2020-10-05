# import some modules used in the example
import traceback
import time
from qgis.core import *
from .AllForestriesLoader import Load as LoadForestObject
from PyQt5 import QtCore, QtGui


class Worker(QtCore.QObject):
    '''Forest Object Worker'''

    def __init__(self):
        QtCore.QObject.__init__(self)
        # if isinstance(layer, QgsVectorLayer) is False:
        #     raise TypeError('Worker expected a QgsVectorLayer, got a {} instead'.format(type(layer)))
        self.killed = False

    def run(self):
        ret = None
        try:
            t1 = LoadForestObject("Opisanie")
            t1.run()
            # QgsApplication.taskManager().addTask(t1)
            t1.waitForFinished()
            ret = [t1.name, t1.lesnichestva, t1.number]

        except Exception as e:
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)
    # error = QtCore.pyqtSignal(Exception, basestring)
    # progress = QtCore.pyqtSignal(float)
