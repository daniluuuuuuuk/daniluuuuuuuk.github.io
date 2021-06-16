import os
from .. import PostgisDB
from qgis.core import Qgis, QgsTask, QgsMessageLog, QgsProject
from PyQt5 import QtCore, QtWidgets
from . import config
from ..gui import areaControllerDialog
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMessageBox
from qgis.PyQt.QtCore import QDate
from ..modules.otvod.tools.Serializer import DbSerializer
from ..modules.otvod.tools.threading.CuttingTypeWorker import (
    Worker as CuttingTypeWorker,
)
from ..modules.otvod.tools.threading.CuttingTypeLoader import CuttingTypeLoader
from .AreaDataContainer import (
    AreaDataPrintContainer,
    AreaCoordinatesTypeDialog,
)
from ..modules.trees_accounting.src.trees_accounting import TaMainWindow
from qgis.utils import iface
from datetime import date
from .CuttingAreaExport import CuttingAreaExport
from ..modules.trees_accounting.src.services.waiting_spinner_widget import (
    QtWaitingSpinner,
)


MESSAGE_CATEGORY = "Удаление лесосеки"
AREA_POINTS_TABLE_NAME = "area_points"
AREA_DATA_TABLE_NAME = "area_data"
AREA_TABLE_NAME = "area"
AREA_LINE_TABLE_NAME = "area_line"
TREES_TRF_HEIGHT_TABLE_NAME = "trees_trf_height"
TREES_NOT_CUTTING_TABLE_NAME = "trees_not_cutting"
TREES_TABLE_NAME = "trees"


class AreaController(QtCore.QObject):
    def __init__(self, feature, parent=None):
        super(AreaController, self).__init__(parent)
        self.feature = feature
        self._editMode = False
        self._changesSaved = False
        self.sd = SettingsWindow()
        self.sd.setModal(False)
        self.ui = self.sd.ui
        self.defaultAreaTypeValues = []
        self.defaultAreaTypes = []
        self.cuttingAreaTypes = []
        self.currentCuttingAreaTypes = []
        self.setupValues()
        self.setupButtons()
        self.window = self.sd.show()
        self.sd.ui.export_pushButton.clicked.connect(self.exportArea)
        self.spinner = QtWaitingSpinner(
            self.sd, True, True, QtCore.Qt.ApplicationModal
        )

    @property
    def editMode(self):
        return self._editMode

    @editMode.setter
    def editMode(self, value):
        self._editMode = value
        self.modeChanged()

    def modeChanged(self):
        self.changeFormEnableState(self.editMode)
        self.ui.buttonBox.button(QDialogButtonBox.Apply).setEnabled(
            self.editMode
        )
        self.ui.delete_pushButton.setEnabled(not self.editMode)
        self.ui.edit_pushButton.setChecked(self.editMode)

    def setupButtons(self):
        self.ui.buttonBox.button(QDialogButtonBox.Apply).setEnabled(False)
        self.ui.edit_pushButton.clicked.connect(self.changeEditMode)
        self.ui.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(
            self.saveChanges
        )
        self.ui.count_pushButton.clicked.connect(self.showCountWindow)
        self.ui.delete_pushButton.clicked.connect(self.deleteArea)
        self.ui.buttonBox.button(QDialogButtonBox.Close).setVisible(False)
        self.ui.useType_comboBox.currentTextChanged.connect(
            self.useTypeChanged
        )
        self.ui.print_pushButton.clicked.connect(self.printArea)

    def printArea(self):
        def areaPointsLoaded(data, points):
            dc = AreaDataPrintContainer(data, points, self.feature, layoutData)
            dc.buildPointsLayer()
            dc.buildAreaLayer()
            dc.prepareTableForLayout()
            dc.printLayout()

        def dialogData(dialog):
            layoutData = {
                "type": dialog.coordTypeGroup.checkedButton().text(),
                "format": dialog.coordFormatGroup.checkedButton().text(),
                "scale": dialog.scaleCombobox.currentText(),
            }
            return layoutData

        iface.mapCanvas().zoomToFeatureExtent(
            self.feature.geometry().boundingBox()
        )
        self.dialog = AreaCoordinatesTypeDialog()
        if self.dialog.exec() == QDialog.Accepted:
            layoutData = dialogData(self.dialog)
            uid = self.feature["uid"]
            serializer = DbSerializer(uid)
            serializer.signal.connect(areaPointsLoaded)
            serializer.loadFromDb()
        return

    def showCountWindow(self):
        uid = self.feature["uid"]
        self.rst = TaMainWindow(uid)
        self.rst.show()

    def saveChanges(self):
        layer = QgsProject.instance().mapLayersByName("Лесосеки")[0]
        try:
            layer.startEditing()
            self.feature["num_kv"] = self.ui.num_kv_lineEdit.text()
            self.feature["area"] = float(str(self.ui.area_lineEdit.text()))
            self.feature["num"] = self.ui.num_lineEdit.text()
            self.feature["fio"] = self.ui.fio_lineEdit.text()
            self.feature["date"] = self.ui.dateEdit.text()
            self.feature["info"] = self.ui.info_textEdit.toPlainText()
            self.feature["num_vds"] = self.ui.num_vd_lineEdit.text()
            self.feature["leshos_text"] = self.ui.leshos_comboBox.currentText()
            self.feature[
                "lesnich_text"
            ] = self.ui.lesnich_comboBox.currentText()
            self.feature[
                "vedomstvo_text"
            ] = self.ui.gplho_comboBox.currentText()
            self.feature["useType"] = self.ui.useType_comboBox.currentText()
            self.feature[
                "cuttingTyp"
            ] = self.ui.cuttingType_comboBox.currentText()
            self.currentCuttingAreaTypes = [
                self.ui.useType_comboBox.currentText(),
                self.ui.cuttingType_comboBox.currentText(),
            ]
            layer.updateFeature(self.feature)
            layer.commitChanges()
            self.cuttingAreaTypes = []
        except Exception as e:
            QMessageBox.information(None, "Ошибка", str(e))
        self.editMode = False

    def changeEditMode(self):
        self.currentCuttingAreaTypes = [
            self.ui.useType_comboBox.currentText(),
            self.ui.cuttingType_comboBox.currentText(),
        ]
        self.editMode = not self.editMode
        if self.editMode:
            self.setUseTypes()
        else:
            self.setupValues()

    def setUseTypes(self):
        useTypes = [
            "Рубки главного пользования",
            "Рубки промежуточного пользования",
            "Прочие рубки",
        ]
        self.ui.useType_comboBox.clear()
        self.ui.useType_comboBox.addItems(useTypes)
        index = self.ui.useType_comboBox.findText(
            self.currentCuttingAreaTypes[0]
        )
        if index >= 0:
            self.ui.useType_comboBox.setCurrentIndex(index)

    def comboboxClear(self, *args):
        for arg in args:
            arg.clear()

    def clearComboboxIndex(self, *args):
        for arg in args:
            arg.setCurrentIndex(-1)

    def useTypeChanged(self):
        if self.ui.useType_comboBox.currentText() == "":
            return

        def workerFinished(result):
            self.worker.deleteLater()
            self.thread.quit()
            self.thread.wait()
            self.thread.deleteLater()
            self.comboboxClear(self.ui.cuttingType_comboBox)
            self.clearComboboxIndex(self.ui.cuttingType_comboBox)
            self.ui.cuttingType_comboBox.addItems(result)
            index = self.ui.cuttingType_comboBox.findText(
                self.currentCuttingAreaTypes[1]
            )
            if index >= 0:
                self.ui.cuttingType_comboBox.setCurrentIndex(index)
            if not self.defaultAreaTypes:
                self.defaultAreaTypes = result

        self.thread = QtCore.QThread(iface.mainWindow())
        self.worker = CuttingTypeWorker()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(workerFinished)
        self.worker.useType = self.ui.useType_comboBox.currentIndex() + 1
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def setupValues(self):
        def setupComboboxes():
            self.ui.leshos_comboBox.addItem(self.feature["leshos_text"])
            self.ui.gplho_comboBox.addItem(self.feature["vedomstvo_text"])
            self.ui.lesnich_comboBox.addItem(self.feature["lesnich_text"])
            self.ui.useType_comboBox.clear()
            self.ui.cuttingType_comboBox.clear()
            self.ui.useType_comboBox.addItem(self.feature["usetype"])
            self.ui.cuttingType_comboBox.addItem(self.feature["cuttingtyp"])
            self.ui.gplho_comboBox.setEnabled(False)
            self.ui.leshos_comboBox.setEnabled(False)
            self.ui.lesnich_comboBox.setEnabled(False)

        def setupLineEdits():
            self.ui.num_kv_lineEdit.setText(str(self.feature["num_kv"]))
            self.ui.num_vd_lineEdit.setText(str(self.feature["num_vds"]))
            self.ui.area_lineEdit.setText(str(self.feature["area"]))
            self.ui.num_lineEdit.setText(str(self.feature["num"]))
            self.ui.fio_lineEdit.setText(str(self.feature["fio"]))
            self.ui.info_textEdit.setText(str(self.feature["info"]))
            self.ui.dateEdit.setDate(
                QDate.fromString(str(self.feature["date"]), "dd.MM.yyyy")
            )

        self.ui.useType_comboBox.blockSignals(True)
        self.ui.cuttingType_comboBox.blockSignals(True)
        setupComboboxes()
        setupLineEdits()
        self.changeFormEnableState(False)
        self.ui.useType_comboBox.blockSignals(False)
        self.ui.cuttingType_comboBox.blockSignals(False)

    def changeFormEnableState(self, val):
        self.ui.num_kv_lineEdit.setEnabled(val)
        self.ui.num_vd_lineEdit.setEnabled(val)
        self.ui.area_lineEdit.setEnabled(val)
        self.ui.num_lineEdit.setEnabled(val)
        self.ui.fio_lineEdit.setEnabled(val)
        self.ui.info_textEdit.setEnabled(val)
        self.ui.dateEdit.setEnabled(val)

        self.ui.useType_comboBox.setEnabled(val)
        self.ui.cuttingType_comboBox.setEnabled(val)

    def deleteArea(self):
        def workerFinished(result):
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()
            if result:
                QMessageBox.information(
                    None,
                    "Модуль отвода",
                    "Лесосека и ее данные были удалены из базы данных",
                )
            iface.mapCanvas().refreshAllLayers()
            self.sd.close()

        reply = QMessageBox.question(
            QDialog(),
            "Удаление лесосеки",
            "Лесосека и все ее данные будут удалены. Продолжить?",
            QMessageBox.Yes,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            thread = QtCore.QThread()
            worker = Worker(self.feature["uid"])
            worker.moveToThread(thread)
            worker.finished.connect(workerFinished)
            thread.started.connect(worker.run)
            thread.start()
        else:
            return False

    def exportArea(self):
        export_file = QtWidgets.QFileDialog.getSaveFileName(
            caption="Сохранение файла",
            directory=os.path.expanduser("~")
            + "/Documents/Экспорт_лесосек_"
            + date.today().strftime("%Y-%m-%d")
            + ".json",
            filter="JSON (*.json)",
        )

        if export_file[0]:
            self.cutting_area_export = CuttingAreaExport(
                uuid_list=[
                    self.feature["uid"],
                ],
                path_to_file=export_file[0],
            )
            self.cutting_area_export.started.connect(
                lambda: self.spinner.start()
            )
            self.cutting_area_export.finished.connect(
                lambda: self.spinner.stop()
            )
            self.cutting_area_export.start()
            self.cutting_area_export.signal_message_result.connect(
                lambda mes: QtWidgets.QMessageBox.information(
                    None, "", str(mes)
                ),
                QtCore.Qt.QueuedConnection,
            )


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.ui = areaControllerDialog.Ui_Dialog()
        self.ui.setupUi(self)

    def closeEvent(self, event):

        layerNamesToDelete = [
            "Лесосека",
            "Точка привязки",
            "Привязка",
            "Пикеты",
        ]

        for name in layerNamesToDelete:
            layer = QgsProject.instance().mapLayersByName(name)
            if layer:
                QgsProject.instance().removeMapLayers([layer[0].id()])

        iface.mapCanvas().refresh()
        self.deleteLater()


class Worker(QtCore.QObject):
    def __init__(self, uid):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.uid = uid
        self.remover = RemoveAreaTask("Remove Area from Database")

    def run(self):
        ret = None
        try:
            self.remover.run(self.uid)
            self.remover.waitForFinished()
            ret = True

        except Exception as e:
            raise e
            # self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)


class RemoveAreaTask(QgsTask):
    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.exception = None

    def deleteArea(self, uid):
        postgisConnection = PostgisDB.PostGisDB()
        cursor = postgisConnection.connection.cursor()
        cursor.execute(
            "DELETE FROM {table} WHERE area_uid='{area_uid}'".format(
                table=AREA_DATA_TABLE_NAME, area_uid=uid
            )
        )
        postgisConnection.connection.commit()
        cursor.execute(
            "DELETE FROM {table} WHERE area_uid='{area_uid}'".format(
                table=AREA_POINTS_TABLE_NAME, area_uid=uid
            )
        )
        postgisConnection.connection.commit()
        cursor.execute(
            "DELETE FROM {table} WHERE uid='{area_uid}'".format(
                table=AREA_TABLE_NAME, area_uid=uid
            )
        )
        postgisConnection.connection.commit()
        cursor.execute(
            "DELETE FROM {table} WHERE uid='{area_uid}'".format(
                table=AREA_LINE_TABLE_NAME, area_uid=uid
            )
        )
        postgisConnection.connection.commit()
        cursor.execute(
            "DELETE FROM {table} WHERE area_uuid='{area_uuid}'".format(
                table=TREES_TRF_HEIGHT_TABLE_NAME, area_uuid=uid
            )
        )
        postgisConnection.connection.commit()
        cursor.execute(
            "DELETE FROM {table} WHERE area_uuid='{area_uuid}'".format(
                table=TREES_NOT_CUTTING_TABLE_NAME, area_uuid=uid
            )
        )
        postgisConnection.connection.commit()
        cursor.execute(
            "DELETE FROM {table} WHERE area_uuid='{area_uuid}'".format(
                table=TREES_TABLE_NAME, area_uuid=uid
            )
        )
        postgisConnection.connection.commit()

    def run(self, uid):
        QgsMessageLog.logMessage(
            '\nStarted task "{}"'.format(self.description()),
            MESSAGE_CATEGORY,
            Qgis.Info,
        )
        self.deleteArea(uid)
        return True

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage(
                'Task "{name}" completed\n'.format(name=self.description()),
                MESSAGE_CATEGORY,
                Qgis.Success,
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without exception '
                    "(probably the task was manually canceled by the "
                    "user)".format(name=self.description()),
                    MESSAGE_CATEGORY,
                    Qgis.Warning,
                )
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.description(), exception=self.exception
                    ),
                    MESSAGE_CATEGORY,
                    Qgis.Critical,
                )
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was cancelled'.format(name=self.description()),
            MESSAGE_CATEGORY,
            Qgis.Info,
        )
        super().cancel()
