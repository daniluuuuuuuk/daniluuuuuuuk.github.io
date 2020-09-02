# import some modules used in the example
from qgis.core import *
from .ForestObjectLoader import Load as LoadForestObject
from PyQt5 import QtCore, QtGui
import traceback
import time

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
            # calculate the total area of all of the features in a layer
            # total_area = 0.0
            # features = self.layer.getFeatures()
            # feature_count = self.layer.featureCount()
            # progress_count = 0
            # step = feature_count // 1000
            # for feature in features:
            #     if self.killed is True:
            #         # kill request received, exit loop early
            #         break
            #     geom = feature.geometry()
            #     total_area += geom.area()
            #     time.sleep(0.1) # simulate a more time consuming task
            #     # increment progress
            #     progress_count += 1
            #     if step == 0 or progress_count % step == 0:
            #         self.progress.emit(progress_count / float(feature_count))
            # if self.killed is False:
            #     self.progress.emit(100)
            #     ret = (self.layer, total_area,)
        except Exception as e:
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)
        
    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)
    # error = QtCore.pyqtSignal(Exception, basestring)
    # progress = QtCore.pyqtSignal(float)