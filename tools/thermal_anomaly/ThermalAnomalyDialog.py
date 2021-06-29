# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ThermalAnomalyDialog
                                 A QGIS plugin
 This plugin shows thermal anomalies
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-04-15
        git sha              : $Format:%H$
        copyright            : (C) 2020 by GIS
        email                : gis@gis.by
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from enum import Enum

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt, QDateTime, QTime
from PyQt5.QtGui import QIcon
from qgis._gui import QgsMapToolPan

from qgis.core import QgsFeature, QgsFeatureRequest, QgsProject, QgsGeometry, \
    QgsCoordinateTransform, QgsCoordinateTransformContext, \
    QgsVectorLayer, QgsLayerTreeGroup, QgsRenderContext, \
    QgsCoordinateReferenceSystem, QgsSimpleMarkerSymbolLayerBase, QgsSymbol, QgsSvgMarkerSymbolLayer
from PyQt5.QtWidgets import QMessageBox, QApplication
from qgis.PyQt.QtGui import QIcon, QColor
from .DataRequest import DataRequest

from ...util import resolvePath

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ThermalAnomalyDialogBase.ui'))


class StatusMessageType(Enum):
    EMPTY = 0
    AUTH_STARTED = 1
    AUTH_FINISHED = 2
    AUTH_FAILED = 3
    LOAD_STARTED = 4
    LOAD_FINISHED = 5
    POLYGON_ON = 6


class ThermalAnomalyDialog(QtWidgets.QDialog, FORM_CLASS):
    groupName = "ThermalAnomaly"
    resultsLayerName = "results"
    searchAreaLayerName = "search_area"

    status_message = [
        "",
        "Авторизация...",
        "Авторизация завершена",
        "Ошибка авторизации",
        "Загрузка данных...",
        "Загузка данных завершена",
        "Щелчок правой клавишей мыши завершает ввод"
    ]
    _validPeriodText = "*данные пользователя действительны до 31 декабря 2020г."

    _clientId = "plugin_for_qgis"
    _clientSecret = "5a963ce5-580a-3992-a905-8388c406d113"

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(ThermalAnomalyDialog, self).__init__(parent)

        self.setupUi(self)

        self.iface = iface

        self.color = QColor(60, 151, 255, 125)

        self.getDataButton.clicked.connect(self.getDataButtonClicked)

        self.lastStatusMessage = StatusMessageType.EMPTY

        self.dataRequest = DataRequest()
        self.dataRequest.authorizationStarted.connect(self.authStarted)
        self.dataRequest.requestFinished.connect(self.showRequestResult)
        self.dataRequest.authorizationFinished.connect(self.authFinished)

        self.init_dialog()

    def init_dialog(self):
        date_time = QDateTime.currentDateTime()
        date = date_time.date()
        time = date_time.time()
        min_date_time = QDateTime(date, QTime(0, 0)).addYears(-1).toUTC()
        max_date_time = QDateTime(date, QTime(23, 59)).toUTC()

        self.dateTimeEditFrom.setDateTime(QDateTime(date, QTime(0, 0)).toUTC())
        self.dateTimeEditFrom.setDateTimeRange(min_date_time, max_date_time)
        self.dateTimeEditTo.setDateTime(QDateTime(date, time).toUTC())
        self.dateTimeEditTo.setDateTimeRange(min_date_time, max_date_time)

        if self.dataRequest is not None and self.dataRequest.isAuthorized():
            self.__show_status_label(StatusMessageType.AUTH_FINISHED)
        else:
            self.__show_status_label(self.lastStatusMessage)

    def authStarted(self):
        self.getDataButton.setEnabled(False)
        self.__show_status_label(StatusMessageType.AUTH_STARTED)

    def authFinished(self, successful):
        if successful:
            self.getDataButton.setEnabled(True)
            self.__show_status_label(StatusMessageType.AUTH_FINISHED)
        else:
            self.__show_status_label(StatusMessageType.AUTH_FAILED)

    def geomTransform(self, geom, crs_orig, crs_dest):
        g = QgsGeometry(geom)
        crsTransform = QgsCoordinateTransform(
            crs_orig, crs_dest, QgsCoordinateTransformContext())  # which context ?
        g.transform(crsTransform)
        return g

    def _show_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)

        msg.setWindowTitle(title)
        msg.setText(message)

        msg.addButton('Ок', QMessageBox.AcceptRole)
        msg.exec()

    def getDataButtonClicked(self):
        clId = self._clientId
        clSecret = self._clientSecret

        dateTimeFrom = self.dateTimeEditFrom.dateTime()
        dateTimeTo = self.dateTimeEditTo.dateTime()
        if dateTimeFrom >= dateTimeTo:
            self._show_message("Некорректные данные", "Дата 'По' должна быть больше, чем дата 'С'")
            return

        pjt = QgsProject.instance()
        # clear results
        layersList = pjt.mapLayersByName(self.resultsLayerName)
        if layersList is not None and len(layersList) > 0:
            pjt.removeMapLayer(layersList[0])
            self.iface.mapCanvas().refresh()

        extent = self.iface.mapCanvas().extent()
        polygonGeometry = self.geomTransform(
            QgsGeometry().fromRect(extent), 
            self.iface.mapCanvas().mapSettings().destinationCrs(),
            QgsCoordinateReferenceSystem(4326))

        availableAreaName = "available_area"
        shpLayer = QgsVectorLayer(os.path.dirname(__file__) + "/roi/ZRV.shp", availableAreaName, "ogr")
        if not shpLayer.isValid():
            self._show_message("Некорректные данные", "Некорректный файл с зоной охвата")
            return
        intersectionGeom = None
        for feature in shpLayer.getFeatures():
            if feature.geometry().intersects(polygonGeometry):
                intersectionGeom = feature.geometry().intersection(polygonGeometry)

        if intersectionGeom == None:
            layersList = pjt.mapLayersByName(availableAreaName)
            if layersList is not None and len(layersList) > 0:
                pjt.removeMapLayer(layersList[0])

            symbols = shpLayer.renderer().symbols(QgsRenderContext())
            symbols[0].setColor(QColor(76, 205, 53, 84))
            pjt.addMapLayer(shpLayer, False)
            if pjt.layerTreeRoot().findGroup(self.tr(self.groupName)) is None:
                pjt.layerTreeRoot().insertChildNode(0, QgsLayerTreeGroup(self.tr(self.groupName)))
            group = pjt.layerTreeRoot().findGroup(self.tr(self.groupName))
            group.addLayer(shpLayer)
            self.iface.layerTreeView().refreshLayerSymbology(shpLayer.id())
            geom = self.geomTransform(
                list(shpLayer.getFeatures())[0].geometry(),
                QgsCoordinateReferenceSystem(4326),
                self.iface.mapCanvas().mapSettings().destinationCrs())
            self.iface.mapCanvas().setExtent(geom.boundingBox())
            self.iface.mapCanvas().refresh()

            self._show_message("Некорректные данные", "Полигон поиска лежит за пределами зоны охвата")
            return

        self.polygon = intersectionGeom.asWkt()

        self.getDataButton.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.__show_status_label(StatusMessageType.LOAD_STARTED)
        self.dataRequest.dataRequest(clId, clSecret, dateTimeFrom, dateTimeTo, self.polygon)

    def showRequestResult(self, items, append, last, message):
        if items is None or len(items) == 0:
            QApplication.restoreOverrideCursor()
            self.__show_status_label(StatusMessageType.LOAD_FINISHED)
            self.getDataButton.setEnabled(True)

            if message is None or len(message) == 0:
                message = "По указанным параметрам ничего не найдено"

            self._show_message("Загузка завершена", message)
            return

        color = QColor(237, 28, 36, 200)
        pjt = QgsProject.instance()
        layersList = pjt.mapLayersByName(self.resultsLayerName)

        if not append:
            if layersList is not None and len(layersList) > 0:
                pjt.removeMapLayer(layersList[0])
            layersList.clear()
        if not append or layersList is None or len(layersList) == 0:
            layer = QgsVectorLayer("Point?crs=EPSG:4326"
                                   "&field=coordinatesWKT:string(255)&field=shootingDateTime:string(255)"
                                   "&field=temperature:double(7)&field=pixelSizeInDirection:double(5)"
                                   "&field=pixelSizeAcross:double(5)&field=thermalPower:double(5)"
                                   "&field=baseResourceId:string(255)&field=id:string(255)&field=updated:string(255)"
                                   "&field=satellite:string(10)",
                                   self.resultsLayerName, "memory")
        else:
            layer = layersList[0]

        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        svg_marker = QgsSvgMarkerSymbolLayer(resolvePath("tools\\thermal_anomaly\\point.svg"))
        svg_marker.setSize(6.0)
        symbol.changeSymbolLayer(0, svg_marker)
        layer.renderer().setSymbol(symbol)

        layer.startEditing()
        poly = QgsGeometry.fromWkt(self.polygon)

        for point in items:
            symbols = layer.renderer().symbols(QgsRenderContext())  # todo which context ?
            symbols[0].setColor(color)
            feature = QgsFeature()
            coord = QgsGeometry.fromWkt(point["coordinatesWKT"])
            feature.setGeometry(coord)
            feature.setAttributes([point["coordinatesWKT"], point["shootingDateTime"], point["temperature"],
                                   point["pixelSizeInDirection"], point["pixelSizeAcross"], point["thermalPower"],
                                   point["baseResourceId"], point["id"], point["updated"], point["satellite"]])
            layer.dataProvider().addFeatures([feature])

        layer.commitChanges()

        if not append:
            pjt.addMapLayer(layer, False)
            if pjt.layerTreeRoot().findGroup(self.tr(self.groupName)) is None:
                pjt.layerTreeRoot().insertChildNode(0, QgsLayerTreeGroup(self.tr(self.groupName)))
            group = pjt.layerTreeRoot().findGroup(self.tr(self.groupName))
            group.insertLayer(0, layer)
        self.iface.layerTreeView().refreshLayerSymbology(layer.id())
        self.iface.mapCanvas().refresh()
        if last:
            QApplication.restoreOverrideCursor()
            self.__show_status_label(StatusMessageType.LOAD_FINISHED)
            self.getDataButton.setEnabled(True)
        else:
            self.__show_status_label(StatusMessageType.LOAD_STARTED, message)

    def __show_status_label(self, status_type, msg=None):
        self.lastStatusMessage = status_type
        if msg is None:
            self.statusLabel.setText(self.status_message[self.lastStatusMessage.value])
        else:
            self.statusLabel.setText(self.status_message[self.lastStatusMessage.value] + " " + msg)
