from qgis.PyQt.QtWidgets import QTableWidget, QComboBox, QMessageBox, QTableWidgetItem
from ...tools import module_errors as er
# from .Converter import Converter
from .tools.CoordinateConverter import CoordinateConverter
from .tools.CoordinateFormatConverter import CoordinateFormatConverter
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
from enum import Enum
from PyQt5 import QtCore
from .tools import GeoOperations
from PyQt5.QtCore import pyqtSignal, QSize
from qgis.core import QgsPointXY
import os
import decimal
import time
from functools import partial
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer

# Только в целях подсказки, нигде не используется:


class TableType(Enum):
    COORDINATE = 0
    AZIMUTH = 1
    RUMB = 2


class CoordType(Enum):
    DECIMAL = 0
    DMS = 1


class DataTable(QTableWidget):

    signal = pyqtSignal(object)
    # rows_changed_signal = pyqtSignal(object)

    def __init__(self, datatable, tableType, coordType, inclination, bindingPoint):
        super().__init__(datatable)
        self.coordType = coordType
        self.tabletype = tableType
        self.bindingPoint = bindingPoint
        self.setGeometry(QtCore.QRect(0, 0, 401, 341))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.anchorLineRows = []
        self.lesosekaRows = []

        self.pointsDict = {}

        self.builder = None

        self.cellChanged.connect(self.cellChangedHandler)
        # self.cellChanged.connect(self.refreshData)

        self.magneticInclination = inclination

        self.rerenderEnabled = True

    def setRerender(self, bl):
        self.rerenderEnabled = bl

    def getPoints(self):
        return self.pointsDict

    def initColumns(self):
        self.columnNames = self.getColumnNames()
        self.setColumnCount(len(self.columnNames))
        self.setHorizontalHeaderLabels(self.columnNames)
        header = self.horizontalHeader()
        for x in range(0, len(self.columnNames) - 1):
            header.setSectionResizeMode(x, QtWidgets.QHeaderView.Stretch)

    def setParams(self, tableType, coordType, inclination, bindingPoint):
        # print("table type in setParams: ", tableType)
        # print("SetParams:", tableType, coordType, inclination, bindingPoint)
        self.tabletype = tableType
        self.coordType = coordType
        self.magneticInclination = inclination
        self.bindingPoint = bindingPoint
        if self.rerenderEnabled:
            self.pointsDict.clear()
        self.initColumns()

    def getParams(self):
        return [self.tabletype, self.coordType, self.magneticInclination, self.bindingPoint]

    def setTableType(self, tableType):
        self.tabletype = tableType

    def getColumnNames(self):
        if (self.tabletype == 0 and self.coordType == 0):
            rs = ["№", "X, °", "Y, °", "GPS", "Тип"]
            self.builder = GeoOperations.parseXYRow
        elif (self.tabletype == 0 and self.coordType == 1):
            rs = ["№", "X, °", "X, ′", "X, ″", "Y, °", "Y, ′", "Y, ″", "Тип"]
            self.builder = GeoOperations.parseDMSXYRow
        elif (self.tabletype == 1 and self.coordType == 0):
            rs = ["№", "Угол, °", "Длина линии, м", "Тип"]
            self.builder = GeoOperations.parseAzimuthDDRow
        elif (self.tabletype == 1 and self.coordType == 1):
            rs = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Тип"]
            self.builder = GeoOperations.parseAzimuthDMSRow
        elif (self.tabletype == 2 and self.coordType == 0):
            rs = ["№", "Угол, °", "Длина линии, м", "Румб", "Тип"]
            self.builder = GeoOperations.parseRumbDDRow
        elif (self.tabletype == 2 and self.coordType == 1):
            rs = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Румб", "Тип"]
            self.builder = GeoOperations.parseRumbDMSRow
        elif (self.tabletype == 3 and self.coordType == 0):
            rs = ["№", "Угол, °", "Длина линии, м", "Тип"]
            self.builder = GeoOperations.parseAzimuthDDRow
        elif (self.tabletype == 3 and self.coordType == 1):
            rs = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Тип"]
            self.builder = GeoOperations.parseAzimuthDMSRow
        elif (self.tabletype == 4 and self.coordType == 0):
            rs = ["№", "Угол, °", "Длина линии, м", "Тип"]
            self.builder = GeoOperations.parseAzimuthDDRow
        elif (self.tabletype == 4 and self.coordType == 1):
            rs = ["№", "X, °", "X, ′", "X, ″", "Длина, м", "Тип"]
            self.builder = GeoOperations.parseAzimuthDMSRow
        else:
            return ["Неправильная конфигурация столбцов"]
        return rs

    def getRowCount(self):
        return self.rowCount()

    def getColCount(self):
        return self.columnCount()

    def setup_cell_widgets(self, index):
        lineTypeCombobox = QtWidgets.QComboBox()
        lineTypeCombobox.addItem(
            QIcon(self.resolve("icons\\line_icon.png")), "Привязка")
        lineTypeCombobox.addItem(
            QIcon(self.resolve("icons\\lesoseka_icon.png")), "Лесосека")
        lineTypeCombobox.currentIndexChanged.connect(
            self.lineTypeComboboxChanged)
        self.setCellWidget(index, len(self.columnNames) - 1, lineTypeCombobox)
        if self.tabletype == 2 and self.coordType == 0:
            rumbCombobox = QtWidgets.QComboBox()
            rumbCombobox.insertItems(0, ["СВ", "ЮВ", "ЮЗ", "СЗ"])
            rumbCombobox.currentIndexChanged.connect(self.rumbComboboxChanged)
            self.setCellWidget(index, 3, rumbCombobox)
        if self.tabletype == 2 and self.coordType == 1:
            rumbCombobox = QtWidgets.QComboBox()
            rumbCombobox.insertItems(0, ["СВ", "ЮВ", "ЮЗ", "СЗ"])
            rumbCombobox.currentIndexChanged.connect(self.rumbComboboxChanged)
            self.setCellWidget(index, 5, rumbCombobox)
        if self.tabletype == 0 and self.coordType == 0:
            gpsButton = QtWidgets.QPushButton()
            # gpsButton.setText("GPS")
            gpsButton.setIcon(
                QIcon(self.resolve('icons\\pick_from_gps_icon.png')))
            gpsButton.setMaximumSize(QSize(70, 50))
            self.setCellWidget(index, 3, gpsButton)
            gpsButton.clicked.connect(partial(self.setCoordinateRow, index))

    def setCoordinateRow(self, index):
        cell = QTableWidgetItem()
        self.setItem(index, 1, cell)
        cell2 = QTableWidgetItem()
        self.setItem(index, 2, cell2)
        gpsCoords = GeoOperations.getCoordFromGPS()
        if gpsCoords:
            self.item(index, 2).setText(str(round(gpsCoords[0], 10)))
            self.item(index, 1).setText(str(round(gpsCoords[1], 10)))

    def update_row_numbers(self):
        for row in range(0, self.getRowCount()):
            cell = QTableWidgetItem()
            self.setItem(row, 0, cell)
            self.item(row, 0).setText(str(str(row) + "-" + str(row + 1)))
            # print("CELL5", self.pointsDict)
        # self.viewport().update()

    def resolve(self, name, basepath=None):
        if not basepath:
            basepath = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(basepath, name)

    def addRow(self):
        self.insertRow(self.getRowCount())
        self.setup_cell_widgets(self.getRowCount() - 1)
        self.update_row_numbers()

    def pop_rows(self, index):
        for row in range(index, self.rowCount()):
            self.pointsDict.pop(row)
        self.pointsDict.pop(index)
        cell = QTableWidgetItem()
        self.setItem(index, 1, cell)
        cell2 = QTableWidgetItem()
        self.setItem(index, 2, cell2)
        self.item(index, 1).setText("0")
        self.item(index, 2).setText("1")
        self.pointsDict[index] = self.pointsDict[index-1]
        self.refreshData()
        self.signal.emit(self.pointsDict)

    def add_line_node_row(self):
        index = 0
        for row in range(0, self.rowCount()):
            cellWidget = self.cellWidget(row, self.columnCount() - 1)
            if cellWidget.currentText() == "Привязка":
                index = row + 1
        self.insertRow(index)
        self.setup_cell_widgets(index)
        self.update_row_numbers()
        # print("index", index, row)
        self.pop_rows(index)

    def add_lesoseka_node_row(self):
        index = 0
        for row in range(0, self.rowCount()):
            cellWidget = self.cellWidget(row, self.columnCount() - 1)
            if cellWidget.currentText() == "Лесосека":
                index = row + 1
        if index == 0:
            index = self.getRowCount()
        self.insertRow(index)
        self.setup_cell_widgets(index)
        cellWidget = self.cellWidget(index, self.columnCount() - 1)
        cellWidget.setCurrentIndex(1)
        self.update_row_numbers()
        self.refreshData()

    def deleteRow(self):
        try:
            self.pointsDict.pop(self.getRowCount() - 1)
        except Exception as e:
            print(e)
        row = self.currentRow()
        self.removeRow(row)
        # self.removeRow(self.getRowCount() - 1)
        self.signal.emit(self.pointsDict)
        self.update_row_numbers()

    def deleteRows(self):
        self.setRowCount(0)
        if self.rerenderEnabled:
            self.pointsDict.clear()
        self.signal.emit(self.pointsDict)

    def setBindingPointXY(self, bpXY):
        self.bindingPoint = bpXY

    def getBindingPointXY(self):
        return self.bindingPoint

    def setMagneticInclination(self, magneticInclination):
        self.magneticInclination = magneticInclination

    def getMagneticInclination(self):
        return self.magneticInclination

    def getJSONRows(self):
        rowsList = [{"Table": {"table_type": self.tabletype,
                               "coord_type": self.coordType,
                               "magnetic_inclination": self.magneticInclination,
                               "BindingPointX": self.bindingPoint.x(),
                               "BindingPointY": self.bindingPoint.y()}}
                    ]
        for row in range(0, self.rowCount()):
            try:
                rowsDict = {}
                for column in range(0, self.columnCount()):
                    if self.horizontalHeaderItem(column).text() == "Румб":
                        comboboxCellWidget = self.cellWidget(row, column)
                        rowsDict.update({self.getColumnNames()[column]: str(
                            comboboxCellWidget.currentText())})
                    elif self.horizontalHeaderItem(column).text() == "Тип":
                        comboboxCellWidget = self.cellWidget(row, column)
                        rowsDict.update({self.getColumnNames()[column]: str(
                            comboboxCellWidget.currentText())})
                    elif self.horizontalHeaderItem(column).text() == "GPS":
                        pass
                    else:
                        rowsDict.update(
                            {self.getColumnNames()[column]: self.item(row, column).text()})
            except Exception as e:
                QMessageBox.information(
                    None,
                    er.MODULE_ERROR,
                    "Ошибка. Отсутствуют значения в" + ": строка " +
                    str(row + 1) + ", колонка " +
                    str(column + 1) + ". Сохранен пустой файл"
                )
                rowsList.clear()
                return rowsList
            rowsList.append({row: rowsDict})
        return rowsList

    def importJSONData(self, data):
        self.data = data

    def getAngleBuilder(self, row):
        if self.tabletype == 3:
            if self.coordType == 0:
                if (self.cellWidget(row, 3).currentText() == "Привязка" or row == 0):
                    return GeoOperations.parseAzimuthDDRow
                else:
                    if self.cellWidget(row - 1, 3).currentText() == "Привязка":
                        return GeoOperations.parseAzimuthDDRow
                    else:
                        return GeoOperations.parseLeftAngleDDRow

            if self.coordType == 1:
                if (self.cellWidget(row, 5).currentText() == "Привязка" or row == 0):
                    return GeoOperations.parseAzimuthDMSRow
                else:
                    if self.cellWidget(row - 1, 5).currentText() == "Привязка":
                        return GeoOperations.parseAzimuthDMSRow
                    else:
                        return GeoOperations.parseLeftAngleDMSRow

        elif self.tabletype == 4:
            if self.coordType == 0:
                if (self.cellWidget(row, 3).currentText() == "Привязка" or row == 0):
                    return GeoOperations.parseAzimuthDDRow
                else:
                    if self.cellWidget(row - 1, 3).currentText() == "Привязка":
                        return GeoOperations.parseAzimuthDDRow
                    else:
                        return GeoOperations.parseRightAngleDDRow

            if self.coordType == 1:
                if (self.cellWidget(row, 5).currentText() == "Привязка" or row == 0):
                    return GeoOperations.parseAzimuthDMSRow
                else:
                    if self.cellWidget(row - 1, 5).currentText() == "Привязка":
                        return GeoOperations.parseAzimuthDMSRow
                    else:
                        return GeoOperations.parseRightAngleDMSRow

    def cellChangedHandler(self, row, column):
        if self.item(row, column) and self.item(row, column).text().find(",") != -1:
            currentText = self.item(row, column).text()
            self.item(row, column).setText(currentText.replace(',','.'))
        
        if self.ensureRowCellsNotEmpty(row) and self.rerenderEnabled:

            angle = False

            if self.tabletype == 0:
                point = self.builder(self, row)

            elif self.tabletype == 3 or self.tabletype == 4:
                self.builder = self.getAngleBuilder(row)
                if (self.builder.__name__ == "parseLeftAngleDMSRow" or \
                        self.builder.__name__ == "parseLeftAngleDDRow" or \
                        self.builder.__name__ == "parseRightAngleDMSRow" or \
                        self.builder.__name__ == "parseRightAngleDDRow"):
                    angle = True
                if not self.pointsDict:
                    point = self.builder(
                        self.bindingPoint, self, row, self.magneticInclination)
                else:
                    if angle:
                        if row == 1:
                            azimuth = GeoOperations.calculateAzimuth(
                                self.bindingPoint, self.pointsDict[row-1][0])
                            point = self.builder(
                                self.pointsDict[row-1][0], azimuth, self, row, self.magneticInclination)
                        elif row > 1:
                            azimuth = GeoOperations.calculateAzimuth(
                                self.pointsDict[row-2][0], self.pointsDict[row-1][0])
                            point = self.builder(
                                self.pointsDict[row-1][0], azimuth, self, row, self.magneticInclination)
                    else:
                        if row == 0:
                            point = self.builder(
                                self.bindingPoint, self, row, self.magneticInclination)
                        else:
                            point = self.builder(
                                self.pointsDict[row - 1][0],
                                self, row, self.magneticInclination
                            )
            else:
                if not self.pointsDict:
                    point = self.builder(
                        self.bindingPoint, self, row, self.magneticInclination)
                else:
                    if row == 0:
                        point = self.builder(
                            self.bindingPoint, self, row, self.magneticInclination)
                    else:
                        point = self.builder(
                            self.pointsDict[row - 1][0],
                            self, row, self.magneticInclination
                        )

            # если редактируется имеющаяся точка - удалить ее
            # if row in self.pointsDict:
            #     del self.pointsDict[row]

            self.pointsDict[row] = [point, self.getPointType(row)]
            
            self.signal.emit(self.pointsDict)
            print(self.pointsDict)
            return row

    def getPointType(self, row):
        for x in range(0, self.getColCount()):
            headertext = self.horizontalHeaderItem(x).text()
            if headertext == 'Тип':
                if self.cellWidget(row, x):
                    cellWidget = self.cellWidget(row, x)
                    pointType = cellWidget.currentText()
                    return pointType

    def rumbComboboxChanged(self, item):
        sender = self.sender()
        postitionOfWidget = sender.pos()
        index = self.indexAt(postitionOfWidget)
        row = index.row()
        col = index.column()
        # self.cellChangedHandler(row, col)
        self.refreshData()

    def lineTypeComboboxChanged(self, item):
        sender = self.sender()
        postitionOfWidget = sender.pos()
        index = self.indexAt(postitionOfWidget)
        row = index.row()
        col = index.column()
        # self.cellChangedHandler(row, col)
        self.refreshData()

    def ensureTableCellsNotEmpty(self):

        self.clearSelection()

        def flicker(row, col):
            self.item(row, col).setBackground(QColor(255,255,255))

        for row in range(0, self.getRowCount()):
            for col in range(0, self.getColCount()):
                headertext = self.horizontalHeaderItem(col).text()
                if headertext == "GPS" or headertext == "Тип" or headertext == "Румб":
                    break
                if not self.item(row, col):
                    self.setItem(row, col, QTableWidgetItem())
                    self.item(row, col).setBackground(QColor(255,0,0,50))
                    QTimer().singleShot(100, partial(flicker, row, col))
                    return False
                if self.item(row, col).text() == "":
                    self.item(row, col).setBackground(QColor(255,0,0,50)) 
                    QTimer().singleShot(100, partial(flicker, row, col))
                    return False
        return True

    def ensureRowCellsNotEmpty(self, row):
        for col in range(0, self.getColCount()):
            headertext = self.horizontalHeaderItem(col).text()
            if headertext == "GPS" or headertext == "Тип" or headertext == "Румб":
                break
            if not self.item(row, col):
                return False
            if self.item(row, col).text() == "":
                return False
        return True

    def refreshData(self):
        for row in range(0, self.rowCount()):
            self.cellChangedHandler(row, 0)

    def delete(self):
        self.close()

    def set_line_type_widget(self, row, column, index):
        lineTypeCombobox = QtWidgets.QComboBox()
        lineTypeCombobox.addItem(
            QIcon(self.resolve("icons\\line_icon.png")), "Привязка")
        lineTypeCombobox.addItem(
            QIcon(self.resolve("icons\\lesoseka_icon.png")), "Лесосека")
        lineTypeCombobox.currentIndexChanged.connect(
            self.lineTypeComboboxChanged)
        self.setCellWidget(row, column, lineTypeCombobox)
        lineTypeCombobox.setCurrentIndex(index)

    def set_rumb_combobox(self, row, column, index):
        rumbCombobox = QtWidgets.QComboBox()
        rumbCombobox.insertItems(0, ["СВ", "ЮВ", "ЮЗ", "СЗ"])
        rumbCombobox.currentIndexChanged.connect(self.rumbComboboxChanged)
        self.setCellWidget(row, column, rumbCombobox)
        rumbCombobox.setCurrentIndex(index)

    def set_gps_button(self, row, column):
        gpsButton = QtWidgets.QPushButton()
        gpsButton.setIcon(QIcon(self.resolve('icons\\pick_from_gps_icon.png')))
        gpsButton.setMaximumSize(QSize(70, 50))
        self.setCellWidget(row, column, gpsButton)

    def move_row_up(self):
        row = self.currentRow()
        column = self.currentColumn()
        if row > 0:
            self.insertRow(row-1)
            for i in range(self.columnCount()):
                if i == self.columnCount() - 1:
                    cellWidget = self.cellWidget(row + 1, i)
                    index = cellWidget.currentIndex()
                    self.set_line_type_widget(row-1, i, index)
                else:
                    if self.tabletype == 0 and self.coordType == 0 and i == 3:
                        self.set_gps_button(row-1, i)
                    elif self.tabletype == 2 and self.coordType == 0 and i == 3 or self.tabletype == 2 and self.coordType == 1 and i == 5:
                        cellWidget = self.cellWidget(row + 1, i)
                        index = cellWidget.currentIndex()
                        self.set_rumb_combobox(row-1, i, index)
                    else:
                        self.setItem(row-1, i, self.takeItem(row + 1, i))
                        self.setCurrentCell(row-1, column)
            self.removeRow(row+1)
            self.update_row_numbers()
            if self.rowCount() < len(self.pointsDict):
                self.pointsDict.pop(self.getRowCount())
            self.refreshData()
            print(self.pointsDict)
            # self.refreshData()

    def move_row_down(self):
        row = self.currentRow()
        column = self.currentColumn()
        if row < self.rowCount()-1 and row > -1:
            self.insertRow(row+2)
            for i in range(self.columnCount()):
                if i == self.columnCount() - 1:
                    cellWidget = self.cellWidget(row, i)
                    index = cellWidget.currentIndex()
                    self.set_line_type_widget(row + 2, i, index)
                else:
                    if self.tabletype == 0 and self.coordType == 0 and i == 3:
                        self.set_gps_button(row+2, i)
                    elif self.tabletype == 2 and self.coordType == 0 and i == 3 or self.tabletype == 2 and self.coordType == 1 and i == 5:
                        cellWidget = self.cellWidget(row, i)
                        index = cellWidget.currentIndex()
                        self.set_rumb_combobox(row + 2, i, index)
                    self.setItem(row + 2, i, self.takeItem(row, i))
                    self.setCurrentCell(row + 2, column)
            self.removeRow(row)
            self.update_row_numbers()
            if self.rowCount() < len(self.pointsDict):
                self.pointsDict.pop(self.getRowCount())
            self.refreshData()
            # print(self.pointsDict)

            # self.refreshData()
    def getTableAsList(self):
        tableAsList = []
        for row in range(0, self.rowCount()):
            rowList = []
            for column in range(0, self.columnCount()):
                if self.horizontalHeaderItem(column).text() == "Румб":
                    comboboxCellWidget = self.cellWidget(row, column)
                    rowList.append(str(comboboxCellWidget.currentText()))
                elif self.horizontalHeaderItem(column).text() == "Тип":
                    comboboxCellWidget = self.cellWidget(row, column)
                    rowList.append(str(comboboxCellWidget.currentText()))
                elif self.horizontalHeaderItem(column).text() == "GPS":
                    pass
                else:
                    rowList.append(self.item(row, column).text())
            tableAsList.append(rowList)
        return tableAsList


class DataTableWrapper():

    def __init__(self, datatable, coordType, tableType, inclination, bindingPoint):
        self.tableModel = DataTable(
            datatable, coordType, tableType, inclination, bindingPoint)
        self.tableModel.initColumns()
        self.i = 0

    def changeTable(self, newDatatable):
        self.datatable = newDatatable

    def setParams(self, tableType, coordType, inclination, bindingPoint):
        self.tableModel.setParams(
            tableType, coordType, inclination, bindingPoint)

    def addRow(self):
        self.tableModel.addRow()

    def deleteRow(self):
        self.tableModel.deleteRow()

    def deleteRows(self):
        self.tableModel.deleteRows()

    def getMagneticInclination(self):
        return self.tableModel.getMagneticInclination()

    def getColumnNames(self):
        return self.tableModel.getColumnNames()

    def getColumnCount(self):
        return self.tableModel.getColCount()

    def getRowsCount(self):
        return self.tableModel.getRowCount()

    def setBindingPointXY(self, x, y):
        self.tableModel.bindingPointXY.append(x, y)

    def getBindingPointXY(self):
        return self.tableModel.getBindingPointXY()

    def getRowsCollection(self):
        self.i = self.i + 1

    def move_row_up(self):
        self.tableModel.move_row_up()

    def move_row_down(self):
        self.tableModel.move_row_down()

    def add_line_node(self):
        self.tableModel.add_line_node_row()

    def add_lesoseka_node(self):
        self.tableModel.add_lesoseka_node_row()

    def getJSONRows(self):
        self.tableModel.getJSONRows()

    def encodeJSON(self, table):
        if isinstance(table, DataTableWrapper):
            return self.tableModel.getJSONRows()
        else:
            type_name = table.__class__.__name__
            raise TypeError(
                f"Object of type '{type_name}' is not JSON serializable")

    def loadData(self, data):
        self.tableModel.importJSONData(data)

    def makeTableFromCuttingArea(self, bindingPoint, cuttingArea):
        currentTableType = self.tableModel.tabletype
        currentCoordType = self.tableModel.coordType
        self.tableModel.setParams(
            1, 0, self.getMagneticInclination(), self.getBindingPointXY())
        azimuthTableList = []
        lastAnchorLinePoint = None
        for key in cuttingArea:
            if cuttingArea[key][1] == "Привязка":
                lastAnchorLinePoint = key
            if key == 0:
                azimuth = GeoOperations.calculateAzimuth(bindingPoint, cuttingArea[key][0])
                distance = GeoOperations.calculateDistance(bindingPoint, cuttingArea[key][0])
            else:
                azimuth = GeoOperations.calculateAzimuth(cuttingArea[key-1][0], cuttingArea[key][0])
                distance = GeoOperations.calculateDistance(cuttingArea[key-1][0], cuttingArea[key][0])
            azimuthTableList.append([str(key) + "-" + str(key + 1), str(azimuth), str(distance), cuttingArea[key][1]])
        if lastAnchorLinePoint is None:
            azimuth = GeoOperations.calculateAzimuth(cuttingArea[key][0], bindingPoint)
            distance = GeoOperations.calculateDistance(cuttingArea[key][0], bindingPoint)
            if azimuth <= 0.1 or distance <= 0.1:
                row = azimuthTableList[-1]
                row[0] = row[0].split('-')[0] + '-' + '0'
                del azimuthTableList[-1]
                azimuthTableList.append(row)
                return
            azimuthTableList.append([str(key + 1) + "-" + "0", str(azimuth), str(distance), cuttingArea[key][1]])
        else:
            azimuth = GeoOperations.calculateAzimuth(cuttingArea[key][0], cuttingArea[lastAnchorLinePoint][0])
            distance = GeoOperations.calculateDistance(cuttingArea[key][0], cuttingArea[lastAnchorLinePoint][0])
            if azimuth <= 0.1 or distance <= 0.1:
                row = azimuthTableList[-1]
                row[0] = row[0].split('-')[0] + '-' + str(lastAnchorLinePoint)
                del azimuthTableList[-1]
                azimuthTableList.append(row)
                return
            azimuthTableList.append([str(key + 1) + "-" + str(lastAnchorLinePoint + 1), str(azimuth), str(distance), cuttingArea[key][1]])

        self.deleteRows()
        self.populateTable(azimuthTableList)
        # print(azimuthTableList)

    def convertCoordFormat(self, coordType):
        self.tableModel.setRerender(False)
        currentTableType = self.tableModel.tabletype
        params = self.tableModel.getParams()
        tableList = self.copyTableData()
        self.tableModel.setParams(
            currentTableType, coordType, self.getMagneticInclination(), self.getBindingPointXY())
        cvt = CoordinateFormatConverter(tableList, currentTableType, coordType)
        if coordType == 0:
            convertedTableList = cvt.convertToDD()
        elif coordType == 1:
            convertedTableList = cvt.convertToDMS()
        self.populateTable(convertedTableList)
        self.tableModel.setRerender(True)

    def populateTable(self, tableList):
        self.deleteRows()
        if self.tableModel.tabletype == 0:
            self.populateCoordTable(tableList)
        elif self.tableModel.tabletype == 1:
            print(tableList)
            self.populateAzimuthTable(tableList)
        elif self.tableModel.tabletype == 2:
            self.populateRumbTable(tableList)
        elif self.tableModel.tabletype == 3:
            self.populateAzimuthTable(tableList)
        elif self.tableModel.tabletype == 4:
            self.populateAzimuthTable(tableList)

    def populateCoordTable(self, tableList):

        def populateDDRows():
            row = 0
            for item in tableList:
                self.addRow()
                for col in range(0, self.tableModel.columnCount()):
                    if col < 3:
                        cell = QTableWidgetItem()
                        self.tableModel.setItem(row, col, cell)
                        self.tableModel.item(row, col).setText(item[col])
                    elif col == 4:
                        lineWidget = self.tableModel.cellWidget(row, col)
                        index = lineWidget.findText(item[3])
                        lineWidget.setCurrentIndex(index)
                row += 1

        def populateDMSRows():
            row = 0
            for item in tableList:
                self.addRow()
                for col in range(0, self.tableModel.columnCount()):
                    if col < 7:
                        cell = QTableWidgetItem()
                        self.tableModel.setItem(row, col, cell)
                        self.tableModel.item(row, col).setText(item[col])
                    elif col == 7:
                        lineWidget = self.tableModel.cellWidget(row, col)
                        index = lineWidget.findText(item[7])
                        lineWidget.setCurrentIndex(index)
                row += 1

        if self.tableModel.coordType == 0:
            populateDDRows()
        elif self.tableModel.coordType == 1:
            populateDMSRows()

    def populateAzimuthTable(self, tableList):
        def populateDDRows():
            row = 0
            for item in tableList:
                self.addRow()
                for col in range(0, self.tableModel.columnCount()):
                    if col < 3:
                        cell = QTableWidgetItem()
                        self.tableModel.setItem(row, col, cell)
                        self.tableModel.item(row, col).setText(item[col])
                    elif col == 3:
                        lineWidget = self.tableModel.cellWidget(row, col)
                        index = lineWidget.findText(item[3])
                        lineWidget.setCurrentIndex(index)
                row += 1

        def populateDMSRows():
            row = 0
            for item in tableList:
                self.addRow()
                for col in range(0, self.tableModel.columnCount()):
                    if col < 5:
                        cell = QTableWidgetItem()
                        self.tableModel.setItem(row, col, cell)
                        self.tableModel.item(row, col).setText(item[col])
                    elif col == 5:
                        lineWidget = self.tableModel.cellWidget(row, col)
                        index = lineWidget.findText(item[5])
                        lineWidget.setCurrentIndex(index)
                row += 1

        if self.tableModel.coordType == 0:
            populateDDRows()
        elif self.tableModel.coordType == 1:
            populateDMSRows()

    def populateRumbTable(self, tableList):
        # print(tableList)
        def populateDDRows():
            row = 0
            for item in tableList:
                self.addRow()
                for col in range(0, self.tableModel.columnCount()):
                    if col < 3:
                        cell = QTableWidgetItem()
                        self.tableModel.setItem(row, col, cell)
                        self.tableModel.item(row, col).setText(item[col])
                    elif col == 3:
                        lineWidget = self.tableModel.cellWidget(row, col)
                        index = lineWidget.findText(item[3])
                        lineWidget.setCurrentIndex(index)
                    elif col == 4:
                        lineWidget = self.tableModel.cellWidget(row, col)
                        index = lineWidget.findText(item[4])
                        lineWidget.setCurrentIndex(index)
                row += 1

        def populateDMSRows():
            row = 0
            for item in tableList:
                self.addRow()
                for col in range(0, self.tableModel.columnCount()):
                    if col < 5:
                        cell = QTableWidgetItem()
                        self.tableModel.setItem(row, col, cell)
                        self.tableModel.item(row, col).setText(item[col])
                    elif col == 5:
                        lineWidget = self.tableModel.cellWidget(row, col)
                        index = lineWidget.findText(item[5])
                        lineWidget.setCurrentIndex(index)
                    elif col == 6:
                        lineWidget = self.tableModel.cellWidget(row, col)
                        index = lineWidget.findText(item[6])
                        lineWidget.setCurrentIndex(index)
                row += 1

        if self.tableModel.coordType == 0:
            populateDDRows()
        elif self.tableModel.coordType == 1:
            populateDMSRows()

    def convertCells(self, currentTableType, newTableType, tableType, coordType, magneticInclination, bindingPoint):
        self.tableModel.setRerender(False)
        tableList = self.copyTableData()
        pointsDict = self.tableModel.getPoints().copy()
        self.deleteRows()
        self.tableModel.setParams(
            tableType, coordType, magneticInclination, bindingPoint)
        if coordType == 1:
            cvt = CoordinateConverter(tableList, currentTableType, coordType)
            convertedValues = None
            # if newTableType == 3 or currentTableType == 3:
            #     convertedValues = []
            if currentTableType == 1 and newTableType == 2:
                convertedValues = cvt.convertDMSAz2Rumb()
            elif currentTableType == 2 and newTableType == 1:
                convertedValues = cvt.convertDMSRumb2Az()
            elif currentTableType == 0 and newTableType == 1:
                convertedValues = cvt.convertDMSCoord2Az(
                    self.getBindingPointXY(), pointsDict)
            elif currentTableType == 0 and newTableType == 2:
                convertedValues = cvt.convertDMSCoord2Rumb(
                    self.getBindingPointXY(), pointsDict)
            elif currentTableType == 1 and newTableType == 0:
                convertedValues = cvt.convert2DMSCoords(pointsDict)
            elif currentTableType == 2 and newTableType == 0:
                convertedValues = cvt.convert2DMSCoords(pointsDict)
            elif currentTableType == 3 and newTableType == 0:
                convertedValues = cvt.convert2DMSCoords(pointsDict)
            elif currentTableType == 4 and newTableType == 0:
                convertedValues = cvt.convert2DMSCoords(pointsDict)         
            elif currentTableType == 3 and newTableType == 1:
                convertedValues = cvt.convertDMSCoord2Az(
                    self.getBindingPointXY(), pointsDict)
            elif currentTableType == 4 and newTableType == 1:
                convertedValues = cvt.convertDMSCoord2Az(
                    self.getBindingPointXY(), pointsDict)
            elif currentTableType == 3 and newTableType == 2:
                convertedValues = cvt.convertDMSCoord2Rumb(
                    self.getBindingPointXY(), pointsDict)
            elif currentTableType == 4 and newTableType == 2:
                convertedValues = cvt.convertDMSCoord2Rumb(
                    self.getBindingPointXY(), pointsDict)

            elif currentTableType == 0 and newTableType == 3 or \
                currentTableType == 0 and newTableType == 4:
                convertedValues = cvt.convertCoord2Angle(self.getBindingPointXY(), pointsDict, newTableType, coordType)
            elif currentTableType == 1 and newTableType == 3 or \
                currentTableType == 1 and newTableType == 4:
                convertedValues = cvt.convertAzimuth2Angle(pointsDict, newTableType, coordType)
            elif currentTableType == 2 and newTableType == 3 or \
                currentTableType == 2 and newTableType == 4:
                convertedValues = cvt.convertRumb2Angle(pointsDict, newTableType, coordType)
            elif currentTableType == 3 and newTableType == 4:
                convertedValues = cvt.convertAngle2Angle(pointsDict, coordType)
            elif currentTableType == 4 and newTableType == 3:
                convertedValues = cvt.convertAngle2Angle(pointsDict, coordType)
            if convertedValues:
                self.populateTable(convertedValues)
        elif coordType == 0:
            if currentTableType == type:
                pass
            # elif currentTableType == 3:
            #     pass
            else:
                cvt = CoordinateConverter(tableList, currentTableType, coordType)
                convertedValues = None
                if currentTableType == 1 and newTableType == 2:
                    convertedValues = cvt.convertDDAzimuth2Rumb()
                elif currentTableType == 2 and newTableType == 1:
                    convertedValues = cvt.convertDDRumb2Azimuth()
                elif currentTableType == 0 and newTableType == 1:
                    convertedValues = cvt.convertDDCoord2Azimuth(
                        self.getBindingPointXY(), pointsDict)
                elif currentTableType == 0 and newTableType == 2:
                    convertedValues = cvt.convertDDCoord2Rumb(
                        self.getBindingPointXY(), pointsDict)
                elif currentTableType == 1 and newTableType == 0:
                    convertedValues = cvt.convert2DDCoords(pointsDict)
                elif currentTableType == 2 and newTableType == 0:
                    convertedValues = cvt.convert2DDCoords(pointsDict)
                elif currentTableType == 3 and newTableType == 0:
                    convertedValues = cvt.convert2DDCoords(pointsDict)
                elif currentTableType == 4 and newTableType == 0:
                    convertedValues = cvt.convert2DDCoords(pointsDict)
                elif currentTableType == 3 and newTableType == 1:
                    convertedValues = cvt.convertDDCoord2Azimuth(
                        self.getBindingPointXY(), pointsDict)
                elif currentTableType == 4 and newTableType == 1:
                    convertedValues = cvt.convertDDCoord2Azimuth(
                        self.getBindingPointXY(), pointsDict)
                elif currentTableType == 3 and newTableType == 2:
                    convertedValues = cvt.convertDDCoord2Rumb(
                        self.getBindingPointXY(), pointsDict)
                elif currentTableType == 4 and newTableType == 2:
                    convertedValues = cvt.convertDDCoord2Rumb(
                        self.getBindingPointXY(), pointsDict)                                                

                elif currentTableType == 0 and newTableType == 3 or \
                    currentTableType == 0 and newTableType == 4:
                    convertedValues = cvt.convertCoord2Angle(self.getBindingPointXY(), pointsDict, newTableType, coordType)
                elif currentTableType == 1 and newTableType == 3 or \
                    currentTableType == 1 and newTableType == 4:
                    convertedValues = cvt.convertAzimuth2Angle(pointsDict, newTableType, coordType)
                elif currentTableType == 2 and newTableType == 3 or \
                    currentTableType == 2 and newTableType == 4:
                    convertedValues = cvt.convertRumb2Angle(pointsDict, newTableType, coordType)
                elif currentTableType == 3 and newTableType == 4:
                    convertedValues = cvt.convertAngle2Angle(pointsDict, coordType)
                elif currentTableType == 4 and newTableType == 3:
                    convertedValues = cvt.convertAngle2Angle(pointsDict, coordType)
                if convertedValues:
                    self.populateTable(convertedValues)
        self.tableModel.setRerender(True)

    def copyTableData(self):
        return self.tableModel.getTableAsList()

    def sortDictionary(self, oldDict):
        length = len(oldDict)
        dictionary = {}
        for x in range(0, length):
            dictionary[x] = oldDict[x]
        return dictionary

    def getParams(self):
        return self.tableModel.getParams()

    def appendTableFromMap(self, tableList):
        for ptTuple in tableList:
            self.addRow()
            row = self.getRowsCount()-1
            point = GeoOperations.convertToWgs(ptTuple[0])
            cellX = QTableWidgetItem()
            cellX.setText(str(point.x()))
            self.tableModel.setItem(row, 2, cellX)

            cellY = QTableWidgetItem()
            cellY.setText(str(point.y()))
            self.tableModel.setItem(row, 1, cellY)

            lineWidget = self.tableModel.cellWidget(row, 4)
            index = lineWidget.findText(ptTuple[1])
            lineWidget.setCurrentIndex(index)
